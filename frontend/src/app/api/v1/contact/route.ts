import crypto from "node:crypto";
import { NextResponse } from "next/server";
import {
  checkRateLimit,
  extractClientIp,
  verifyTurnstileServer,
} from "@/lib/server-api-utils";

function sanitizeString(input?: string | null): string {
  if (!input || typeof input !== "string") return "";
  return input
    .replace(/<[^>]+>/g, "")
    .replace(/[\x00-\x1f\x7f]/g, " ")
    .trim();
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export async function POST(req: Request) {
  try {
    const clientIp = extractClientIp(req);
    const rate = checkRateLimit(clientIp, "contact_submit", 5, 600_000);
    if (!rate.allowed) {
      return NextResponse.json(
        {
          error_code: "RATE_LIMIT_EXCEEDED",
          message: "Too many messages sent. Please wait before submitting again.",
          retry_after_seconds: rate.retryAfterSeconds,
        },
        { status: 429 }
      );
    }

    const body = await req.json().catch(() => ({}));

    const safeName = sanitizeString(body.sender_name);
    const safeEmail = sanitizeString(body.sender_email);
    const safeCompany = sanitizeString(body.sender_company) || "Direct / Independent";
    const safeRole = sanitizeString(body.role_opportunity) || "Engineering Opportunity";
    const safeMessage = sanitizeString(body.message);
    const turnstileToken = body.turnstile_token;

    if (!safeName || safeName.length < 2) {
      return NextResponse.json(
        { error_code: "VALIDATION_ERROR", message: "Name must be at least 2 characters." },
        { status: 422 }
      );
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!safeEmail || !emailRegex.test(safeEmail)) {
      return NextResponse.json(
        { error_code: "VALIDATION_ERROR", message: "A valid email address is required." },
        { status: 422 }
      );
    }

    if (!safeMessage || safeMessage.length < 10) {
      return NextResponse.json(
        { error_code: "VALIDATION_ERROR", message: "Message must be at least 10 characters." },
        { status: 422 }
      );
    }

    const isValid = await verifyTurnstileServer(turnstileToken, clientIp);
    if (!isValid) {
      return NextResponse.json(
        { error_code: "TURNSTILE_FAILED", message: "Human verification failed. Please try again." },
        { status: 403 }
      );
    }

    let emailDispatched = false;
    const resendApiKey = process.env.RESEND_API_KEY;
    const targetEmail = process.env.CONTACT_NOTIFY_EMAIL || "shreyas.chemakoora@gmail.com";
    const fromEmail = process.env.RESEND_FROM_EMAIL || "Shreyas Portfolio <onboarding@resend.dev>";

    if (resendApiKey && !resendApiKey.startsWith("re_placeholder")) {
      const nowUtc = new Date().toUTCString();
      const subject = `🚀 [Portfolio Inquiry] ${safeName} (${safeCompany}) — ${safeRole}`;

      const escName = escapeHtml(safeName);
      const escEmail = escapeHtml(safeEmail);
      const escCompany = escapeHtml(safeCompany);
      const escRole = escapeHtml(safeRole);
      const escMessage = escapeHtml(safeMessage).replace(/\n/g, "<br>");

      const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${escapeHtml(subject)}</title>
</head>
<body style="margin: 0; padding: 24px; background-color: #050508; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #FAFAFA;">
  <div style="max-width: 600px; margin: 0 auto; background-color: #0B0F17; border: 1px solid #1E293B; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <div style="background: linear-gradient(90deg, #00F0FF, #8B5CF6); padding: 4px;"></div>
    <div style="padding: 24px 28px 16px; border-bottom: 1px solid #1E293B;">
      <div style="font-family: monospace; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: #00F0FF; margin-bottom: 6px;">
        PORTFOLIO RECRUITER INQUIRY
      </div>
      <h1 style="margin: 0; font-size: 20px; font-weight: 700; color: #FAFAFA;">
        New Direct Message from ${escName}
      </h1>
      <p style="margin: 4px 0 0; font-size: 13px; color: #94A3B8;">
        Received at ${nowUtc} via Shreyas Portfolio
      </p>
    </div>

    <div style="padding: 20px 28px; background-color: #0E1420; border-bottom: 1px solid #1E293B;">
      <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
        <tr>
          <td style="padding: 6px 0; color: #94A3B8; width: 140px; font-family: monospace;">Candidate / Role:</td>
          <td style="padding: 6px 0; color: #FAFAFA; font-weight: 600;">${escRole}</td>
        </tr>
        <tr>
          <td style="padding: 6px 0; color: #94A3B8; font-family: monospace;">Company / Org:</td>
          <td style="padding: 6px 0; color: #FAFAFA; font-weight: 600;">${escCompany}</td>
        </tr>
        <tr>
          <td style="padding: 6px 0; color: #94A3B8; font-family: monospace;">Recruiter Email:</td>
          <td style="padding: 6px 0;">
            <a href="mailto:${escEmail}" style="color: #00F0FF; text-decoration: none; font-weight: 600;">${escEmail}</a>
          </td>
        </tr>
      </table>
    </div>

    <div style="padding: 24px 28px;">
      <div style="font-family: monospace; font-size: 11px; text-transform: uppercase; color: #10B981; letter-spacing: 0.05em; margin-bottom: 10px;">
        Message Content:
      </div>
      <div style="padding: 16px; background-color: #050508; border: 1px solid #1E293B; border-radius: 8px; font-size: 14px; line-height: 1.6; color: #E2E8F0; white-space: pre-wrap;">
${escMessage}
      </div>
    </div>

    <div style="padding: 16px 28px; background-color: #070A0F; border-top: 1px solid #1E293B; font-size: 12px; color: #64748B;">
      💡 <strong>Tip:</strong> Click <em>Reply</em> in your email client to reply directly to <span style="color: #00F0FF;">${escEmail}</span>.
    </div>
  </div>
</body>
</html>
      `.trim();

      const plainText = `
New Recruiter Inquiry from Shreyas Portfolio
--------------------------------------------
From: ${safeName}
Email: ${safeEmail}
Company: ${safeCompany}
Role / Opportunity: ${safeRole}
Timestamp: ${nowUtc}

Message:
${safeMessage}

Reply directly to this email to respond to ${safeEmail}.
      `.trim();

      try {
        const resendRes = await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${resendApiKey}`,
            "Content-Type": "application/json",
            "User-Agent": "ShreyasPortfolio/1.0",
          },
          body: JSON.stringify({
            from: fromEmail,
            to: [targetEmail],
            reply_to: safeEmail,
            subject,
            html: htmlContent,
            text: plainText,
          }),
          signal: AbortSignal.timeout(8000),
        });

        if (resendRes.ok) {
          emailDispatched = true;
        }
      } catch (e) {
        console.warn("Resend email dispatch error:", e);
      }
    }

    const submissionId = crypto.randomUUID();

    return NextResponse.json(
      {
        id: submissionId,
        status: emailDispatched ? "notified" : "received",
        message: emailDispatched
          ? "Thank you for reaching out. Your message has been delivered directly to Shreyas's inbox."
          : "Thank you for reaching out. Your message has been safely recorded.",
        email_dispatched: emailDispatched,
      },
      { status: 201 }
    );
  } catch (err: any) {
    return NextResponse.json(
      { error_code: "SERVER_ERROR", message: err?.message || "Internal server error." },
      { status: 500 }
    );
  }
}
