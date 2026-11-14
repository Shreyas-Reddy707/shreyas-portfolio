export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 rounded-xl border border-hairline bg-surface/90 p-8">
      <h1 className="text-3xl font-bold text-[#FAFAFA]">Privacy Policy</h1>
      <p className="text-sm leading-relaxed text-slate-300">
        This portfolio operates on a zero-login, zero-tracking architecture. No third-party
        advertising cookies or behavioral trackers are used.
      </p>
      <section className="space-y-2 text-sm text-slate-300">
        <h2 className="text-lg font-semibold text-cyanPulse">
          1. Bot Protection &amp; Rate Limiting
        </h2>
        <p>
          Contact reveal, recruiter inquiry, and AI assistant endpoints use Cloudflare Turnstile
          and keyed HMAC-SHA256 IP hashing in Redis strictly for abuse prevention. Raw visitor IP
          addresses are never persisted to PostgreSQL.
        </p>
      </section>
      <section className="space-y-2 text-sm text-slate-300">
        <h2 className="text-lg font-semibold text-cyanPulse">
          2. Recruiter Inquiries
        </h2>
        <p>
          Messages submitted via the direct contact modal are stored solely for responding to
          career and engineering inquiries.
        </p>
      </section>
    </div>
  );
}

