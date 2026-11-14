import { NextResponse } from "next/server";
import {
  checkRateLimit,
  extractClientIp,
  verifyTurnstileServer,
} from "@/lib/server-api-utils";

export async function POST(req: Request) {
  try {
    const clientIp = extractClientIp(req);
    const rate = checkRateLimit(clientIp, "contact_reveal", 10, 60_000);
    if (!rate.allowed) {
      return NextResponse.json(
        {
          error_code: "RATE_LIMIT_EXCEEDED",
          message: "Too many requests. Please wait a moment before trying again.",
          retry_after_seconds: rate.retryAfterSeconds,
        },
        { status: 429 }
      );
    }

    const body = await req.json().catch(() => ({}));
    const turnstileToken = body.turnstile_token;

    const isValid = await verifyTurnstileServer(turnstileToken, clientIp);
    if (!isValid) {
      return NextResponse.json(
        {
          error_code: "TURNSTILE_FAILED",
          message: "Human verification failed. Please refresh and try again.",
        },
        { status: 403 }
      );
    }

    const email = process.env.CONTACT_NOTIFY_EMAIL || "shreyas.chemakoora@gmail.com";
    const phone = process.env.CONTACT_PHONE || "+91 9346759117";
    const cleanDigits = phone.replace(/[\s-]/g, "");

    return NextResponse.json({
      email,
      phone,
      mailto_uri: `mailto:${email}`,
      tel_uri: `tel:${cleanDigits}`,
      linkedin_url: "https://www.linkedin.com/in/shreyas-reddy-8a7512285",
      github_url: "https://github.com/Shreyas-Reddy707",
      resume_pdf_url: "/resume/Shreyas_Reddy_Resume.pdf",
    });
  } catch (err: any) {
    return NextResponse.json(
      { error_code: "SERVER_ERROR", message: err?.message || "Unexpected error." },
      { status: 500 }
    );
  }
}
