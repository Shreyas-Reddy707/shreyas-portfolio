import {
  ArrowRight,
  Award,
  Briefcase,
  Cpu,
  Database,
  ExternalLink,
  FolderGit2,
  Globe,
  Layers,
  Shield,
  Sparkles,
  Trophy,
} from "lucide-react";
import Link from "next/link";
import { HeroQuickConnectStrip } from "@/components/ui/HeroQuickConnectStrip";
import { fetchPortfolioBundle } from "@/lib/server-portfolio";

export default async function CommandHubPage() {
  const bundle = await fetchPortfolioBundle();
  const { profile, flagship_projects, auto_synced_repos, experiences, hackathons, certificates } =
    bundle;

  const featuredCertCount = certificates.filter((c) => c.is_featured).length;

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="max-w-3xl space-y-6 pt-4">
        <div className="flex items-center gap-2 font-mono text-[11px] tracking-wider text-cyanPulse uppercase">
          <span>──</span>
          <span>AI &amp; SOFTWARE ENGINEERING PORTFOLIO</span>
        </div>

        <div className="inline-flex items-center gap-2 rounded-full border border-emeraldSignal/30 bg-emeraldSignal/10 px-3 py-1 font-mono text-xs text-emeraldSignal">
          <span className="h-1.5 w-1.5 rounded-full bg-emeraldSignal animate-pulse" />
          <span>{profile.availability_badge}</span>
        </div>

        <h1 className="text-4xl font-extrabold tracking-tight text-[#FAFAFA] sm:text-5xl">
          Shreyas{" "}
          <span className="bg-gradient-to-r from-[#00F0FF] via-[#8B5CF6] to-[#14B8A6] bg-clip-text text-transparent">
            Reddy
          </span>
        </h1>

        <p className="text-lg font-medium text-cyanPulse sm:text-xl">
          {profile.headline}
        </p>

        <p className="leading-relaxed text-slate-300">
          {profile.subheadline}
        </p>

        {/* Hero Recruiter Quick-Action Strip */}
        <HeroQuickConnectStrip
          profile={profile}
          flagshipCount={flagship_projects.length}
        />
      </section>

      {/* Live Engineering Telemetry */}
      <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-xl border border-hairline bg-surface/85 p-4 backdrop-blur">
          <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
            Active Role
          </p>
          <p className="mt-1 font-mono text-xl font-bold text-cyanPulse truncate">FDE @ Limelite</p>
          <p className="mt-0.5 text-xs text-slate-400">New Zealand (Remote)</p>
        </div>
        <div className="rounded-xl border border-hairline bg-surface/85 p-4 backdrop-blur">
          <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
            Flagship Systems
          </p>
          <p className="mt-1 font-mono text-2xl font-bold text-emeraldSignal">
            {flagship_projects.length}
          </p>
          <p className="mt-0.5 text-xs text-slate-400">
            +{auto_synced_repos.length} Auto-Synced GitHub Repos
          </p>
        </div>
        <div className="rounded-xl border border-hairline bg-surface/85 p-4 backdrop-blur">
          <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
            Hackathons
          </p>
          <p className="mt-1 font-mono text-2xl font-bold text-[#FAFAFA]">
            {hackathons.length}
          </p>
          <p className="mt-0.5 text-xs text-slate-400">SIH &apos;25 · Devnovate 3.0 · WikiVerse</p>
        </div>
        <div className="rounded-xl border border-hairline bg-surface/85 p-4 backdrop-blur">
          <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
            Verified Certs
          </p>
          <p className="mt-1 font-mono text-2xl font-bold text-cyanPulse">
            {certificates.length}
          </p>
          <p className="mt-0.5 text-xs text-slate-400">
            {featuredCertCount} Featured · 25 Local PDFs
          </p>
        </div>
      </section>

      {/* 7-Category Skills Matrix */}
      <section className="space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-[#FAFAFA]">
              Technical{" "}
              <span className="bg-gradient-to-r from-[#00F0FF] via-[#8B5CF6] to-[#14B8A6] bg-clip-text text-transparent">
                skills
              </span>{" "}
              &amp; Architecture Matrix
            </h2>
            <p className="text-xs font-mono text-slate-400 mt-1">
              7 core categories covering 43 verified skills and tools
            </p>
          </div>
          <span className="rounded-full border border-hairline bg-obsidian px-3 py-1 font-mono text-xs text-cyanPulse">
            43 Verified Skills
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {profile.hero_pillars.map((pillar) => (
            <div
              key={pillar.id}
              className="rounded-xl border border-hairline bg-surface/85 p-5 backdrop-blur transition hover:border-cyanPulse/60"
            >
              <div className="flex items-center justify-between pb-3 border-b border-hairline">
                <div className="flex items-center gap-2">
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: pillar.accent || "#00F0FF" }}
                  />
                  <h3 className="text-sm font-semibold text-[#FAFAFA]">
                    {pillar.label}
                  </h3>
                </div>
                <span className="font-mono text-xs text-slate-400">
                  {pillar.count}
                </span>
              </div>

              <div className="mt-3 flex flex-wrap gap-1.5">
                {(pillar.skills || []).map((skill) => (
                  <span
                    key={skill}
                    className="rounded border border-hairline bg-obsidian px-2 py-0.5 font-mono text-[11px] text-slate-300 hover:text-white hover:border-slate-500 transition"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Flagship Systems Highlights */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-[#FAFAFA]">
            Featured{" "}
            <span className="bg-gradient-to-r from-[#00F0FF] via-[#8B5CF6] to-[#14B8A6] bg-clip-text text-transparent">
              projects
            </span>
          </h2>
          <Link
            href="/projects"
            className="inline-flex items-center gap-1 font-mono text-xs text-cyanPulse hover:underline"
          >
            <span>View all {flagship_projects.length} systems</span>
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {flagship_projects.slice(0, 3).map((project) => (
            <Link
              key={project.slug}
              href="/projects"
              className="group rounded-xl border border-hairline bg-surface/85 p-5 transition hover:border-cyanPulse flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <span className="rounded border border-hairline bg-obsidian px-2 py-0.5 font-mono text-[10px] text-cyanPulse">
                    {project.category}
                  </span>
                  <span className="font-mono text-[10px] text-emeraldSignal font-semibold">
                    FLAGSHIP
                  </span>
                </div>
                <h3 className="text-base font-bold text-[#FAFAFA] group-hover:text-cyanPulse">
                  {project.title}
                </h3>
                <p className="text-xs text-slate-300 line-clamp-2">
                  {project.tagline}
                </p>
                <div className="flex flex-wrap gap-1">
                  {project.tech_stack.slice(0, 4).map((tech) => (
                    <span
                      key={tech}
                      className="rounded border border-hairline bg-obsidian px-1.5 py-0.5 font-mono text-[10px] text-slate-400"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-hairline flex items-center justify-between font-mono text-xs text-slate-400">
                <span>{project.metrics?.[0]?.label}: {project.metrics?.[0]?.value}</span>
                <span className="text-cyanPulse group-hover:translate-x-0.5 transition">→</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Quick Navigation Cards */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Link
          href="/projects"
          className="group rounded-xl border border-hairline bg-surface/85 p-5 transition hover:border-cyanPulse"
        >
          <FolderGit2 className="h-5 w-5 text-cyanPulse" />
          <h3 className="mt-3 font-semibold text-[#FAFAFA] group-hover:text-cyanPulse">
            Flagship &amp; GitHub Vault
          </h3>
          <p className="mt-1 text-xs text-slate-400">
            SecureRAG, DataMind v2, ConstructPulse, CrisisPulse, telarc, Denoising + live repos.
          </p>
        </Link>

        <Link
          href="/experience"
          className="group rounded-xl border border-hairline bg-surface/85 p-5 transition hover:border-emeraldSignal"
        >
          <Briefcase className="h-5 w-5 text-emeraldSignal" />
          <h3 className="mt-3 font-semibold text-[#FAFAFA] group-hover:text-emeraldSignal">
            Career &amp; Leadership ({experiences.length})
          </h3>
          <p className="mt-1 text-xs text-slate-400">
            Limelite FDE (NZ), Viswam.ai Tech Lead, ICFAI Tech B.Tech CSE (AI &apos;27).
          </p>
        </Link>

        <Link
          href="/hackathons"
          className="group rounded-xl border border-hairline bg-surface/85 p-5 transition hover:border-cyanPulse"
        >
          <Trophy className="h-5 w-5 text-cyanPulse" />
          <h3 className="mt-3 font-semibold text-[#FAFAFA] group-hover:text-cyanPulse">
            Hackathon Arena ({hackathons.length})
          </h3>
          <p className="mt-1 text-xs text-slate-400">
            Devnovate 3.0 (Winner), SIH 2025 (Finalist), WikiVerse IIIT-H (CrisisPulse).
          </p>
        </Link>

        <Link
          href="/certificates"
          className="group rounded-xl border border-hairline bg-surface/85 p-5 transition hover:border-emeraldSignal"
        >
          <Award className="h-5 w-5 text-emeraldSignal" />
          <h3 className="mt-3 font-semibold text-[#FAFAFA] group-hover:text-emeraldSignal">
            Credentials Vault ({certificates.length})
          </h3>
          <p className="mt-1 text-xs text-slate-400">
            {certificates.length} Verified Certs + In-App PDF Viewers (Microsoft, Google, NVIDIA, IBM, Tata).
          </p>
        </Link>
      </section>
    </div>
  );
}
