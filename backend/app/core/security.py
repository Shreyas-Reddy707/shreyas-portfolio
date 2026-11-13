import asyncio
import hashlib
import hmac
import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, Request, status

from app.core.config import settings

ALLOWED_OUTBOUND_HOSTS = {
    "api.github.com",
    "raw.githubusercontent.com",
    "challenges.cloudflare.com",
    "generativelanguage.googleapis.com",
    "api.groq.com",
    "api.resend.com",
}

_LOCAL_DEV_TEST_SECRET = "1x0000000000000000000000000000000AA"  # noqa: S105
_DEV_DUMMY_TOKENS = {
    "0.cloudflare_turnstile_response_token_string",
    "test_valid_turnstile_token",
    "local-dev-turnstile-token",
}


def extract_client_ip(request: Request) -> str:
    """Extract normalized client IP with proxy validation."""
    client_host = request.client.host if request.client and request.client.host else "127.0.0.1"
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        candidate = cf_ip.strip()
        try:
            ipaddress.ip_address(candidate)
            # Only trust CF-Connecting-IP if incoming direct connection is from a trusted proxy (loopback or private CIDR)
            peer_ip = ipaddress.ip_address(client_host)
            if peer_ip.is_loopback or peer_ip.is_private:
                return candidate
        except ValueError:
            pass
    return client_host


def hash_client_ip(request: Request) -> str:
    """Compute keyed HMAC-SHA256 hash of client IP for PII-safe rate limiting."""
    client_ip = extract_client_ip(request)
    return hmac.new(
        settings.IP_HASH_PEPPER.encode("utf-8"),
        client_ip.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


async def verify_github_webhook_signature(request: Request) -> bytes:
    """Verify X-Hub-Signature-256 against raw request bytes before JSON parsing."""
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "MISSING_HMAC_SIGNATURE",
                "message": "Missing X-Hub-Signature-256 header.",
            },
        )

    raw_body = await request.body()
    expected_mac = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    expected_header = f"sha256={expected_mac}"

    if not hmac.compare_digest(expected_header, signature_header):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_HMAC_SIGNATURE",
                "message": "Webhook HMAC signature mismatch.",
            },
        )
    return raw_body


async def validate_outbound_url_async(url: str) -> str:
    """Validate outbound URL against strict HTTPS, host allowlist, and SSRF IP rules asynchronously."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    if (
        settings.APP_ENV == "development"
        and settings.AI_PROVIDER == "ollama"
        and parsed.scheme == "http"
        and host == "localhost"
        and parsed.port == 11434
    ):
        return url

    if parsed.scheme != "https":
        raise ValueError(f"Outbound URL must use https:// scheme: {url}")

    if host not in ALLOWED_OUTBOUND_HOSTS:
        raise ValueError(f"Outbound host '{host}' is not in ALLOWED_OUTBOUND_HOSTS.")

    loop = asyncio.get_running_loop()
    try:
        addr_info = await asyncio.wait_for(
            loop.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM),
            timeout=3.0,
        )
    except (socket.gaierror, TimeoutError) as exc:
        raise ValueError(f"DNS resolution failed or timed out for '{host}'.") from exc

    for entry in addr_info:
        ip_str = entry[4][0]
        ip_obj = ipaddress.ip_address(ip_str)
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
        ):
            raise ValueError(f"Blocked SSRF target IP '{ip_str}' for host '{host}'.")

    return url


def validate_outbound_url(url: str) -> str:
    """Validate outbound URL against strict HTTPS, host allowlist, and SSRF IP rules."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    if (
        settings.APP_ENV == "development"
        and settings.AI_PROVIDER == "ollama"
        and parsed.scheme == "http"
        and host == "localhost"
        and parsed.port == 11434
    ):
        return url

    if parsed.scheme != "https":
        raise ValueError(f"Outbound URL must use https:// scheme: {url}")

    if host not in ALLOWED_OUTBOUND_HOSTS:
        raise ValueError(f"Outbound host '{host}' is not in ALLOWED_OUTBOUND_HOSTS.")

    try:
        addr_info = socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed for '{host}'.") from exc

    for entry in addr_info:
        ip_str = entry[4][0]
        ip_obj = ipaddress.ip_address(ip_str)
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
        ):
            raise ValueError(f"Blocked SSRF target IP '{ip_str}' for host '{host}'.")

    return url


async def verify_turnstile_token(token: str, remote_ip: str | None = None) -> bool:
    """Verify Cloudflare Turnstile token, supporting local dummy keys & live siteverify."""
    cleaned = (token or "").strip()
    if not cleaned or cleaned == "invalid_bot_token" or cleaned.startswith("FAIL_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "TURNSTILE_VERIFICATION_FAILED",
                "message": "Bot verification failed. Please retry.",
            },
        )

    # In development or testing, accept standard dummy test tokens or local dummy secret
    if settings.APP_ENV == "development":
        if cleaned in _DEV_DUMMY_TOKENS:
            return True
        if settings.TURNSTILE_SECRET_KEY == _LOCAL_DEV_TEST_SECRET and len(cleaned) >= 10:
            return True

    verify_url = await validate_outbound_url_async("https://challenges.cloudflare.com/turnstile/v0/siteverify")
    payload = {
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": cleaned,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(follow_redirects=False, timeout=5.0) as client:
            resp = await client.post(verify_url, data=payload)
            data = resp.json()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "TURNSTILE_VERIFICATION_FAILED",
                "message": "Unable to verify Turnstile token.",
            },
        ) from exc

    if not data.get("success"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "TURNSTILE_VERIFICATION_FAILED",
                "message": "Turnstile token rejected.",
            },
        )

    return True

