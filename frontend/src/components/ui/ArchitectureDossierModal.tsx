"use client";

import {
  CheckCircle2,
  Cpu,
  ExternalLink,
  Github,
  Layers,
  Network,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { ProjectItem } from "@/lib/types";

interface ArchitectureDossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  project: ProjectItem | null;
}

export function ArchitectureDossierModal({
  isOpen,
  onClose,
  project,
}: ArchitectureDossierModalProps) {
  const [activeTab, setActiveTab] = useState<"pipeline" | "architecture" | "security">("pipeline");

  const dialogRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement | null;
      document.body.style.overflow = "hidden";

      const timer = setTimeout(() => {
        const focusables = dialogRef.current?.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusables && focusables.length > 0) {
          focusables[0].focus();
        }
      }, 50);

      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === "Escape") {
          onClose();
        } else if (e.key === "Tab") {
          if (!dialogRef.current) return;
          const focusables = dialogRef.current.querySelectorAll<HTMLElement>(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          );
          if (focusables.length === 0) return;
          const first = focusables[0];
          const last = focusables[focusables.length - 1];
          if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
          } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      };

      window.addEventListener("keydown", handleKeyDown);
      return () => {
        clearTimeout(timer);
        document.body.style.overflow = "auto";
        window.removeEventListener("keydown", handleKeyDown);
        if (previousActiveElement.current) {
          previousActiveElement.current.focus();
        }
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen || !project) return null;

  const pipelineLayers = project.model_3d_config?.pipeline_layers || [];
  const eyebrow = project.model_3d_config?.eyebrow || project.category.toUpperCase();
  const subtitle = project.model_3d_config?.subtitle || project.tagline;
  const coreConcept = project.model_3d_config?.core_concept || project.summary;
  const metricPills = project.model_3d_config?.metric_pills || [];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/85 backdrop-blur-md transition-opacity duration-200"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="dossier-modal-title"
    >
      <div
        ref={dialogRef}
        className="relative flex flex-col w-full max-w-4xl max-h-[90vh] rounded-2xl border border-hairline bg-[#0B0F17] shadow-2xl shadow-cyanPulse/10 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-hairline bg-surface/90">
          <div className="space-y-1.5 min-w-0 pr-4">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs uppercase tracking-widest text-cyanPulse font-semibold">
                {eyebrow}
              </span>
              <span className="rounded border border-hairline bg-obsidian px-2 py-0.5 font-mono text-[10px] text-emeraldSignal">
                ARCHITECTURAL DOSSIER
              </span>
            </div>
            <h2 id="dossier-modal-title" className="text-2xl sm:text-3xl font-bold text-[#FAFAFA]">
              {project.title}
            </h2>
            <p className="font-mono text-xs text-slate-400">
              {subtitle}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg border border-hairline bg-obsidian text-slate-400 hover:text-white hover:border-slate-500 transition shrink-0"
            aria-label="Close modal"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Metric Banner */}
        {metricPills.length > 0 && (
          <div className="flex flex-wrap gap-2 px-6 py-3 border-b border-hairline bg-obsidian/60">
            {metricPills.map((pill, idx) => (
              <span
                key={idx}
                className="rounded-full border border-cyanPulse/40 bg-cyanPulse/10 px-3 py-1 font-mono text-[11px] font-medium text-cyanPulse"
              >
                {pill}
              </span>
            ))}
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 px-6 border-b border-hairline bg-surface/50 font-mono text-xs">
          <button
            type="button"
            onClick={() => setActiveTab("pipeline")}
            className={`py-3 px-3 border-b-2 font-medium transition ${
              activeTab === "pipeline"
                ? "border-cyanPulse text-cyanPulse"
                : "border-transparent text-slate-400 hover:text-white"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <Layers className="h-3.5 w-3.5" />
              <span>Interactive Pipeline ({pipelineLayers.length} Layers)</span>
            </span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("architecture")}
            className={`py-3 px-3 border-b-2 font-medium transition ${
              activeTab === "architecture"
                ? "border-cyanPulse text-cyanPulse"
                : "border-transparent text-slate-400 hover:text-white"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <Cpu className="h-3.5 w-3.5" />
              <span>System Blueprint & Stack</span>
            </span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("security")}
            className={`py-3 px-3 border-b-2 font-medium transition ${
              activeTab === "security"
                ? "border-cyanPulse text-cyanPulse"
                : "border-transparent text-slate-400 hover:text-white"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Security Invariants</span>
            </span>
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {activeTab === "pipeline" && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl border border-hairline bg-obsidian/80">
                <p className="text-xs font-mono text-cyanPulse uppercase tracking-wider font-semibold">
                  Executive Concept Thesis
                </p>
                <p className="mt-1 text-sm text-slate-200 leading-relaxed">
                  {coreConcept}
                </p>
              </div>

              <div className="space-y-3">
                <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
                  Step-by-Step Execution Layers
                </p>
                {pipelineLayers.map((layer, idx) => {
                  const isCyan = layer.accent === "cyan";
                  const isEmerald = layer.accent === "emerald";
                  return (
                    <div
                      key={layer.id || idx}
                      className="p-4 rounded-xl border border-hairline bg-surface/90 space-y-2 hover:border-cyanPulse/60 transition"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <span
                            className={`px-2 py-0.5 rounded font-mono text-xs font-bold ${
                              isCyan
                                ? "bg-cyanPulse/20 text-cyanPulse border border-cyanPulse/40"
                                : isEmerald
                                  ? "bg-emeraldSignal/20 text-emeraldSignal border border-emeraldSignal/40"
                                  : "bg-purple-500/20 text-purple-400 border border-purple-500/40"
                            }`}
                          >
                            {layer.id}
                          </span>
                          <h4 className="font-semibold text-sm text-[#FAFAFA]">
                            {layer.name}
                          </h4>
                        </div>
                        <span className="font-mono text-xs px-2 py-0.5 rounded border border-hairline bg-obsidian text-slate-400">
                          {layer.badge}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed pl-8">
                        {layer.detail}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === "architecture" && (
            <div className="space-y-6">
              {project.ai_explainer?.architecture_stack && (
                <div className="space-y-2">
                  <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
                    Production Architecture Stack
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {project.ai_explainer.architecture_stack.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 p-2.5 rounded-lg border border-hairline bg-obsidian font-mono text-xs text-slate-200"
                      >
                        <CheckCircle2 className="h-3.5 w-3.5 text-cyanPulse shrink-0" />
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
                  Architecture Specification
                </p>
                <div className="p-4 rounded-xl border border-hairline bg-obsidian font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {project.architecture_md}
                </div>
              </div>

              <div className="space-y-2">
                <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
                  Full Technology Stack
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {project.tech_stack.map((t) => (
                    <span
                      key={t}
                      className="px-2.5 py-1 rounded-md border border-hairline bg-surface font-mono text-xs text-slate-300"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === "security" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
                  Zero-Trust & Engineering Invariants
                </p>
                <div className="space-y-2.5">
                  {(project.security_highlights || []).map((sec, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 p-3 rounded-xl border border-emeraldSignal/30 bg-emeraldSignal/5 text-xs text-slate-200"
                    >
                      <ShieldCheck className="h-4 w-4 text-emeraldSignal shrink-0 mt-0.5" />
                      <span>{sec}</span>
                    </div>
                  ))}
                  {(!project.security_highlights || project.security_highlights.length === 0) && (
                    <div className="p-4 rounded-xl border border-hairline bg-obsidian text-xs text-slate-500">
                      Security details not provided.
                    </div>
                  )}
                </div>
              </div>

              {project.ai_explainer?.engineering_highlights && (
                <div className="space-y-2 pt-2">
                  <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
                    Engineering Milestones & Verification
                  </p>
                  <div className="space-y-2">
                    {project.ai_explainer.engineering_highlights.map((eh, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl border border-hairline bg-surface text-xs text-slate-300"
                      >
                        {eh}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer CTAs */}
        <div className="flex items-center justify-between p-4 px-6 border-t border-hairline bg-surface/80 font-mono text-xs">
          <span className="text-slate-400">
            Telemetry: {project.primary_language || "Python"} · {project.metrics?.[0]?.label}: {project.metrics?.[0]?.value}
          </span>
          <div className="flex items-center gap-2">
            {project.github_url && (
              <a
                href={project.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-hairline bg-obsidian hover:bg-surface text-slate-200 hover:text-white transition"
              >
                <Github className="h-3.5 w-3.5" />
                <span>View Source Code</span>
                <ExternalLink className="h-3 w-3 text-cyanPulse" />
              </a>
            )}
            {project.live_url && (
              <a
                href={project.live_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-cyanPulse text-obsidian font-bold hover:bg-cyan-400 transition"
              >
                <span>Live Deployment</span>
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

