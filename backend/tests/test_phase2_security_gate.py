import hashlib
import hmac
import json
import uuid

import pytest
from app.core.config import settings
from app.core.redis_guard import get_redis
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def clean_redis_rate_limits():
    """Clear rate-limit and webhook test keys before/after test runs."""
    client = await get_redis()
    keys = await client.keys("rl:*")
    if keys:
        await client.delete(*keys)
    yield
    keys = await client.keys("rl:*")
    if keys:
        await client.delete(*keys)


@pytest.mark.asyncio
async def test_01_health_and_public_portfolio_no_cleartext_pii(clean_redis_rate_limits):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        health_res = await ac.get("/api/v1/health")
        assert health_res.status_code == 200
        health_body = health_res.json()
        assert health_body["status"] == "ok"
        assert health_body["postgres_connected"] is True
        assert health_body["redis_connected"] is True
        assert health_body["pgvector_enabled"] is True

        port_res = await ac.get("/api/v1/public/portfolio")
        assert port_res.status_code == 200
        assert port_res.headers.get("X-Content-Type-Options") == "nosniff"
        assert port_res.headers.get("X-Frame-Options") == "DENY"

        port_body = port_res.json()
        assert port_body["profile"]["full_name"] == "Shreyas Reddy"
        assert len(port_body["flagship_projects"]) == 5
        assert len(port_body["auto_synced_repos"]) >= 1

        raw_json = json.dumps(port_body)
        assert "email_cleartext" not in raw_json
        assert "phone_cleartext" not in raw_json
        assert "shreyas.chemakoora@gmail.com" not in raw_json
        assert "+91 9346759117" not in raw_json


@pytest.mark.asyncio
async def test_02_forged_github_webhook_rejected_401(clean_redis_rate_limits):
    transport = ASGITransport(app=app)
    payload = {"zen": "hack", "repository": {"full_name": "shreyas-reddy/SecureRAG"}}
    delivery_id = str(uuid.uuid4())
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/webhooks/github",
            json=payload,
            headers={
                "X-GitHub-Event": "push",
                "X-GitHub-Delivery": delivery_id,
                "X-Hub-Signature-256": "sha256=" + ("0" * 64),
            },
        )
    assert res.status_code == 401
    assert res.json()["error_code"] == "INVALID_HMAC_SIGNATURE"


@pytest.mark.asyncio
async def test_03_valid_hmac_webhook_and_replay_idempotency(clean_redis_rate_limits):
    transport = ASGITransport(app=app)
    raw_body = json.dumps(
        {"ref": "refs/heads/main", "repository": {"full_name": "shreyas-reddy/SecureRAG"}}
    ).encode("utf-8")
    sig = "sha256=" + hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    delivery_id = str(uuid.uuid4())
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "push",
        "X-GitHub-Delivery": delivery_id,
        "X-Hub-Signature-256": sig,
    }

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        first = await ac.post("/api/v1/webhooks/github", content=raw_body, headers=headers)
        assert first.status_code == 200
        assert first.json()["status"] == "accepted"

        replay = await ac.post("/api/v1/webhooks/github", content=raw_body, headers=headers)
        assert replay.status_code == 200
        assert replay.json()["status"] == "duplicate_ignored"


@pytest.mark.asyncio
async def test_04_bopla_mass_assignment_blocked_422(clean_redis_rate_limits):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/agent/chat",
            json={
                "query": "Tell me about SecureRAG",
                "turnstile_token": "0.cloudflare_turnstile_response_token_string",
                "is_admin": True,
                "role": "superuser",
            },
        )
    assert res.status_code == 422
    assert res.json()["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_05_contact_reveal_invalid_turnstile_rejected_403(clean_redis_rate_limits):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/public/contact-reveal",
            json={"turnstile_token": "invalid_bot_token"},
        )
    assert res.status_code == 403
    assert res.json()["error_code"] == "TURNSTILE_VERIFICATION_FAILED"
    raw = res.text
    assert "shreyas.chemakoora@gmail.com" not in raw
    assert "+91 9346759117" not in raw


@pytest.mark.asyncio
async def test_06_agent_rate_limit_trip_429(clean_redis_rate_limits):
    transport = ASGITransport(app=app)
    payload = {
        "query": "What experience does Shreyas have at Viswam.ai?",
        "turnstile_token": "0.cloudflare_turnstile_response_token_string",
    }
    headers = {"CF-Connecting-IP": "203.0.113.42"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        for i in range(5):
            ok_res = await ac.post("/api/v1/agent/chat", json=payload, headers=headers)
            assert ok_res.status_code == 200, f"Request {i + 1} failed unexpectedly: {ok_res.text}"

        tripped = await ac.post("/api/v1/agent/chat", json=payload, headers=headers)
        assert tripped.status_code == 429
        body = tripped.json()
        assert body["error_code"] == "RATE_LIMIT_EXCEEDED"
        assert body["retry_after_seconds"] > 0
        assert tripped.headers.get("X-Content-Type-Options") == "nosniff"


@pytest.mark.asyncio
async def test_07_oversized_payload_rejected_413(clean_redis_rate_limits):
    transport = ASGITransport(app=app)
    oversized_query = "A" * 5000
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/agent/chat",
            json={
                "query": oversized_query,
                "turnstile_token": "0.cloudflare_turnstile_response_token_string",
            },
        )
    assert res.status_code == 413
    assert res.json()["error_code"] == "PAYLOAD_TOO_LARGE"


@pytest.mark.asyncio
async def test_08_contact_submission_and_resend_dispatch(clean_redis_rate_limits):
    transport = ASGITransport(app=app)
    contact_payload = {
        "sender_name": "Sarah Connor",
        "sender_email": "sarah.connor@cyberdyne-ai.com",
        "sender_company": "Cyberdyne AI Systems",
        "role_opportunity": "Principal AI Systems Architect",
        "message": "Hi Shreyas, we reviewed your SecureRAG and DataMind systems and would love to discuss a leadership role.",
        "turnstile_token": "0.cloudflare_turnstile_response_token_string",
    }
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/contact", json=contact_payload)

    assert res.status_code == 201
    body = res.json()
    assert body["status"] in ("received", "notified")
    assert "submission_id" in body
    assert isinstance(body["email_dispatched"], bool)
    assert body["contact"]["email"] == "shreyas.chemakoora@gmail.com"


