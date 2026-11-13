import re
import uuid
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")
_HTML_TAGS_RE = re.compile(r"<[^>]+>")


# ---------------------------------------------------------------------------
# Strict Request Schemas (extra="forbid" blocks BOPLA / Mass Assignment)
# ---------------------------------------------------------------------------


class ContactRevealRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    turnstile_token: str = Field(..., min_length=10, max_length=2048)


class AgentChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: str = Field(..., min_length=3, max_length=500)
    turnstile_token: str = Field(..., min_length=10, max_length=2048)
    category_filter: Literal["project", "experience", "hackathon", "certificate"] | None = None

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        cleaned = _CONTROL_CHARS_RE.sub("", v).strip()
        if len(cleaned) < 3:
            raise ValueError("Query must contain at least 3 printable characters.")
        return cleaned


class ContactSubmissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    sender_name: str = Field(..., min_length=2, max_length=120)
    sender_email: EmailStr = Field(..., max_length=160)
    sender_company: str | None = Field(default=None, max_length=140)
    role_opportunity: str | None = Field(default=None, max_length=160)
    message: str = Field(..., min_length=10, max_length=2000)
    turnstile_token: str = Field(..., min_length=10, max_length=2048)

    @field_validator("sender_name", "sender_company", "role_opportunity", "message", mode="before")
    @classmethod
    def strip_html_and_controls(cls, v: Any) -> Any:
        if v is None:
            return None
        if not isinstance(v, str):
            return v
        cleaned = _HTML_TAGS_RE.sub("", v)
        cleaned = _CONTROL_CHARS_RE.sub(" ", cleaned).strip()
        return cleaned


# ---------------------------------------------------------------------------
# Public Read Schemas (Strictly exclude cleartext email & phone)
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    environment: str
    postgres_connected: bool
    redis_connected: bool
    pgvector_enabled: bool
    timestamp: datetime


class CandidateProfilePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str
    display_name: str
    headline: str
    subheadline: str
    location: str
    education_degree: str
    education_institution: str
    graduation_year: int
    github_username: str
    github_url: str
    linkedin_url: str
    email_masked: str
    phone_masked: str
    resume_pdf_url: str
    availability_badge: str
    hero_pillars: list[dict[str, Any]]
    hero_3d_config: dict[str, Any]
    last_github_sync_at: datetime | None = None


class ProjectPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    tagline: str
    category: str
    summary: str
    architecture_md: str
    ai_explainer: dict[str, Any]
    tech_stack: list[str]
    security_highlights: list[str]
    metrics: list[dict[str, Any]]
    github_url: str | None = None
    live_url: str | None = None
    primary_language: str | None = None
    stars_count: int
    forks_count: int
    open_issues_count: int
    is_flagship: bool
    is_featured: bool
    is_auto_synced: bool
    display_order: int
    model_3d_config: dict[str, Any]
    last_pushed_at: datetime


class ExperiencePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    role: str
    organization: str
    organization_url: str | None = None
    location: str
    employment_type: str
    start_date: date
    end_date: date | None = None
    is_current: bool
    summary: str
    highlights: list[str]
    metrics: list[dict[str, Any]]
    tech_stack: list[str]
    spline_node_config: dict[str, Any]
    display_order: int


class HackathonPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    event_name: str
    organizer: str
    project_title: str
    project_id: uuid.UUID | None = None
    award_status: str
    team_name: str
    role: str
    team_members: list[str]
    event_date: date
    problem_statement: str
    architecture_summary: str
    tech_stack: list[str]
    outcomes: list[str]
    github_url: str | None = None
    live_url: str | None = None
    proof_url: str | None = None
    model_3d_config: dict[str, Any]
    display_order: int


class CertificatePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    issuer: str
    category: str
    issue_date: date
    credential_id: str | None = None
    verify_url: str | None = None
    certificate_asset_url: str | None = None
    skills_covered: list[str]
    summary: str
    badge_3d_config: dict[str, Any]
    is_featured: bool
    display_order: int


class PortfolioBundleResponse(BaseModel):
    profile: CandidateProfilePublic
    flagship_projects: list[ProjectPublic]
    auto_synced_repos: list[ProjectPublic]
    experiences: list[ExperiencePublic]
    hackathons: list[HackathonPublic]
    certificates: list[CertificatePublic]
    last_synced_at: datetime


class GitHubProfileManifestResponse(BaseModel):
    schema_version: str = "1.0"
    generated_at: datetime
    candidate: dict[str, str]
    flagship_projects: list[dict[str, Any]]
    recent_auto_synced_repos: list[dict[str, Any]]
    hackathons: list[dict[str, Any]]
    certificates: list[dict[str, Any]]
    markdown_block: str


class ContactRevealResponse(BaseModel):
    email: str
    phone: str
    mailto_uri: str
    tel_uri: str
    linkedin_url: str


class ContactSubmissionResponse(BaseModel):
    status: str
    submission_id: uuid.UUID
    message: str
    contact: ContactRevealResponse
    email_dispatched: bool = Field(default=False)


class AgentCitation(BaseModel):
    source_type: str
    slug: str
    title: str


class AgentChatResponse(BaseModel):
    answer: str
    citations: list[AgentCitation]
    fallback_used: bool
    remaining_queries_in_window: int

