"use client";

import { Activity, Layers, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { PipelineLayer, ProjectItem } from "@/lib/types";

interface InteractivePipelineCardProps {
  project: ProjectItem;
  onOpenDossier?: (project: ProjectItem) => void;
}

const DEFAULT_PIPELINE_LAYERS: PipelineLayer[] = [
  {
    id: "L1",
    name: "Input Ingestion & Validation",
    badge: "ingress",
    accent: "cyan",
    detail: "Validates input streams and payload schema boundaries.",
  },
  {
    id: "L2",
    name: "Core Processing Pipeline",
    badge: "core",
    accent: "violet",
    detail: "Executes business logic and algorithmic transformations.",
  },
  {
    id: "L3",
    name: "Security & Policy Invariant Audit",
    badge: "security",
    accent: "emerald",
    detail: "Enforces strict authorization and data sanitization invariants.",
  },
  {
    id: "L4",
    name: "Telemetry & Metric Emission",
    badge: "telemetry",
    accent: "cyan",
    detail: "Streams real-time metrics and operational performance logs.",
  },
  {
    id: "L5",
    name: "Persistent Store & Vector Indexing",
    badge: "store",
    accent: "violet",
    detail: "Persists immutable records and refreshes vector indexes.",
  },
];

export function InteractivePipelineCard({
  project,
  onOpenDossier,
}: InteractivePipelineCardProps) {
  const configuredLayers = project.model_3d_config?.pipeline_layers;
  const layers: PipelineLayer[] =
    configuredLayers && configuredLayers.length > 0
      ? configuredLayers
      : DEFAULT_PIPELINE_LAYERS;

  const [activeLayerIndex, setActiveLayerIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const isPaused = isHovered || isFocused;
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const selectLayer = (idx: number, isExplicit = false) => {
    setActiveLayerIndex(idx);
    if (typeof window !== "undefined") {
      window.dispatchEvent(
        new CustomEvent("portfolio:active-layer", {
          detail: {
            projectSlug: project.slug,
            layerIndex: idx,
            layerId: layers[idx]?.id || "L1",
            selectProject: isExplicit,
          },
        })
      );
    }
  };

  // Dispatch 3D sync event whenever activeLayerIndex changes
  useEffect(() => {
    if (typeof window !== "undefined" && layers.length > 0) {
      window.dispatchEvent(
        new CustomEvent("portfolio:active-layer", {
          detail: {
            projectSlug: project.slug,
            layerIndex: activeLayerIndex,
            layerId: layers[activeLayerIndex]?.id || "L1",
          },
        })
      );
    }
  }, [activeLayerIndex, project.slug, layers]);

  // Auto-cycle through layers every 2.8 seconds when not paused
  useEffect(() => {
    if (isPaused || layers.length <= 1) return;

    timerRef.current = setInterval(() => {
      setActiveLayerIndex((prev) => (prev + 1) % layers.length);
    }, 2800);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPaused, layers.length]);

  return (
    <div
      className="relative flex flex-col justify-between rounded-2xl border border-slate-800/80 bg-[#0B0F17]/95 p-5 shadow-2xl backdrop-blur transition-all duration-300"
      onMouseEnter={() => {
        setIsHovered(true);
        selectLayer(activeLayerIndex, true);
      }}
      onMouseLeave={() => setIsHovered(false)}
      onFocus={() => setIsFocused(true)}
      onBlur={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) {
          setIsFocused(false);
        }
      }}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between pb-3.5 mb-3 border-b border-hairline font-mono text-[11px]">
        <div className="flex items-center gap-2 text-cyanPulse font-semibold">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyanPulse opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyanPulse" />
          </span>
          <span className="tracking-wider uppercase">LIVE PIPELINE ARCHITECTURE</span>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <span className="text-[10px] text-emeraldSignal font-medium">
            L{activeLayerIndex + 1} ACTIVE
          </span>
          <span>·</span>
          <span>CYCLE: {isPaused ? "PAUSED" : "2.8s"}</span>
        </div>
      </div>

      {/* 5 Interactive Pipeline Rows */}
      <div className="space-y-2.5">
        {layers.map((layer, idx) => {
          const isActive = activeLayerIndex === idx;
          const isCyan = layer.accent === "cyan";
          const isEmerald = layer.accent === "emerald";

          return (
            <button
              type="button"
              key={layer.id || idx}
              aria-pressed={isActive}
              onClick={() => selectLayer(idx, true)}
              onMouseEnter={() => selectLayer(idx, true)}
              onFocus={() => selectLayer(idx, true)}
              className={`group w-full text-left cursor-pointer rounded-xl border p-3 transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyanPulse focus-visible:ring-offset-2 focus-visible:ring-offset-[#0B0F17] ${
                isActive
                  ? "border-[#00F0FF] bg-[#00F0FF]/[0.08] shadow-[0_0_22px_rgba(0,240,255,0.18)] scale-[1.01]"
                  : "border-hairline/70 bg-surface/50 hover:border-slate-600 hover:bg-surface/80"
              }`}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2.5 min-w-0">
                  <span
                    className={`px-2 py-0.5 rounded font-mono text-xs font-bold shrink-0 transition ${
                      isActive
                        ? "bg-[#00F0FF] text-obsidian shadow-sm shadow-[#00F0FF]"
                        : isCyan
                          ? "bg-cyanPulse/15 text-cyanPulse border border-cyanPulse/30"
                          : isEmerald
                            ? "bg-emeraldSignal/15 text-emeraldSignal border border-emeraldSignal/30"
                            : "bg-purple-500/15 text-purple-400 border border-purple-500/30"
                    }`}
                  >
                    {layer.id}
                  </span>
                  <h4
                    className={`text-xs sm:text-sm font-semibold truncate transition ${
                      isActive ? "text-[#FAFAFA]" : "text-slate-300 group-hover:text-white"
                    }`}
                  >
                    {layer.name}
                  </h4>
                </div>

                <span
                  className={`font-mono text-[11px] px-2 py-0.5 rounded border shrink-0 transition ${
                    isActive
                      ? "border-cyanPulse/60 bg-cyanPulse/20 text-cyanPulse font-medium"
                      : "border-hairline bg-obsidian text-slate-400"
                  }`}
                >
                  {layer.badge}
                </span>
              </div>

              {/* Expanded detail on active layer */}
              {isActive && (
                <div className="mt-2.5 pt-2 border-t border-cyanPulse/20 pl-7 text-xs text-slate-200 leading-relaxed font-sans animate-in fade-in duration-200">
                  <p>{layer.detail}</p>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Card Bottom Indicator */}
      <div className="mt-3.5 pt-2.5 border-t border-hairline/80 flex items-center justify-between font-mono text-[10px] text-slate-400">
        <span className="flex items-center gap-1.5">
          <Activity className="h-3 w-3 text-cyanPulse" />
          <span>Click or hover layer to inspect telemetry</span>
        </span>
        {onOpenDossier && (
          <button
            type="button"
            onClick={() => onOpenDossier(project)}
            className="text-cyanPulse hover:underline font-semibold"
          >
            Full Dossier →
          </button>
        )}
      </div>
    </div>
  );
}

