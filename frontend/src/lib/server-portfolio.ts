import fs from "node:fs/promises";
import path from "node:path";
import type { PortfolioBundle } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchPortfolioBundle(): Promise<PortfolioBundle> {
  try {
    const res = await fetch(`${API_BASE}/public/portfolio`, {
      next: { revalidate: 3600, tags: ["portfolio"] },
      signal: AbortSignal.timeout(3000),
    });
    if (res.ok) {
      return (await res.json()) as PortfolioBundle;
    }
  } catch {
    // Fall back to local GitOps seed manifest when backend is offline during build
  }

  const candidatePaths = [
    path.resolve(process.cwd(), "..", "content", "portfolio_data.json"),
    path.resolve(process.cwd(), "content", "portfolio_data.json"),
    path.resolve(process.cwd(), "public", "content", "portfolio_data.json"),
    path.resolve(process.cwd(), "frontend", "public", "content", "portfolio_data.json"),
  ];

  let raw: string | null = null;
  for (const candidate of candidatePaths) {
    try {
      raw = await fs.readFile(candidate, "utf-8");
      if (raw) break;
    } catch {
      continue;
    }
  }

  if (!raw) {
    throw new Error(
      "Unable to locate fallback portfolio manifest at content/portfolio_data.json"
    );
  }

  const parsed = JSON.parse(raw);

  const nowIso = new Date().toISOString();
  const projects = (parsed.projects || []).map(
    (p: Record<string, unknown>, idx: number) => ({
      id: `seed-proj-${idx}`,
      stars_count: 0,
      forks_count: 0,
      open_issues_count: 0,
      last_pushed_at: nowIso,
      ...p,
    })
  );

  return {
    profile: parsed.candidate_profile,
    flagship_projects: projects.filter((p: { is_flagship?: boolean }) => p.is_flagship),
    auto_synced_repos: projects.filter((p: { is_flagship?: boolean }) => !p.is_flagship),
    experiences: (parsed.experiences || []).map(
      (e: Record<string, unknown>, idx: number) => ({ id: `seed-exp-${idx}`, ...e })
    ),
    hackathons: (parsed.hackathons || []).map(
      (h: Record<string, unknown>, idx: number) => ({ id: `seed-hack-${idx}`, ...h })
    ),
    certificates: (parsed.certificates || []).map(
      (c: Record<string, unknown>, idx: number) => ({ id: `seed-cert-${idx}`, ...c })
    ),
    last_synced_at: nowIso,
  } as PortfolioBundle;
}

