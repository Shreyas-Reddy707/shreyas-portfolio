import hashlib
import json
import uuid

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
    if existing_delivery is not None:
        return {"status": "duplicate_ignored", "delivery_id": delivery_id}

    repo_full_name = None
    repo_obj = None
    try:
        parsed = json.loads(raw_body.decode("utf-8"))
        repo = parsed.get("repository")
        if isinstance(repo, dict):
            repo_full_name = repo.get("full_name")
            if repo.get("name"):
                repo_obj = repo
    except Exception:
        repo_full_name = None

    db.add(
        WebhookDelivery(
            delivery_id=delivery_id[:64],
            event_type=event_type[:64],
            repository_full_name=repo_full_name[:200] if repo_full_name else None,
            signature_verified=True,
            payload_sha256=payload_hash,
            status="processed",
        )
    )
    await db.commit()

    if event_type in {"push", "repository", "release"} and repo_obj is not None:
        await sync_github_repositories(db, repo_payloads=[repo_obj])
    else:
        await invalidate_portfolio_cache()

    return {"status": "accepted", "delivery_id": delivery_id}
