"use client";

import {
  Building2,
  Calendar,
  CheckCircle2,
  ExternalLink,
  Eye,
  MapPin,
  Sparkles,
} from "lucide-react";
import { useState } from "react";
import type { ExperienceItem } from "@/lib/types";
import { PdfViewerModal } from "./PdfViewerModal";

export function ExperienceClientView({
  experiences,
}: {
  experiences: ExperienceItem[];
}) {
  const [selectedProof, setSelectedProof] = useState<{
    url: string;
    title: string;
    subtitle: string;
  } | null>(null);

  return (
    <div className="space-y-12">
      {/* Emergent-Style Header */}
      <header className="space-y-3">
        <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-[#8B5CF6] font-semibold">
          <span>──</span>
          <span>DEPLOYMENT HISTORY</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-[#FAFAFA]">
          Work{" "}
          <span className="bg-gradient-to-r from-[#00F0FF] via-[#8B5CF6] to-[#14B8A6] bg-clip-text text-transparent">
            experience
          </span>
        </h1>

        <p className="text-sm sm:text-base leading-relaxed text-slate-300 max-w-3xl">
          Forward-deployed engineering: building where the users are — sales floors, hackathon floors and data pipelines.
        </p>
      </header>

      {/* Vertical Spine Timeline with Concentric Glowing Nodes */}
      <div className="relative pl-8 sm:pl-12 space-y-10">
        {/* Continuous Gradient Vertical Spine */}
        <div className="absolute left-[17px] sm:left-[23px] top-4 bottom-4 w-[2px] bg-gradient-to-b from-[#00F0FF] via-[#8B5CF6] to-[#10B981]" />

        {experiences.map((exp, idx) => {
          const hasInternshipProof = exp.slug === "viswam-ai-tech-lead";
          const proofUrl = hasInternshipProof ? "/certificates/viswam-ai-internship.pdf" : null;
          const isCurrent = exp.is_current;
          const nodeColor = exp.spline_node_config?.accent_hex || (idx === 0 ? "#00F0FF" : idx === 1 ? "#A855F7" : "#10B981");
          const statusLabel = exp.spline_node_config?.status_label || (isCurrent ? "ACTIVE NODE" : undefined);

          return (
            <div key={exp.slug} id={exp.slug} className="scroll-mt-24 relative group">
              {/* Concentric Glowing Circular Node */}
              <div
                className="absolute -left-[32px] sm:-left-[42px] top-6 flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-full border-2 bg-obsidian transition-all duration-300 group-hover:scale-110"
                style={{
                  borderColor: nodeColor,
                  boxShadow: `0 0 20px ${nodeColor}80`,
                }}
              >
                <div
                  className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full animate-pulse"
                  style={{ backgroundColor: nodeColor }}
                />
              </div>

              {/* Experience Card */}
              <article
                className={`scroll-mt-24 relative rounded-2xl border p-6 sm:p-8 backdrop-blur transition-all duration-300 overflow-hidden ${
                  isCurrent
                    ? "border-cyanPulse/50 bg-[#0B0F17]/95 shadow-2xl shadow-cyanPulse/10"
                    : "border-hairline bg-[#0B0F17]/85 hover:border-slate-700"
                }`}
              >
                {/* Radial Top-Right Corner Glow */}
                <div
                  className="absolute -top-12 -right-12 w-64 h-64 rounded-full pointer-events-none opacity-40 blur-2xl"
                  style={{
                    background: `radial-gradient(circle, ${nodeColor}33 0%, transparent 70%)`,
                  }}
                />

                {/* Top Metadata Bar */}
                <div className="flex flex-wrap items-center justify-between gap-3 pb-4 mb-4 border-b border-hairline font-mono text-xs">
                  <span className="text-slate-400 font-medium tracking-wider uppercase">
                    {exp.start_date} — {isCurrent ? "PRESENT" : exp.end_date || "PRESENT"}
                  </span>

                  <div className="flex items-center gap-2">
                    {statusLabel && (
                      <span
                        className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-[11px] font-semibold"
                        style={{
                          borderColor: `${nodeColor}66`,
                          backgroundColor: `${nodeColor}15`,
                          color: nodeColor,
                        }}
                      >
                        <span className="h-1.5 w-1.5 rounded-full animate-ping" style={{ backgroundColor: nodeColor }} />
                        <span>{statusLabel}</span>
                      </span>
                    )}
                    <span className="flex items-center gap-1 text-slate-400">
                      <Calendar className="h-3.5 w-3.5 text-slate-500" />
                      <span>{exp.employment_type}</span>
                    </span>
                  </div>
                </div>

                {/* Role Title & Organization */}
                <div className="space-y-1">
                  <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#FAFAFA]">
                    {exp.role}
                  </h2>
                  <div className="flex flex-wrap items-center gap-2 text-sm text-cyanPulse font-medium">
                    <Building2 className="h-4 w-4 text-cyanPulse shrink-0" />
                    <span>{exp.organization}</span>
                    <span className="text-slate-500">·</span>
                    <span className="flex items-center gap-1 text-slate-400 font-mono text-xs">
                      <MapPin className="h-3 w-3" />
                      <span>{exp.location}</span>
                    </span>
                  </div>
                </div>

                {/* Left-Bordered Thesis Quote */}
                <div className="mt-5 p-4 rounded-r-xl border-l-2 bg-obsidian/70" style={{ borderColor: nodeColor }}>
                  <p className="text-sm text-slate-200 italic leading-relaxed">
                    &ldquo;{exp.summary}&rdquo;
                  </p>
                </div>

                {/* Checkmark Bullets */}
                <ul className="mt-5 space-y-3 text-sm text-slate-300">
                  {exp.highlights.map((h, i) => (
                    <li key={i} className="flex items-start gap-2.5">
                      <CheckCircle2
                        className="h-4 w-4 shrink-0 mt-0.5"
                        style={{ color: nodeColor }}
                      />
                      <span className="leading-relaxed">{h}</span>
                    </li>
                  ))}
                </ul>

                {/* Skill Pills & Proof CTA */}
                <div className="mt-6 pt-5 border-t border-hairline flex flex-wrap items-center justify-between gap-4">
                  <div className="flex flex-wrap gap-1.5">
                    {exp.tech_stack.map((skill) => (
                      <span
                        key={skill}
                        className="rounded-lg border border-hairline bg-obsidian px-3 py-1 font-mono text-xs text-slate-300"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>

                  {proofUrl && (
                    <button
                      type="button"
                      onClick={() =>
                        setSelectedProof({
                          url: proofUrl,
                          title: "Viswam.ai Technical Leadership Internship Certificate",
                          subtitle: "Tech Lead — AI & Software Development Pod (June – August 2025)",
                        })
                      }
                      className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg border border-[#A855F7]/50 bg-[#A855F7]/15 hover:bg-[#A855F7]/25 text-[#A855F7] font-mono text-xs font-semibold transition"
                    >
                      <Eye className="h-3.5 w-3.5" />
                      <span>View Certificate PDF</span>
                    </button>
                  )}
                </div>
              </article>
            </div>
          );
        })}
      </div>

      {/* Proof Modal */}
      <PdfViewerModal
        isOpen={Boolean(selectedProof)}
        onClose={() => setSelectedProof(null)}
        pdfUrl={selectedProof?.url || null}
        title={selectedProof?.title || "Verification Document"}
        subtitle={selectedProof?.subtitle}
      />
    </div>
  );
}
