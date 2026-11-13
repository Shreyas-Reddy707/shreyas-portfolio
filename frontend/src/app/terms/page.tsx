export default function TermsPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 rounded-xl border border-hairline bg-surface/90 p-8">
      <h1 className="text-3xl font-bold text-[#FAFAFA]">Terms of Use</h1>
      <p className="text-sm leading-relaxed text-slate-300">
        All architectural blueprints, project summaries, and case studies presented on this site
        belong to Chemakoora Shreyas Reddy unless otherwise noted under open-source licenses.
      </p>
      <section className="space-y-2 text-sm text-slate-300">
        <h2 className="text-lg font-semibold text-emeraldSignal">
          1. Acceptable Use
        </h2>
        <p>
          Automated scraping of contact details, rate-limit evasion, or prompt-injection probing
          against the Ask Shreyas AI endpoint is prohibited.
        </p>
      </section>
      <section className="space-y-2 text-sm text-slate-300">
        <h2 className="text-lg font-semibold text-emeraldSignal">
          2. Open-Source Projects
        </h2>
        <p>
          Linked GitHub repositories remain governed by their respective repository licenses
          (such as MIT for telarc).
        </p>
      </section>
    </div>
  );
}

