export interface HeroPillar {
  id: string;
  label: string;
  count: number;
  accent?: string;
  skills?: string[];
}

export interface CandidateProfile {
  full_name: string;
  display_name: string;
  headline: string;
  subheadline: string;
  location: string;
  education_degree: string;
  education_institution: string;
  graduation_year: number;
  github_username: string;
  github_url: string;
  linkedin_url: string;
  email_masked: string;
  phone_masked: string;
  resume_pdf_url: string;
  availability_badge: string;
  hero_pillars: HeroPillar[];
  hero_3d_config: Record<string, unknown>;
  last_github_sync_at?: string | null;
}

export interface AiExplainer {
  problem_statement?: string;
  architecture_stack?: string[];
  engineering_highlights?: string[];
  generated_by?: string;
  readme_sha_synced?: string;
}

export interface ProjectMetric {
  label: string;
  value: string;
}

export interface PipelineLayer {
  id: string;
  name: string;
  badge: string;
  accent: "cyan" | "violet" | "emerald" | string;
  detail: string;
}

export interface Model3dConfig {
  archetype?: string;
  primary_hex?: string;
  secondary_hex?: string;
  wireframe?: boolean;
  layers_count?: number;
  rotation_speed?: number;
  camera_position?: [number, number, number];
  eyebrow?: string;
  subtitle?: string;
  core_concept?: string;
  why_built?: string;
  core_idea?: string;
  visualizer_type?: string;
  visualizer_config?: Record<string, unknown>;
  metric_pills?: string[];
  pipeline_layers?: PipelineLayer[];
}

export interface ProjectItem {
  id: string;
  slug: string;
  title: string;
  tagline: string;
  category: string;
  summary: string;
  architecture_md: string;
  ai_explainer: AiExplainer;
  tech_stack: string[];
  security_highlights: string[];
  metrics: ProjectMetric[];
  github_url?: string | null;
  live_url?: string | null;
  primary_language?: string | null;
  stars_count: number;
  forks_count: number;
  open_issues_count: number;
  is_flagship: boolean;
  is_featured: boolean;
  is_auto_synced: boolean;
  display_order: number;
  model_3d_config: Model3dConfig;
  last_pushed_at: string;
}

export interface ExperienceItem {
  id: string;
  slug: string;
  role: string;
  organization: string;
  organization_url?: string | null;
  location: string;
  employment_type: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  summary: string;
  highlights: string[];
  metrics: ProjectMetric[];
  tech_stack: string[];
  spline_node_config: {
    z_position?: number;
    accent_hex?: string;
    node_scale?: number;
    status_label?: string;
  };
  display_order: number;
}

export interface HackathonItem {
  id: string;
  slug: string;
  event_name: string;
  organizer: string;
  project_title: string;
  project_id?: string | null;
  award_status: string;
  team_name: string;
  role: string;
  team_members: string[];
  event_date: string;
  problem_statement: string;
  architecture_summary: string;
  tech_stack: string[];
  outcomes: string[];
  github_url?: string | null;
  live_url?: string | null;
  proof_url?: string | null;
  model_3d_config: Model3dConfig;
  display_order: number;
}

export interface CertificateItem {
  id: string;
  slug: string;
  title: string;
  issuer: string;
  category: string;
  issue_date: string;
  credential_id?: string | null;
  verify_url?: string | null;
  certificate_asset_url?: string | null;
  skills_covered: string[];
  summary: string;
  badge_3d_config: Model3dConfig;
  is_featured: boolean;
  display_order: number;
}

export interface PortfolioBundle {
  profile: CandidateProfile;
  flagship_projects: ProjectItem[];
  auto_synced_repos: ProjectItem[];
  experiences: ExperienceItem[];
  hackathons: HackathonItem[];
  certificates: CertificateItem[];
  last_synced_at: string;
}

export interface ContactRevealResponse {
  email: string;
  phone: string;
  mailto_uri: string;
  tel_uri: string;
  linkedin_url: string;
}

export interface AgentCitation {
  source_type: string;
  slug: string;
  title: string;
}

export interface AgentChatResponse {
  answer: string;
  citations: AgentCitation[];
  fallback_used: boolean;
  remaining_queries_in_window: number;
}

