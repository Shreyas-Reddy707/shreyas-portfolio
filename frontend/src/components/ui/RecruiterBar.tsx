"use client";

import { FileText, Github, Linkedin, Menu, Send, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import type { CandidateProfile } from "@/lib/types";
import { ContactModal } from "./ContactModal";

const NAV_ITEMS = [
  { href: "/", label: "Overview" },
  { href: "/projects", label: "Projects" },
  { href: "/experience", label: "Work Experience" },
  { href: "/hackathons", label: "Hackathons" },
  { href: "/certificates", label: "Certifications" },
];

export function RecruiterBar({ profile }: { profile: CandidateProfile }) {
  const rawPathname = usePathname();
  const pathname = rawPathname || "/";
  const [modalOpen, setModalOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-[#050508]/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
          {/* Left: Brand Identity */}
          <Link
            href="/"
            className="flex items-center gap-2.5 font-mono text-sm font-semibold tracking-wider text-white hover:text-cyanPulse transition"
          >
            <span className="h-2 w-2 rounded-full bg-emeraldSignal animate-pulse" />
            <span>SHREYAS REDDY</span>
          </Link>

          {/* Center: Single-row pill navigation container */}
          <nav className="hidden md:flex items-center gap-1 rounded-full border border-slate-800/90 bg-slate-900/80 p-1 shadow-inner">
            {NAV_ITEMS.map((item) => {
              const active =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={
                    active
                      ? "rounded-full border border-[#00F0FF]/40 bg-[#00F0FF]/12 px-3.5 py-1.5 text-xs font-medium text-[#00F0FF] shadow-[0_0_12px_rgba(0,240,255,0.2)] transition"
                      : "rounded-full px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800/80 hover:text-white transition"
                  }
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* Right: Compact & Clean — Never Wraps Below Center Nav */}
          <div className="flex items-center gap-2">
            <a
              href={profile.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-surface/80 text-slate-300 transition hover:border-cyanPulse hover:text-white"
              title="LinkedIn Profile"
            >
              <Linkedin className="h-4 w-4 text-cyanPulse" />
            </a>

            <a
              href={profile.github_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-surface/80 text-slate-300 transition hover:border-cyanPulse hover:text-white"
              title="GitHub Profile"
            >
              <Github className="h-4 w-4" />
            </a>

            <a
              href={profile.resume_pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Download Resume PDF"
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700/80 bg-surface/80 px-3 py-1.5 font-mono text-xs text-slate-200 transition hover:border-[#00F0FF]/50 hover:text-white"
            >
              <FileText className="h-3.5 w-3.5 text-emeraldSignal" />
              <span className="hidden sm:inline">Resume PDF</span>
            </a>

            <button
              type="button"
              onClick={() => setModalOpen(true)}
              className="inline-flex items-center gap-1.5 rounded-lg bg-[#00F0FF] px-3.5 py-1.5 text-xs font-semibold text-slate-950 shadow-[0_0_20px_rgba(0,240,255,0.35)] hover:bg-cyan-300 transition"
            >
              <Send className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Get in Touch</span>
            </button>

            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-surface/80 text-slate-300 hover:text-white transition"
              aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
            >
              {mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-800 bg-[#050508]/95 px-4 py-3 backdrop-blur-xl">
            <nav className="flex flex-col gap-1.5">
              {NAV_ITEMS.map((item) => {
                const active =
                  item.href === "/"
                    ? pathname === "/"
                    : pathname.startsWith(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={
                      active
                        ? "rounded-lg border border-[#00F0FF]/40 bg-[#00F0FF]/12 px-3 py-2 text-xs font-medium text-[#00F0FF]"
                        : "rounded-lg px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800/80 hover:text-white"
                    }
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        )}
      </header>

      <ContactModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        linkedinUrl={profile.linkedin_url}
        githubUrl={profile.github_url}
      />
    </>
  );
}

