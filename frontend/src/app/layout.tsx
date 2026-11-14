import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import type { ReactNode } from "react";
import { ClientCanvasShell } from "@/components/canvas/ClientCanvasShell";
import { AskShreyasDrawer } from "@/components/ui/AskShreyasDrawer";
import { RecruiterBar } from "@/components/ui/RecruiterBar";
import { fetchPortfolioBundle } from "@/lib/server-portfolio";
import "./globals.css";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

export const metadata: Metadata = {
  title: {
    default: "Shreyas Reddy | AI & Software Engineer",
    template: "%s | Shreyas Reddy",
  },
  description:
    "Engineering portfolio of Shreyas Reddy — Forward Deployed Engineer (Limelite NZ), Tech Lead at Viswam.ai, Zero-Trust RAG Architect (SecureRAG), & B.Tech CSE (AI) '27.",
  openGraph: {
    title: "Shreyas Reddy | AI & Software Engineer",
    description:
      "Explore SecureRAG, DataMind v2, ConstructPulse, and live GitHub-synced architectures in an interactive 3D spatial workspace.",
    type: "website",
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  const bundle = await fetchPortfolioBundle();
  const { profile, flagship_projects } = bundle;

  const personJsonLd = {
    "@context": "https://schema.org",
    "@type": "Person",
    name: profile.full_name,
    alternateName: profile.display_name,
    jobTitle: "AI Systems & Full-Stack Engineer",
    alumniOf: {
      "@type": "CollegeOrUniversity",
      name: profile.education_institution,
    },
    address: {
      "@type": "PostalAddress",
      addressLocality: "Hyderabad",
      addressRegion: "Telangana",
      addressCountry: "IN",
    },
    sameAs: [profile.linkedin_url, profile.github_url],
  };

  const softwareJsonLd = flagship_projects.map((p) => ({
    "@context": "https://schema.org",
    "@type": "SoftwareSourceCode",
    name: p.title,
    description: p.tagline,
    programmingLanguage: p.primary_language || "Python",
    codeRepository: p.github_url || profile.github_url,
    author: { "@type": "Person", name: profile.full_name },
  }));

  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} dark`}
    >
      <body className="min-h-screen bg-obsidian font-sans text-[#FAFAFA] antialiased">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify([personJsonLd, ...softwareJsonLd]).replace(/</g, "\\u003c"),
          }}
        />

        <ClientCanvasShell />

        <div className="relative z-10 flex min-h-screen flex-col">
          <RecruiterBar profile={profile} />
          <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 lg:py-12">
            {children}
          </main>
          <footer className="border-t border-hairline bg-obsidian/90 py-6 text-xs text-slate-400">
            <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 sm:px-6">
              <p className="font-mono">
                {profile.full_name} · {profile.location}
              </p>
              <div className="flex items-center gap-4">
                <Link href="/privacy" className="hover:text-cyanPulse">
                  Privacy
                </Link>
                <Link href="/terms" className="hover:text-cyanPulse">
                  Terms
                </Link>
                <a href="/llms.txt" className="font-mono hover:text-cyanPulse">
                  /llms.txt
                </a>
              </div>
            </div>
          </footer>
        </div>

        <AskShreyasDrawer />
      </body>
    </html>
  );
}

