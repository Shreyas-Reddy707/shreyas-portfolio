"use client";

import {
  ArrowRight,
  Check,
  Copy,
  FileText,
  FolderGit2,
  Github,
  Linkedin,
  Mail,
  Phone,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { revealContactDetails } from "@/lib/api";
import type { CandidateProfile } from "@/lib/types";

export function HeroQuickConnectStrip({
  profile,
  flagshipCount,
}: {
  profile: CandidateProfile;
  flagshipCount: number;
}) {
  const [copiedType, setCopiedType] = useState<"email" | "phone" | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  async function handleCopy(kind: "email" | "phone") {
    try {
      const revealed = await revealContactDetails();
      const val = kind === "email" ? revealed.email : revealed.phone;
      await navigator.clipboard.writeText(val);
      setCopiedType(kind);
      setToast(
        kind === "email" ? `Copied email: ${val}` : `Copied phone: ${val}`
      );
      setTimeout(() => {
        setCopiedType(null);
        setToast(null);
      }, 3000);
    } catch {
      setToast("Unable to reveal contact. Try LinkedIn or direct message.");
      setTimeout(() => setToast(null), 3000);
    }
  }

  return (
    <>
      <div className="flex flex-wrap items-center gap-2.5 pt-2">
        <Link
          href="/projects"
          className="inline-flex items-center gap-2 rounded-lg bg-cyanPulse px-4 py-2.5 text-xs font-semibold text-slate-950 shadow-[0_0_20px_rgba(0,240,255,0.35)] transition hover:bg-cyan-300"
        >
          <FolderGit2 className="h-4 w-4" />
          <span>Explore {flagshipCount} Flagships</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>

        <a
          href={profile.resume_pdf_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-surface/80 px-3.5 py-2.5 font-mono text-xs text-slate-200 transition hover:border-emeraldSignal hover:text-white"
        >
          <FileText className="h-3.5 w-3.5 text-emeraldSignal" />
          <span>Download Resume PDF</span>
        </a>

        <button
          type="button"
          onClick={() => void handleCopy("email")}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-800 bg-surface/80 px-3 py-2.5 font-mono text-xs text-slate-200 transition hover:border-cyanPulse hover:text-white"
          title="Click to copy verified email"
        >
          {copiedType === "email" ? (
            <Check className="h-3.5 w-3.5 text-emeraldSignal" />
          ) : (
            <Mail className="h-3.5 w-3.5 text-cyanPulse" />
          )}
          <span>{copiedType === "email" ? "Email Copied!" : "Copy Email"}</span>
          <Copy className="h-3 w-3 text-slate-500" />
        </button>

        <button
          type="button"
          onClick={() => void handleCopy("phone")}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-800 bg-surface/80 px-3 py-2.5 font-mono text-xs text-slate-200 transition hover:border-emeraldSignal hover:text-white"
          title="Click to copy verified phone"
        >
          {copiedType === "phone" ? (
            <Check className="h-3.5 w-3.5 text-emeraldSignal" />
          ) : (
            <Phone className="h-3.5 w-3.5 text-emeraldSignal" />
          )}
          <span>{copiedType === "phone" ? "Phone Copied!" : "Copy Phone"}</span>
          <Copy className="h-3 w-3 text-slate-500" />
        </button>

        <a
          href={profile.linkedin_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-800 bg-surface/80 px-3 py-2.5 text-xs text-slate-300 transition hover:border-cyanPulse hover:text-white"
          title="LinkedIn Profile"
        >
          <Linkedin className="h-3.5 w-3.5 text-cyanPulse" />
          <span className="hidden sm:inline">LinkedIn</span>
        </a>

        <a
          href={profile.github_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-800 bg-surface/80 px-3 py-2.5 text-xs text-slate-300 transition hover:border-cyanPulse hover:text-white"
          title="GitHub Profile"
        >
          <Github className="h-3.5 w-3.5 text-slate-300" />
          <span className="hidden sm:inline">GitHub</span>
        </a>
      </div>

      {toast && (
        <div className="fixed bottom-5 left-5 z-50 rounded-lg border border-emeraldSignal/40 bg-surface px-4 py-2.5 font-mono text-xs text-emerald-200 shadow-xl backdrop-blur">
          {toast}
        </div>
      )}
    </>
  );
}

