"use client";

import { Check, CheckCircle2, Copy, Github, Linkedin, Mail, Phone, Send, X } from "lucide-react";
import { useState, type FormEvent } from "react";
import { revealContactDetails, submitContactForm } from "@/lib/api";

interface ContactModalProps {
  open: boolean;
  onClose: () => void;
  linkedinUrl?: string;
  githubUrl?: string;
}

export function ContactModal({ open, onClose, linkedinUrl, githubUrl }: ContactModalProps) {
  const [senderName, setSenderName] = useState("");
  const [senderEmail, setSenderEmail] = useState("");
  const [senderCompany, setSenderCompany] = useState("");
  const [roleOpportunity, setRoleOpportunity] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ message: string; emailDispatched: boolean } | null>(null);
  const [copiedType, setCopiedType] = useState<"email" | "phone" | null>(null);

  if (!open) return null;

  async function handleCopy(kind: "email" | "phone") {
    try {
      const revealed = await revealContactDetails();
      const val = kind === "email" ? revealed.email : revealed.phone;
      await navigator.clipboard.writeText(val);
      setCopiedType(kind);
      setTimeout(() => setCopiedType(null), 3000);
    } catch {
      setError("Unable to retrieve contact details right now.");
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await submitContactForm({
        sender_name: senderName,
        sender_email: senderEmail,
        sender_company: senderCompany || undefined,
        role_opportunity: roleOpportunity || undefined,
        message,
      });
      setSuccess({
        message: res.message,
        emailDispatched: Boolean(res.email_dispatched),
      });
      setSenderName("");
      setSenderEmail("");
      setSenderCompany("");
      setRoleOpportunity("");
      setMessage("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send inquiry.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-md">
      <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-[#0B0F17] p-6 shadow-2xl">
        <div className="mb-4 flex items-center justify-between border-b border-hairline pb-3">
          <div className="flex items-center gap-2 font-mono">
            <span className="h-2 w-2 rounded-full bg-emeraldSignal animate-pulse" />
            <h2 className="text-base font-bold text-[#FAFAFA]">
              Get in Touch with Shreyas Reddy
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close contact modal"
            className="rounded-md p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* 1-Click Fast Contact Channels */}
        <div className="mb-4 space-y-2 rounded-xl border border-hairline bg-surface/50 p-3">
          <p className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
            Instant 1-Click Direct Channels
          </p>
          <div className="grid grid-cols-2 gap-2 font-mono text-xs">
            <button
              type="button"
              onClick={() => handleCopy("email")}
              className="flex items-center justify-center gap-2 rounded-lg border border-hairline bg-obsidian py-2 px-3 text-slate-200 hover:border-cyanPulse hover:text-white transition"
            >
              {copiedType === "email" ? (
                <Check className="h-3.5 w-3.5 text-emeraldSignal" />
              ) : (
                <Mail className="h-3.5 w-3.5 text-cyanPulse" />
              )}
              <span>{copiedType === "email" ? "Copied Email!" : "Copy Email"}</span>
            </button>

            <button
              type="button"
              onClick={() => handleCopy("phone")}
              className="flex items-center justify-center gap-2 rounded-lg border border-hairline bg-obsidian py-2 px-3 text-slate-200 hover:border-emeraldSignal hover:text-white transition"
            >
              {copiedType === "phone" ? (
                <Check className="h-3.5 w-3.5 text-emeraldSignal" />
              ) : (
                <Phone className="h-3.5 w-3.5 text-emeraldSignal" />
              )}
              <span>{copiedType === "phone" ? "Copied Phone!" : "Copy Phone"}</span>
            </button>
          </div>
        </div>

        {success ? (
          <div className="space-y-4 py-4">
            <div className="flex items-start gap-3 rounded-lg border border-emeraldSignal/40 bg-emeraldSignal/10 p-4 text-sm text-emerald-200">
              <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emeraldSignal" />
              <div>
                <p className="font-semibold text-base text-white">
                  {success.emailDispatched
                    ? "Message Sent to Shreyas's Inbox"
                    : "Message Recorded & Saved"}
                </p>
                <p className="mt-1 text-slate-300 text-xs leading-relaxed">
                  {success.emailDispatched
                    ? "Your inquiry has been delivered directly to shreyas.chemakoora@gmail.com. Shreyas will reply directly to your email address shortly."
                    : "Your inquiry has been securely recorded. Shreyas will reply directly to your email address shortly."}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="w-full rounded-lg bg-cyanPulse px-4 py-2 text-sm font-semibold text-obsidian hover:bg-cyan-400 transition"
            >
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3">
            <p className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
              Or Send a Direct Inquiry
            </p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <input
                required
                minLength={2}
                maxLength={120}
                value={senderName}
                onChange={(e) => setSenderName(e.target.value)}
                placeholder="Your Name *"
                className="rounded-lg border border-hairline bg-obsidian px-3 py-2 text-sm text-[#FAFAFA] placeholder:text-slate-500 focus:border-cyanPulse focus:outline-none"
              />
              <input
                required
                type="email"
                maxLength={160}
                value={senderEmail}
                onChange={(e) => setSenderEmail(e.target.value)}
                placeholder="Work Email *"
                className="rounded-lg border border-hairline bg-obsidian px-3 py-2 text-sm text-[#FAFAFA] placeholder:text-slate-500 focus:border-cyanPulse focus:outline-none"
              />
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <input
                maxLength={140}
                value={senderCompany}
                onChange={(e) => setSenderCompany(e.target.value)}
                placeholder="Company / Organization"
                className="rounded-lg border border-hairline bg-obsidian px-3 py-2 text-sm text-[#FAFAFA] placeholder:text-slate-500 focus:border-cyanPulse focus:outline-none"
              />
              <input
                maxLength={160}
                value={roleOpportunity}
                onChange={(e) => setRoleOpportunity(e.target.value)}
                placeholder="Role / Opportunity"
                className="rounded-lg border border-hairline bg-obsidian px-3 py-2 text-sm text-[#FAFAFA] placeholder:text-slate-500 focus:border-cyanPulse focus:outline-none"
              />
            </div>
            <textarea
              required
              minLength={10}
              maxLength={2000}
              rows={3}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Share role details, interview availability, or technical questions..."
              className="w-full rounded-lg border border-hairline bg-obsidian px-3 py-2 text-sm text-[#FAFAFA] placeholder:text-slate-500 focus:border-cyanPulse focus:outline-none"
            />
            {error && (
              <p className="text-xs text-rose-400">{error}</p>
            )}
            <button
              type="submit"
              disabled={submitting}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-cyanPulse px-4 py-2.5 text-sm font-semibold text-obsidian transition hover:bg-cyan-400 disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
              {submitting ? "Sending..." : "Send Direct Inquiry"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

