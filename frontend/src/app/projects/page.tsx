import { ProjectsClientView } from "@/components/ui/ProjectsClientView";
import { fetchPortfolioBundle } from "@/lib/server-portfolio";

export default async function ProjectsPage() {
  const bundle = await fetchPortfolioBundle();

  return (
    <ProjectsClientView
      flagship={bundle.flagship_projects}
      autoSynced={bundle.auto_synced_repos}
    />
  );
}

