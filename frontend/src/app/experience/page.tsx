import { fetchPortfolioBundle } from "@/lib/server-portfolio";
import { ExperienceClientView } from "@/components/ui/ExperienceClientView";

export default async function ExperiencePage() {
  const bundle = await fetchPortfolioBundle();

  return <ExperienceClientView experiences={bundle.experiences} />;
}
