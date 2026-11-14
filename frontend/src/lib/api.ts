import type { AgentChatResponse, ContactRevealResponse } from "./types";
import { DEV_TURNSTILE_TOKEN, getTurnstileToken } from "./turnstile";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export { DEV_TURNSTILE_TOKEN };

export async function revealContactDetails(
  turnstileToken?: string
): Promise<ContactRevealResponse> {
  const token = turnstileToken || (await getTurnstileToken("contact-reveal"));
  const res = await fetch(`${API_BASE}/public/contact-reveal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ turnstile_token: token }),
  });
  if (!res.ok) {
    throw new Error("Unable to reveal contact details.");
  }
  return (await res.json()) as ContactRevealResponse;
}

export async function submitContactForm(payload: {
  sender_name: string;
  sender_email: string;
  sender_company?: string;
  role_opportunity?: string;
  message: string;
  turnstile_token?: string;
}): Promise<{ status: string; message: string; email_dispatched?: boolean }> {
  const token =
    payload.turnstile_token || (await getTurnstileToken("contact-submit"));
  const res = await fetch(`${API_BASE}/contact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...payload,
      turnstile_token: token,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || "Failed to send message.");
  }
  return (await res.json()) as { status: string; message: string; email_dispatched?: boolean };
}

export async function askShreyasAgent(
  query: string,
  turnstileToken?: string,
  categoryFilter: "project" | "experience" | "hackathon" | "certificate" | null = null
): Promise<AgentChatResponse> {
  const token = turnstileToken || (await getTurnstileToken("agent-chat"));
  const res = await fetch(`${API_BASE}/agent/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      turnstile_token: token,
      category_filter: categoryFilter,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || "Assistant temporarily unavailable.");
  }
  return (await res.json()) as AgentChatResponse;
}
