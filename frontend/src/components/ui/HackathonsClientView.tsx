"use client";

import { Eye, Github, Trophy, Users } from "lucide-react";
import { useState } from "react";
import type { HackathonItem } from "@/lib/types";
import { PdfViewerModal } from "./PdfViewerModal";

export function HackathonsClientView({
  hackathons,
}: {
  hackathons: HackathonItem[];
}) {
  const [selectedProof, setSelectedProof] = useState<{
    url: string;
    title: string;
    subtitle: string;
  } | null>(null);

  return (
    <div className="space-y-10">
      {/* Emergent-Style Header */}
      <header className="space-y-3">
        <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-cyanPulse font-semibold">
          <span>──</span>
          <span>COMPETITIVE PROOF-OF-WORK</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-[#FAFAFA]">
          Hackathon{" "}
          <span className="bg-gradient-to-r from-[#00F0FF] via-[#8B5CF6] to-[#14B8A6] bg-clip-text text-transparent">
            case studies
          </span>
        </h1>

        <p className="text-sm sm:text-base leading-relaxed text-slate-300 max-w-3xl">
          Rapid-fire engineering prototypes and crisis systems built under 36-hour pressure with Team CODEX,
          featuring Devnovate 3.0 (Winner), Smart India Hackathon 2025, and WikiVerse IIIT-H.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {hackathons.map((hack) => {
          // Check if proof_url is available
          const hasProof = Boolean(hack.proof_url);

          return (
            <article
              key={hack.slug}
              id={hack.slug}
              className="scroll-mt-24 flex flex-col justify-between rounded-xl border border-hairline bg-surface/90 p-6 backdrop-blur transition hover:border-cyanPulse/60"
            >
              <div className="space-y-4">
                <div className="flex items-start justify-between gap-2">
                  <span className="inline-flex items-center gap-1.5 rounded border border-emeraldSignal/30 bg-emeraldSignal/10 px-2.5 py-0.5 font-mono text-[11px] text-emeraldSignal">
                    <Trophy className="h-3 w-3" />
                    <span>{hack.award_status}</span>
                  </span>
                  <span className="font-mono text-xs text-slate-400">
                    {hack.event_date}
                  </span>
                </div>

                <div>
                  <h2 className="text-lg font-bold text-[#FAFAFA]">
                    {hack.event_name}
                  </h2>
                  <p className="text-xs text-slate-400">{hack.organizer}</p>
                </div>

                <div className="rounded-lg border border-hairline bg-obsidian/80 p-3">
                  <p className="font-mono text-xs font-semibold text-cyanPulse">
                    {hack.project_title}
                  </p>
                  <p className="mt-1 flex items-center gap-1.5 text-xs text-slate-300">
                    <Users className="h-3.5 w-3.5 text-emeraldSignal" />
                    <span>
                      {hack.team_name} · {hack.role}
                    </span>
                  </p>
                </div>

                <div className="space-y-2 text-xs leading-relaxed text-slate-300">
                  <p>
                    <strong className="font-mono text-slate-200">Problem: </strong>
                    {hack.problem_statement}
                  </p>
                  <p>
                    <strong className="font-mono text-slate-200">Architecture: </strong>
                    {hack.architecture_summary}
                  </p>
                </div>

                <ul className="list-disc space-y-1 pl-4 text-xs text-slate-400">
                  {hack.outcomes.map((o, i) => (
                    <li key={i}>{o}</li>
                  ))}
                </ul>
              </div>

              <div className="mt-5 space-y-3 border-t border-hairline pt-4">
                <div className="flex flex-wrap gap-1.5">
                  {hack.tech_stack.map((tech) => (
                    <span
                      key={tech}
                      className="rounded border border-hairline bg-obsidian px-2 py-0.5 font-mono text-[11px] text-slate-300"
                    >
                      {tech}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between pt-1">
                  {hack.github_url ? (
                    <a
                      href={hack.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 font-mono text-xs text-cyanPulse hover:underline"
                    >
                      <Github className="h-3.5 w-3.5" />
                      <span>View Code</span>
                    </a>
                  ) : (
                    <span />
                  )}

                  {hasProof && hack.proof_url && (
                    <button
                      type="button"
                      onClick={() =>
                        setSelectedProof({
                          url: hack.proof_url!,
                          title: `${hack.event_name} Certificate / Proof`,
                          subtitle: `${hack.award_status} · ${hack.team_name}`,
                        })
                      }
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-emeraldSignal/50 bg-emeraldSignal/10 hover:bg-emeraldSignal/20 text-emeraldSignal font-mono text-xs transition"
                    >
                      <Eye className="h-3 w-3" />
                      <span>View Proof PDF</span>
                    </button>
                  )}
                </div>
              </div>
            </article>
          );
        })}
      </div>

      {/* PDF Modal */}
      <PdfViewerModal
        isOpen={Boolean(selectedProof)}
        onClose={() => setSelectedProof(null)}
        pdfUrl={selectedProof?.url || null}
        title={selectedProof?.title || "Hackathon Proof"}
        subtitle={selectedProof?.subtitle}
      />
    </div>
  );
}

