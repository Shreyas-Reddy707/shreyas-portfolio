import { CertificatesClientView } from "@/components/ui/CertificatesClientView";
import { fetchPortfolioBundle } from "@/lib/server-portfolio";

export default async function CertificatesPage() {
  const bundle = await fetchPortfolioBundle();

  return <CertificatesClientView certificates={bundle.certificates} />;
}

