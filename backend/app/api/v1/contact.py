import html
import logging
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis_guard import check_rate_limit
from app.core.security import (
    extract_client_ip,
    hash_client_ip,
    validate_outbound_url,
    verify_turnstile_token,
)
from app.models.portfolio import CandidateProfile, ContactSubmission
from app.schemas.portfolio import (
    ContactRevealResponse,
    ContactSubmissionRequest,
    ContactSubmissionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def send_recruiter_email_via_resend(
    submission: ContactSubmission,
) -> tuple[bool, str | None]:
    """Dispatch an immediate recruiter inquiry email via Resend API."""
    if not settings.RESEND_API_KEY or settings.RESEND_API_KEY.startswith("re_placeholder"):
        logger.info("Resend email dispatch skipped: RESEND_API_KEY not configured or placeholder.")
        return False, "RESEND_API_KEY not configured"

    try:
        url = validate_outbound_url("https://api.resend.com/emails")
    except ValueError as e:
        logger.warning("Resend outbound URL validation failed: %s", e)
        return False, f"SSRF check failed: {e}"

    safe_name = html.escape(submission.sender_name or "Anonymous Recruiter")
    safe_email = html.escape(submission.sender_email or "")
    safe_company = html.escape(submission.sender_company or "Direct / Independent")
    safe_role = html.escape(submission.role_opportunity or "Engineering Opportunity")
    safe_message = html.escape(submission.message or "").replace("\n", "<br>")
    submitted_at_str = (
        submission.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        if submission.created_at
        else datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    )

    subject = f"🚀 [Portfolio Inquiry] {safe_name} ({safe_company}) — {safe_role}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>{subject}</title>
    </head>
    <body style="margin: 0; padding: 24px; background-color: #050508; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #FAFAFA;">
      <div style="max-width: 600px; margin: 0 auto; background-color: #0B0F17; border: 1px solid #1E293B; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        <!-- Header Strip -->
        <div style="background: linear-gradient(90deg, #00F0FF, #8B5CF6); padding: 4px;"></div>
        <div style="padding: 24px 28px 16px; border-bottom: 1px solid #1E293B;">
          <div style="font-family: monospace; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: #00F0FF; margin-bottom: 6px;">
            PORTFOLIO RECRUITER INQUIRY
          </div>
          <h1 style="margin: 0; font-size: 20px; font-weight: 700; color: #FAFAFA;">
            New Direct Message from {safe_name}
          </h1>
          <p style="margin: 4px 0 0; font-size: 13px; color: #94A3B8;">
            Received at {submitted_at_str} via Shreyas Portfolio
          </p>
        </div>

        <!-- Details Grid -->
        <div style="padding: 20px 28px; background-color: #0E1420; border-bottom: 1px solid #1E293B;">
          <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <tr>
              <td style="padding: 6px 0; color: #94A3B8; width: 140px; font-family: monospace;">Candidate / Role:</td>
              <td style="padding: 6px 0; color: #FAFAFA; font-weight: 600;">{safe_role}</td>
            </tr>
            <tr>
              <td style="padding: 6px 0; color: #94A3B8; font-family: monospace;">Company / Org:</td>
              <td style="padding: 6px 0; color: #FAFAFA; font-weight: 600;">{safe_company}</td>
            </tr>
            <tr>
              <td style="padding: 6px 0; color: #94A3B8; font-family: monospace;">Recruiter Email:</td>
              <td style="padding: 6px 0;">
                <a href="mailto:{safe_email}" style="color: #00F0FF; text-decoration: none; font-weight: 600;">{safe_email}</a>
              </td>
            </tr>
          </table>
        </div>

        <!-- Message Body -->
        <div style="padding: 24px 28px;">
          <div style="font-family: monospace; font-size: 11px; text-transform: uppercase; color: #10B981; letter-spacing: 0.05em; margin-bottom: 10px;">
            Message Content:
          </div>
          <div style="padding: 16px; background-color: #050508; border: 1px solid #1E293B; border-radius: 8px; font-size: 14px; line-height: 1.6; color: #E2E8F0; white-space: pre-wrap;">
{safe_message}
          </div>
        </div>

        <!-- Footer / Reply Hint -->
        <div style="padding: 16px 28px; background-color: #070A0F; border-top: 1px solid #1E293B; font-size: 12px; color: #64748B;">
          💡 <strong>Tip:</strong> Simply click <em>Reply</em> in your email client to reply directly to <span style="color: #00F0FF;">{safe_email}</span>.
        </div>
      </div>
    </body>
    </html>
    """

    plain_text = f"""
New Recruiter Inquiry from Shreyas Portfolio
--------------------------------------------
From: {safe_name}
Email: {submission.sender_email}
Company: {safe_company}
Role / Opportunity: {safe_role}
Timestamp: {submitted_at_str}

Message:
{submission.message}

Reply directly to this email to respond to {submission.sender_email}.
    """.strip()

    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "ShreyasPortfolioAPI/1.0",
    }

    payload = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [settings.CONTACT_NOTIFY_EMAIL],
        "reply_to": submission.sender_email,
        "subject": subject,
        "html": html_content,
        "text": plain_text,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=False) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code in (200, 201):
                res_data = resp.json()
                email_id = res_data.get("id")
                logger.info("Resend email dispatched successfully: id=%s", email_id)
                return True, email_id
            else:
                err_text = resp.text[:300]
                logger.warning(
                    "Resend API rejected dispatch (status %d): %s",
                    resp.status_code,
                    err_text,
                )
                return False, f"Resend HTTP {resp.status_code}: {err_text}"
    except Exception as exc:
        logger.warning("Resend email dispatch error: %s", type(exc).__name__)
        return False, str(exc)


@router.post(
    "/contact",
    response_model=ContactSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_recruiter_contact(
    request: Request,
    payload: ContactSubmissionRequest,
    db: AsyncSession = Depends(get_db),
) -> ContactSubmissionResponse:
    """Accept a rate-limited, Turnstile-verified recruiter inquiry."""
    ip_hash = hash_client_ip(request)
    await check_rate_limit("contact_submit", ip_hash, limit=3, window_seconds=3600)

    await verify_turnstile_token(payload.turnstile_token, extract_client_ip(request))

    profile = (
        await db.execute(
            select(CandidateProfile).where(CandidateProfile.singleton_key == "SHREYAS_REDDY")
        )
    ).scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "PROFILE_NOT_FOUND", "message": "Candidate profile not seeded."},
        )

    submission = ContactSubmission(
        sender_name=payload.sender_name,
        sender_email=str(payload.sender_email),
        sender_company=payload.sender_company,
        role_opportunity=payload.role_opportunity,
        message=payload.message,
        ip_sha256=ip_hash,
        turnstile_verified=True,
        status="received",
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    email_sent, _ = await send_recruiter_email_via_resend(submission)
    if email_sent:
        submission.status = "notified"
        await db.commit()
        await db.refresh(submission)

    phone_digits = profile.phone_cleartext.replace(" ", "").replace("-", "")
    return ContactSubmissionResponse(
        status=submission.status,
        submission_id=submission.id,
        message=(
            "Thank you for reaching out. Your message has been delivered directly to Shreyas's inbox."
            if email_sent
            else "Thank you for reaching out. Your message has been recorded."
        ),
        email_dispatched=email_sent,
        contact=ContactRevealResponse(
            email=profile.email_cleartext,
            phone=profile.phone_cleartext,
            mailto_uri=f"mailto:{profile.email_cleartext}",
            tel_uri=f"tel:{phone_digits}",
            linkedin_url=profile.linkedin_url,
        ),
    )

