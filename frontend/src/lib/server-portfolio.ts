import { loadPortfolioBundle } from "./server-api-utils";
import type { PortfolioBundle } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export async function fetchPortfolioBundle(): Promise<PortfolioBundle> {
  // If an external backend URL is configured (e.g. http://localhost:8000/api/v1), attempt fetch
  if (API_BASE && !API_BASE.startsWith("/")) {
    try {
      const res = await fetch(`${API_BASE}/public/portfolio`, {
        next: { revalidate: 3600, tags: ["portfolio"] },
        signal: AbortSignal.timeout(3000),
      });
      if (res.ok) {
        return (await res.json()) as PortfolioBundle;
      }
    } catch {
      // Fall back to local GitOps seed manifest when external backend is offline
    }
  }

  // Self-contained Serverless mode: loads directly from portfolio_data.json
  return await loadPortfolioBundle();
}

