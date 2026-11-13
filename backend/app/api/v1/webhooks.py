import hashlib
import json
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_guard import (
    acquire_webhook_delivery_lock,
    check_rate_limit,
    invalidate_portfolio_cache,
)
from app.core.security import hash_client_ip, verify_github_webhook_signature
from app.models.portfolio import WebhookDelivery
from app.services.github_sync import sync_github_repositories

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhooks/github")
async def receive_github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Verify HMAC-SHA256 signature, enforce idempotency, and sync repository metadata."""
    ip_hash = hash_client_ip(request)
    await check_rate_limit("github_webhook", ip_hash, limit=30, window_seconds=60)

    delivery_id = request.headers.get("X-GitHub-Delivery") or str(uuid.uuid4())
    event_type = request.headers.get("X-GitHub-Event", "unknown")

    try:
        raw_body = await verify_github_webhook_signature(request)
    except HTTPException as exc:
        body_bytes = await request.body()
        payload_hash = hashlib.sha256(body_bytes).hexdigest()
        existing = (
            await db.execute(
                select(WebhookDelivery).where(WebhookDelivery.delivery_id == delivery_id)
            )
        ).scalar_one_or_none()
        if existing is None:
            db.add(
                WebhookDelivery(
                    delivery_id=delivery_id[:64],
                    event_type=event_type[:64],
                    repository_full_name=None,
                    signature_verified=False,
                    payload_sha256=payload_hash,
                    status="rejected_hmac",
                    error_detail=str(exc.detail)[:500],
                )
            )
            await db.commit()
        raise

    payload_hash = hashlib.sha256(raw_body).hexdigest()

    acquired = await acquire_webhook_delivery_lock(delivery_id)
    if not acquired:
        return {"status": "duplicate_ignored", "delivery_id": delivery_id}

    existing_delivery = (
        await db.execute(
            select(WebhookDelivery).where(WebhookDelivery.delivery_id == delivery_id)
        )
    ).scalar_one_or_none()
    if existing_delivery is not None and existing_delivery.status in {"processed", "ignored"}:
        return {"status": "duplicate_ignored", "delivery_id": delivery_id}

    repo_full_name = None
    repo_obj = None
    touches_manifest = False
    try:
        parsed = json.loads(raw_body.decode("utf-8"))
        repo = parsed.get("repository")
        if isinstance(repo, dict):
            repo_full_name = repo.get("full_name")
            if repo.get("name"):
                repo_obj = repo
        commits = parsed.get("commits")
        if isinstance(commits, list):
            for c in commits:
                all_files = (c.get("added") or []) + (c.get("modified") or []) + (c.get("removed") or [])
                if any("portfolio_data.json" in str(f) for f in all_files):
                    touches_manifest = True
                    break
    except Exception:
        repo_full_name = None

    is_portfolio_repo = bool(
        repo_full_name and "shreyas-portfolio" in repo_full_name.lower()
    )

    if existing_delivery is not None:
        delivery_record = existing_delivery
        delivery_record.event_type = event_type[:64]
        delivery_record.repository_full_name = repo_full_name[:200] if repo_full_name else None
        delivery_record.signature_verified = True
        delivery_record.payload_sha256 = payload_hash
        delivery_record.status = "failed"
    else:
        delivery_record = WebhookDelivery(
            delivery_id=delivery_id[:64],
            event_type=event_type[:64],
            repository_full_name=repo_full_name[:200] if repo_full_name else None,
            signature_verified=True,
            payload_sha256=payload_hash,
            status="failed",
        )
        db.add(delivery_record)
    await db.commit()

    try:
        if event_type in {"push", "repository", "release"} and repo_obj is not None:
            await sync_github_repositories(db, repo_payloads=[repo_obj])

        if touches_manifest or is_portfolio_repo:
            manifest_path = Path(__file__).resolve().parents[4] / "content" / "portfolio_data.json"
            if manifest_path.exists():
                try:
                    from scripts.sync_portfolio_content import sync_database_from_manifest

                    await sync_database_from_manifest(manifest_path)
                except Exception as m_err:
                    logger.warning("Manifest sync error during webhook processing: %s", m_err)

        await invalidate_portfolio_cache()

        delivery_record.status = "processed"
        delivery_record.error_detail = None
        await db.commit()
    except Exception as exc:
        try:
            await db.rollback()
        except Exception as rb_err:
            logger.debug("Database rollback error: %s", rb_err)

        try:
            rec = (
                await db.execute(
                    select(WebhookDelivery).where(WebhookDelivery.delivery_id == delivery_id[:64])
                )
            ).scalar_one_or_none()
            if rec:
                rec.status = "failed"
                rec.error_detail = str(exc)[:500]
                await db.commit()
        except Exception as rec_err:
            logger.warning("Failed to record webhook delivery failure: %s", rec_err)
        finally:
            try:
                from app.core.redis_guard import get_redis

                client = await get_redis()
                await client.delete(f"webhook:lock:{delivery_id}")
            except Exception as redis_err:
                logger.debug("Failed to release webhook delivery lock: %s", redis_err)
        raise exc

    return {"status": "accepted", "delivery_id": delivery_id}
