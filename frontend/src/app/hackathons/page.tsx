import { fetchPortfolioBundle } from "@/lib/server-portfolio";
import { HackathonsClientView } from "@/components/ui/HackathonsClientView";

export default async function HackathonsPage() {
  const bundle = await fetchPortfolioBundle();

  return <HackathonsClientView hackathons={bundle.hackathons} />;
}
