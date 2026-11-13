"use client";

import { Award, ExternalLink, Eye, FileText, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { CertificateItem } from "@/lib/types";
import { PdfViewerModal } from "./PdfViewerModal";

export function CertificatesClientView({
  certificates,
}: {
  certificates: CertificateItem[];
}) {
  const [tierFilter, setTierFilter] = useState<"all" | "featured" | "foundation">("all");
  const [activeCategory, setActiveCategory] = useState("All");
  const [selectedCert, setSelectedCert] = useState<CertificateItem | null>(null);

  const categories = useMemo(() => {
    const set = new Set<string>(["All"]);
    certificates.forEach((c) => set.add(c.category));
    return Array.from(set);
  }, [certificates]);

  const counts = useMemo(() => {
    const featuredCount = certificates.filter((c) => c.is_featured).length;
    const foundationCount = certificates.filter((c) => !c.is_featured).length;
    return {
      all: certificates.length,
      featured: featuredCount,
      foundation: foundationCount,
    };
  }, [certificates]);

  const filtered = useMemo(() => {
    return certificates.filter((c) => {
      // Tier filter
      if (tierFilter === "featured" && !c.is_featured) return false;
      if (tierFilter === "foundation" && c.is_featured) return false;
      // Category filter
      if (activeCategory !== "All" && c.category !== activeCategory) return false;
      return true;
    });
  }, [certificates, tierFilter, activeCategory]);

  useEffect(() => {
    function handleHashJump() {
      if (typeof window === "undefined" || !window.location.hash) return;
      const targetSlug = window.location.hash.replace("#", "");
      if (!targetSlug) return;

      const targetCert = certificates.find((c) => c.slug === targetSlug);
      if (targetCert) {
        if (!targetCert.is_featured && tierFilter === "featured") {
          setTierFilter("all");
        }
        if (activeCategory !== "All" && targetCert.category !== activeCategory) {
          setActiveCategory("All");
        }
        setTimeout(() => {
          const el = document.getElementById(targetSlug);
          if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "center" });
            el.classList.add("ring-2", "ring-cyanPulse", "transition-all");
            setTimeout(() => el.classList.remove("ring-2", "ring-cyanPulse"), 2500);
          }
        }, 150);
      }
    }

    handleHashJump();
    window.addEventListener("hashchange", handleHashJump);
    return () => window.removeEventListener("hashchange", handleHashJump);
  }, [certificates, tierFilter, activeCategory]);

  return (
    <div className="space-y-10">
      {/* Emergent-Style Header */}
      <header className="space-y-3">
        <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-emeraldSignal font-semibold">
          <span>──</span>
          <span>CREDENTIALS VAULT &amp; PDF VIEWERS</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-[#FAFAFA]">
          Professional{" "}
          <span className="bg-gradient-to-r from-[#00F0FF] via-[#8B5CF6] to-[#14B8A6] bg-clip-text text-transparent">
            certifications
          </span>
        </h1>

        <p className="text-sm sm:text-base leading-relaxed text-slate-300 max-w-3xl">
          22 verified industry certifications covering Cloud Architecture, Generative AI, Prompt Engineering,
          and Cybersecurity, with 25 local PDF proof documents viewable directly in-app.
        </p>
      </header>

      {/* Top Controls: Tier Switcher + Category Filters */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl border border-hairline bg-surface/70 backdrop-blur">
        {/* Tier Tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-lg border border-hairline bg-obsidian">
          <button
            type="button"
            onClick={() => setTierFilter("all")}
            className={`px-3 py-1.5 rounded-md font-mono text-xs font-medium transition ${
              tierFilter === "all"
                ? "bg-surface text-cyanPulse shadow-sm border border-hairline"
                : "text-slate-400 hover:text-white"
            }`}
          >
            All Vault ({counts.all})
          </button>
          <button
            type="button"
            onClick={() => setTierFilter("featured")}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md font-mono text-xs font-medium transition ${
              tierFilter === "featured"
                ? "bg-emeraldSignal/15 text-emeraldSignal shadow-sm border border-emeraldSignal/40"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Sparkles className="h-3.5 w-3.5" />
            Featured ({counts.featured})
          </button>
          <button
            type="button"
            onClick={() => setTierFilter("foundation")}
            className={`px-3 py-1.5 rounded-md font-mono text-xs font-medium transition ${
              tierFilter === "foundation"
                ? "bg-surface text-slate-200 shadow-sm border border-hairline"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Foundation ({counts.foundation})
          </button>
        </div>

        {/* Category Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setActiveCategory(cat)}
              className={
                activeCategory === cat
                  ? "rounded-md border border-cyanPulse/60 bg-cyanPulse/10 px-2.5 py-1 font-mono text-[11px] font-medium text-cyanPulse"
                  : "rounded-md border border-hairline bg-obsidian/80 px-2.5 py-1 font-mono text-[11px] text-slate-400 hover:border-slate-500 hover:text-slate-200"
              }
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Certificate Cards Grid */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
        {filtered.map((cert) => {
          const pdfAsset = cert.certificate_asset_url || cert.verify_url;
          return (
            <article
              key={cert.slug}
              id={cert.slug}
              className={`scroll-mt-24 flex flex-col justify-between rounded-xl border p-5 backdrop-blur transition-all duration-200 hover:-translate-y-0.5 ${
                cert.is_featured
                  ? "border-hairline bg-surface/90 hover:border-emeraldSignal/60 hover:shadow-lg hover:shadow-emeraldSignal/5"
                  : "border-hairline/60 bg-surface/60 hover:border-slate-500"
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <div
                      className={`p-1.5 rounded-lg border ${
                        cert.is_featured
                          ? "border-emeraldSignal/40 bg-emeraldSignal/10 text-emeraldSignal"
                          : "border-hairline bg-obsidian text-slate-400"
                      }`}
                    >
                      <Award className="h-4 w-4" />
                    </div>
                    {cert.is_featured && (
                      <span className="font-mono text-[10px] text-emeraldSignal uppercase tracking-wider font-semibold">
                        Featured
                      </span>
                    )}
                  </div>
                  <span className="rounded border border-hairline bg-obsidian px-2 py-0.5 font-mono text-[10px] text-cyanPulse">
                    {cert.category}
                  </span>
                </div>

                <div>
                  <h2 className="text-sm font-bold text-[#FAFAFA] leading-snug">
                    {cert.title}
                  </h2>
                  <p className="mt-1 font-mono text-xs text-slate-400">
                    {cert.issuer} · {cert.issue_date}
                  </p>
                </div>

                <p className="text-xs leading-relaxed text-slate-300">
                  {cert.summary}
                </p>

                <div className="flex flex-wrap gap-1">
                  {cert.skills_covered.slice(0, 4).map((skill) => (
                    <span
                      key={skill}
                      className="rounded border border-hairline bg-obsidian px-2 py-0.5 font-mono text-[10px] text-slate-300"
                    >
                      {skill}
                    </span>
                  ))}
                  {cert.skills_covered.length > 4 && (
                    <span className="rounded border border-hairline bg-obsidian px-1.5 py-0.5 font-mono text-[10px] text-slate-400">
                      +{cert.skills_covered.length - 4}
                    </span>
                  )}
                </div>
              </div>

              {/* Card Footer Actions */}
              <div className="mt-5 flex items-center justify-between border-t border-hairline pt-3 font-mono text-xs">
                <span className="text-[11px] text-slate-500 truncate max-w-[120px]" title={cert.credential_id || ""}>
                  {cert.credential_id || "Verified"}
                </span>

                <div className="flex items-center gap-2">
                  {pdfAsset && (
                    <button
                      type="button"
                      onClick={() => setSelectedCert(cert)}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-emeraldSignal/50 bg-emeraldSignal/10 hover:bg-emeraldSignal/20 text-emeraldSignal text-[11px] font-medium transition"
                      title="View PDF Certificate Proof"
                    >
                      <Eye className="h-3 w-3" />
                      <span>View Proof</span>
                    </button>
                  )}
                  {pdfAsset && (
                    <a
                      href={pdfAsset}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1 rounded-md border border-hairline bg-obsidian text-slate-400 hover:text-white hover:border-slate-500 transition"
                      title="Open PDF in new tab"
                    >
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </div>
            </article>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="p-12 text-center rounded-xl border border-hairline bg-surface/50 font-mono text-sm text-slate-400">
          No certificates found for the selected tier and category filter.
        </div>
      )}

      {/* In-App PDF Viewer Modal */}
      <PdfViewerModal
        isOpen={Boolean(selectedCert)}
        onClose={() => setSelectedCert(null)}
        pdfUrl={selectedCert ? (selectedCert.certificate_asset_url || selectedCert.verify_url || null) : null}
        title={selectedCert?.title || "Certificate Document"}
        subtitle={selectedCert ? `${selectedCert.issuer} · Credential ID: ${selectedCert.credential_id || "Verified"}` : undefined}
      />
    </div>
  );
}
