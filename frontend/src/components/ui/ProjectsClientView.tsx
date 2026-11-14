"use client";

import {
  ExternalLink,
  GitFork,
  Github,
  Network,
  ShieldCheck,
  Sparkles,
  Star,
} from "lucide-react";
import { useMemo, useState } from "react";
import type { ProjectItem } from "@/lib/types";
import { ArchitectureDossierModal } from "./ArchitectureDossierModal";
import { ProjectVisualizerEngine } from "./ProjectVisualizerEngine";

interface ProjectsClientViewProps {
  flagship: ProjectItem[];
  autoSynced: ProjectItem[];
}

export function ProjectsClientView({ flagship, autoSynced }: ProjectsClientViewProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [activeDossierProject, setActiveDossierProject] = useState<ProjectItem | null>(null);

  const categories = useMemo(() => {
    const cats = new Set<string>(["All"]);
    flagship.forEach((p) => cats.add(p.category));
    return Array.from(cats);
  }, [flagship]);

  const filteredFlagship = useMemo(() => {
    if (selectedCategory === "All") return flagship;
    return flagship.filter((p) => p.category === selectedCategory);
  }, [flagship, selectedCategory]);

  return (
    <div className="space-y-16">
      {/* Top Header */}
      <header className="space-y-3">
        <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-cyanPulse font-semibold">
          <span>──</span>
          <span>PRODUCTION BLUEPRINTS &amp; ARCHITECTURE</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-[#FAFAFA]">
          Featured{" "}
          <span className="bg-gradient-to-r from-[#00F0FF] via-[#8B5CF6] to-[#14B8A6] bg-clip-text text-transparent">
            projects
          </span>
        </h1>

        <p className="text-sm sm:text-base leading-relaxed text-slate-300 max-w-3xl">
          Curated production systems (01–05) demonstrating Zero-Trust RAG defenses, autonomous SQL/EDA agents,
          construction ERP workflows, real-time crisis routing, and regional multimedia archival.
        </p>
      </header>

      {/* Category Filter Pills */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl border border-hairline bg-surface/70 backdrop-blur">
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setSelectedCategory(cat)}
              className={
                selectedCategory === cat
                  ? "rounded-lg border border-cyanPulse bg-cyanPulse/15 px-3 py-1.5 font-mono text-xs font-medium text-cyanPulse"
                  : "rounded-lg border border-hairline bg-obsidian px-3 py-1.5 font-mono text-xs text-slate-300 hover:border-slate-500 hover:text-white"
              }
            >
              {cat}
            </button>
          ))}
        </div>
        <span className="font-mono text-xs text-slate-400">
          Showing {filteredFlagship.length} Flagship Architecture Systems
        </span>
      </div>

      {/* Flagship Projects Split-Screen Showcases (01 .. 06) */}
      <section className="space-y-16">
        {filteredFlagship.map((proj, idx) => {
          const indexNumber = String(idx + 1).padStart(2, "0");
          const eyebrow = proj.model_3d_config?.eyebrow || proj.category.toUpperCase();
          const subtitle = proj.model_3d_config?.subtitle || proj.tagline;
          const whyBuilt =
            proj.model_3d_config?.why_built ||
            proj.summary;
          const coreIdea =
            proj.model_3d_config?.core_idea ||
            proj.model_3d_config?.core_concept ||
            proj.tagline;
          const metricPills =
            proj.model_3d_config?.metric_pills ||
            (proj.metrics || []).map((m) => `${m.label}: ${m.value}`);

          return (
            <article
              key={proj.slug}
              id={proj.slug}
              className="scroll-mt-24 relative rounded-3xl border border-hairline bg-surface/70 p-6 sm:p-8 backdrop-blur transition-all duration-300 hover:border-slate-700 hover:shadow-2xl hover:shadow-cyanPulse/5"
            >
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Left Side: System Metadata, Outlined Index & Recruiter Storytelling */}
                <div className="lg:col-span-6 space-y-6">
                  {/* Big Outlined Monospace Index Number + Gradient Rule */}
                  <div className="flex items-center">
                    <span
                      style={{
                        WebkitTextStroke: "1.5px rgba(148, 163, 184, 0.35)",
                        color: "transparent",
                        fontSize: "4.5rem",
                        lineHeight: 1,
                        fontFamily: "monospace",
                        fontWeight: 900,
                      }}
                    >
                      {indexNumber}
                    </span>
                    <div className="flex-1 h-[1px] bg-gradient-to-r from-slate-700 via-slate-800 to-transparent ml-4" />
                  </div>

                  {/* Eyebrow & Title */}
                  <div className="space-y-1.5">
                    <p className="font-mono text-xs uppercase tracking-widest text-cyanPulse font-semibold">
                      {eyebrow}
                    </p>
                    <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#FAFAFA]">
                      {proj.title}
                    </h2>
                    <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
                      {subtitle}
                    </p>
                  </div>

                  {/* Recruiter Storytelling: 2-Row Architectural Callout Grid */}
                  <div className="space-y-3 pt-1">
                    {/* WHY WE BUILT IT */}
                    <div className="p-3.5 rounded-xl border border-amber-500/25 bg-amber-500/5 space-y-1">
                      <div className="flex items-center gap-2 font-mono text-[11px] font-bold text-amber-400 uppercase tracking-wider">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                        <span>WHY WE BUILT IT</span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed font-sans pl-3.5">
                        {whyBuilt}
                      </p>
                    </div>

                    {/* THE CORE IDEA */}
                    <div className="p-3.5 rounded-xl border border-emeraldSignal/30 bg-emeraldSignal/5 space-y-1">
                      <div className="flex items-center gap-2 font-mono text-[11px] font-bold text-emeraldSignal uppercase tracking-wider">
                        <span className="w-1.5 h-1.5 rounded-full bg-emeraldSignal" />
                        <span>THE CORE IDEA</span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed font-sans pl-3.5">
                        {coreIdea}
                      </p>
                    </div>
                  </div>

                  {/* Metric Pills */}
                  {metricPills.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-1">
                      {metricPills.map((pill, pIdx) => (
                        <span
                          key={pIdx}
                          className="rounded-full border border-[#00F0FF]/40 bg-[#00F0FF]/10 text-[#00F0FF] font-mono text-[11px] font-medium px-3.5 py-1"
                        >
                          {pill}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Dual CTA Buttons */}
                  <div className="flex flex-wrap items-center gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setActiveDossierProject(proj)}
                      className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-[#00F0FF] text-obsidian font-mono font-bold text-xs uppercase tracking-wider shadow-[0_0_25px_rgba(0,240,255,0.45)] hover:shadow-[0_0_35px_rgba(0,240,255,0.65)] hover:bg-cyan-300 transition-all duration-200"
                    >
                      <Network className="h-4 w-4" />
                      <span>Explore Architecture</span>
                    </button>

                    {proj.github_url && (
                      <a
                        href={proj.github_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-4 py-3 rounded-lg border border-slate-700 bg-obsidian hover:border-slate-500 text-slate-200 hover:text-white font-mono text-xs uppercase tracking-wider transition-all duration-200"
                      >
                        <Github className="h-4 w-4" />
                        <span>GitHub Repo</span>
                        <ExternalLink className="h-3 w-3 text-cyanPulse" />
                      </a>
                    )}
                  </div>

                  {/* Tech Stack Tags */}
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {proj.tech_stack.slice(0, 6).map((tech) => (
                      <span
                        key={tech}
                        className="rounded border border-hairline bg-obsidian/90 px-2 py-0.5 font-mono text-[11px] text-slate-400"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Right Side: Polymorphic Project Visualizer Engine */}
                <div className="lg:col-span-6">
                  <ProjectVisualizerEngine
                    project={proj}
                    onOpenDossier={(p) => setActiveDossierProject(p)}
                  />
                </div>
              </div>
            </article>
          );
        })}
      </section>

      {/* Part 2: Academic & Explorations (Colab Research & Workbenches) */}
      {autoSynced.length > 0 && (
        <section className="space-y-12 pt-12 border-t border-hairline">
          <div className="space-y-3">
            <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-[#8B5CF6] font-semibold">
              <span>──</span>
              <span>COLAB RESEARCH &amp; EXPERIMENTAL WORKBENCHES</span>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-4">
              <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-[#FAFAFA]">
                Academic &amp;{" "}
                <span className="bg-gradient-to-r from-[#00F0FF] via-[#8B5CF6] to-[#14B8A6] bg-clip-text text-transparent">
                  explorations
                </span>
              </h2>
              <span className="rounded-full border border-hairline bg-obsidian px-3 py-1 font-mono text-xs text-cyanPulse">
                {autoSynced.length} Colab Projects
              </span>
            </div>

            <p className="text-sm leading-relaxed text-slate-300 max-w-3xl">
              Computer vision spatial noise benchmarks in Google Colab, Scikit-Learn evaluation pipelines, and exploratory data wrangling notebooks.
            </p>
          </div>

          <div className="space-y-12">
            {autoSynced.map((repo, idx) => {
              const indexNumber = String(idx + 1).padStart(2, "0");
              const eyebrow = repo.model_3d_config?.eyebrow || repo.category.toUpperCase();
              const subtitle = repo.model_3d_config?.subtitle || repo.tagline;
              const whyBuilt =
                repo.model_3d_config?.why_built || repo.summary;
              const coreIdea =
                repo.model_3d_config?.core_idea ||
                repo.model_3d_config?.core_concept ||
                repo.tagline;
              const metricPills =
                repo.model_3d_config?.metric_pills ||
                (repo.metrics || []).map((m) => `${m.label}: ${m.value}`);

              return (
                <article
                  key={repo.slug}
                  id={repo.slug}
                  className="scroll-mt-24 relative rounded-3xl border border-hairline bg-surface/70 p-6 sm:p-8 backdrop-blur transition-all duration-300 hover:border-slate-700 hover:shadow-2xl hover:shadow-cyanPulse/5"
                >
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                    {/* Left Column: Index, Metadata, 2-Row Callout Grid & Dual CTA */}
                    <div className="lg:col-span-6 space-y-6">
                      {/* Big Outlined Monospace Index Number + Gradient Rule */}
                      <div className="flex items-center">
                        <span
                          style={{
                            WebkitTextStroke: "1.5px rgba(148, 163, 184, 0.35)",
                            color: "transparent",
                            fontSize: "4.5rem",
                            lineHeight: 1,
                            fontFamily: "monospace",
                            fontWeight: 900,
                          }}
                        >
                          {indexNumber}
                        </span>
                        <div className="flex-1 h-[1px] bg-gradient-to-r from-slate-700 via-slate-800 to-transparent ml-4" />
                      </div>

                      {/* Eyebrow & Title */}
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between gap-2">
                          <p className="font-mono text-xs uppercase tracking-widest text-[#8B5CF6] font-semibold">
                            {eyebrow}
                          </p>
                          <span className="rounded border border-amber-500/40 bg-amber-500/10 px-2 py-0.5 font-mono text-[10px] text-amber-400 font-semibold">
                            GOOGLE COLAB
                          </span>
                        </div>
                        <h3 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#FAFAFA]">
                          {repo.title}
                        </h3>
                        <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
                          {subtitle}
                        </p>
                      </div>

                      {/* Recruiter Storytelling: 2-Row Architectural Callout Grid */}
                      <div className="space-y-3 pt-1">
                        {/* WHY WE BUILT IT */}
                        <div className="p-3.5 rounded-xl border border-amber-500/25 bg-amber-500/5 space-y-1">
                          <div className="flex items-center gap-2 font-mono text-[11px] font-bold text-amber-400 uppercase tracking-wider">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                            <span>WHY WE BUILT IT</span>
                          </div>
                          <p className="text-xs text-slate-300 leading-relaxed font-sans pl-3.5">
                            {whyBuilt}
                          </p>
                        </div>

                        {/* THE CORE IDEA */}
                        <div className="p-3.5 rounded-xl border border-emeraldSignal/30 bg-emeraldSignal/5 space-y-1">
                          <div className="flex items-center gap-2 font-mono text-[11px] font-bold text-emeraldSignal uppercase tracking-wider">
                            <span className="w-1.5 h-1.5 rounded-full bg-emeraldSignal" />
                            <span>THE CORE IDEA</span>
                          </div>
                          <p className="text-xs text-slate-300 leading-relaxed font-sans pl-3.5">
                            {coreIdea}
                          </p>
                        </div>
                      </div>

                      {/* Metric Pills */}
                      {metricPills.length > 0 && (
                        <div className="flex flex-wrap gap-2 pt-1">
                          {metricPills.map((pill, pIdx) => (
                            <span
                              key={pIdx}
                              className="rounded-full border border-[#00F0FF]/40 bg-[#00F0FF]/10 text-[#00F0FF] font-mono text-[11px] font-medium px-3.5 py-1"
                            >
                              {pill}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Dual CTA Buttons */}
                      <div className="flex flex-wrap items-center gap-3 pt-2">
                        <button
                          type="button"
                          onClick={() => setActiveDossierProject(repo)}
                          className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-cyanPulse text-obsidian font-mono font-bold text-xs uppercase tracking-wider shadow-[0_0_20px_rgba(0,240,255,0.35)] hover:bg-cyan-300 transition-all duration-200"
                        >
                          <Network className="h-4 w-4" />
                          <span>Explore Architecture</span>
                        </button>

                        {repo.github_url && (
                          <a
                            href={repo.github_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-4 py-3 rounded-lg border border-slate-700 bg-obsidian hover:border-slate-500 text-slate-200 hover:text-white font-mono text-xs uppercase tracking-wider transition-all duration-200"
                          >
                            <Github className="h-4 w-4" />
                            <span>GitHub Repo</span>
                            <ExternalLink className="h-3 w-3 text-cyanPulse" />
                          </a>
                        )}
                      </div>

                      {/* Tech Stack Tags */}
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {repo.tech_stack.map((tech) => (
                          <span
                            key={tech}
                            className="rounded border border-hairline bg-obsidian/90 px-2 py-0.5 font-mono text-[11px] text-slate-400"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Right Column: Polymorphic Project Visualizer Engine */}
                    <div className="lg:col-span-6">
                      <ProjectVisualizerEngine
                        project={repo}
                        onOpenDossier={(p) => setActiveDossierProject(p)}
                      />
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      )}

      {/* Architecture Dossier Modal */}
      <ArchitectureDossierModal
        isOpen={Boolean(activeDossierProject)}
        onClose={() => setActiveDossierProject(null)}
        project={activeDossierProject}
      />
    </div>
  );
}
