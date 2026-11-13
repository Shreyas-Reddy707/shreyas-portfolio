import uuid
from datetime import date, datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CandidateProfile(Base):
    """Singleton table holding Shreyas Reddy's verified profile and 3D hub config."""

    __tablename__ = "candidate_profile"
    __table_args__ = (
        CheckConstraint("singleton_key = 'SHREYAS_REDDY'", name="ck_candidate_profile_singleton"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    singleton_key: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True, server_default=text("'SHREYAS_REDDY'")
    )
    full_name: Mapped[str] = mapped_column(
        String(120), nullable=False, server_default=text("'Chemakoora Shreyas Reddy'")
    )
    display_name: Mapped[str] = mapped_column(
        String(80), nullable=False, server_default=text("'Shreyas Reddy'")
    )
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    subheadline: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(
        String(120), nullable=False, server_default=text("'Hyderabad, Telangana, India'")
    )
    education_degree: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
        server_default=text("'B.Tech in Computer Science & Engineering (Artificial Intelligence)'"),
    )
    education_institution: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
        server_default=text("'ICFAI Foundation for Higher Education (ICFAI Tech)'"),
    )
    graduation_year: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("2027")
    )
    github_username: Mapped[str] = mapped_column(String(80), nullable=False)
    github_url: Mapped[str] = mapped_column(String(255), nullable=False)
    linkedin_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        server_default=text("'https://www.linkedin.com/in/shreyas-reddy-8a7512285'"),
    )
    email_masked: Mapped[str] = mapped_column(
        String(120), nullable=False, server_default=text("'shreyas.chemakoora [at] gmail.com'")
    )
    phone_masked: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default=text("'+91 93467-XXXXX'")
    )
    email_cleartext: Mapped[str] = mapped_column(
        String(160), nullable=False, server_default=text("'shreyas.chemakoora@gmail.com'")
    )
    phone_cleartext: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'+91 9346759117'")
    )
    resume_pdf_url: Mapped[str] = mapped_column(
        String(255), nullable=False, server_default=text("'/resume/Shreyas_Reddy_Resume.pdf'")
    )
    availability_badge: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        server_default=text("'Open to AI Engineering & Full-Stack Internships / Grad Roles'"),
    )
    hero_pillars: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    hero_3d_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    last_github_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Project(Base):
    """Flagship systems and auto-synced public GitHub repositories."""

    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(
            "category IN ('Agentic AI & RAG', 'Cybersecurity & Zero-Trust', "
            "'Computer Vision & ML', 'Full-Stack & Open Source')",
            name="ck_projects_category",
        ),
        CheckConstraint("stars_count >= 0", name="ck_projects_stars_nonneg"),
        CheckConstraint("forks_count >= 0", name="ck_projects_forks_nonneg"),
        CheckConstraint("open_issues_count >= 0", name="ck_projects_issues_nonneg"),
        Index(
            "ix_projects_featured_order",
            text("is_flagship DESC"),
            text("is_featured DESC"),
            text("display_order ASC"),
            text("last_pushed_at DESC"),
            postgresql_where=text("is_archived = FALSE"),
        ),
        Index("ix_projects_category", "category", "display_order"),
        Index("ix_projects_last_pushed_at", text("last_pushed_at DESC")),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    github_repo_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    tagline: Mapped[str] = mapped_column(String(280), nullable=False)
    category: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default=text("'Agentic AI & RAG'")
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    architecture_md: Mapped[str] = mapped_column(Text, nullable=False)
    ai_explainer: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    tech_stack: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    security_highlights: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    metrics: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    github_url: Mapped[str | None] = mapped_column(String(255))
    live_url: Mapped[str | None] = mapped_column(String(255))
    primary_language: Mapped[str | None] = mapped_column(String(64))
    stars_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    forks_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    open_issues_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    readme_sha: Mapped[str | None] = mapped_column(String(64))
    latest_commit_sha: Mapped[str | None] = mapped_column(String(64))
    is_flagship: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE")
    )
    is_auto_synced: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("100")
    )
    model_3d_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    last_pushed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Experience(Base):
    """Career leadership and academic milestones on the 3D Z-axis timeline."""

    __tablename__ = "experiences"
    __table_args__ = (
        CheckConstraint(
            "employment_type IN ('Leadership Internship', 'Technical Team Lead', "
            "'Education', 'Full-Time', 'Open Source')",
            name="ck_experiences_employment_type",
        ),
        Index("ix_experiences_timeline", text("display_order ASC"), text("start_date DESC")),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(160), nullable=False)
    organization: Mapped[str] = mapped_column(String(160), nullable=False)
    organization_url: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(
        String(120), nullable=False, server_default=text("'Hyderabad, India'")
    )
    employment_type: Mapped[str] = mapped_column(String(64), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    highlights: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    metrics: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    tech_stack: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    spline_node_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Hackathon(Base):
    """Hackathon Arena case studies and proof-of-work builds."""

    __tablename__ = "hackathons"
    __table_args__ = (
        Index("ix_hackathons_project_id", "project_id"),
        Index("ix_hackathons_order_date", text("display_order ASC"), text("event_date DESC")),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    event_name: Mapped[str] = mapped_column(String(180), nullable=False)
    organizer: Mapped[str] = mapped_column(String(160), nullable=False)
    project_title: Mapped[str] = mapped_column(String(160), nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL")
    )
    award_status: Mapped[str] = mapped_column(String(120), nullable=False)
    team_name: Mapped[str] = mapped_column(
        String(80), nullable=False, server_default=text("'Team CODEX'")
    )
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    team_members: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    architecture_summary: Mapped[str] = mapped_column(Text, nullable=False)
    tech_stack: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    outcomes: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    github_url: Mapped[str | None] = mapped_column(String(255))
    live_url: Mapped[str | None] = mapped_column(String(255))
    proof_url: Mapped[str | None] = mapped_column(String(255))
    model_3d_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Certificate(Base):
    """Verified credentials vault with category filtering and 3D plaque metadata."""

    __tablename__ = "certificates"
    __table_args__ = (
        CheckConstraint(
            "category IN ('AI & Agents', 'Cloud Architecture', 'Cybersecurity', "
            "'Data Science & Big Data')",
            name="ck_certificates_category",
        ),
        Index(
            "ix_certificates_category_order",
            "category",
            text("display_order ASC"),
            text("issue_date DESC"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    issuer: Mapped[str] = mapped_column(String(140), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    credential_id: Mapped[str | None] = mapped_column(String(128))
    verify_url: Mapped[str | None] = mapped_column(String(255))
    certificate_asset_url: Mapped[str | None] = mapped_column(String(255))
    skills_covered: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    badge_3d_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE")
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class PortfolioEmbedding(Base):
    """768-dimensional pgvector store for 'Ask Shreyas AI' RAG retrieval."""

    __tablename__ = "portfolio_embeddings"
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('profile', 'project', 'experience', 'hackathon', 'certificate')",
            name="ck_portfolio_embeddings_source_type",
        ),
        CheckConstraint("chunk_index >= 0", name="ck_portfolio_embeddings_chunk_nonneg"),
        UniqueConstraint(
            "source_type",
            "source_id",
            "chunk_index",
            name="uq_portfolio_embeddings_source_chunk",
        ),
        Index("ix_portfolio_embeddings_source", "source_type", "source_id"),
        Index("ix_portfolio_embeddings_content_hash", "content_hash"),
        Index(
            "ix_portfolio_embeddings_hnsw_cosine",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    source_slug: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(768), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class WebhookDelivery(Base):
    """Immutable HMAC idempotency and audit ledger for GitHub webhooks."""

    __tablename__ = "webhook_deliveries"
    __table_args__ = (
        CheckConstraint(
            "status IN ('processed', 'ignored', 'failed', 'rejected_hmac')",
            name="ck_webhook_deliveries_status",
        ),
        Index("ix_webhook_deliveries_processed_at", text("processed_at DESC")),
    )

    delivery_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    repository_full_name: Mapped[str | None] = mapped_column(String(200))
    signature_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    payload_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_detail: Mapped[str | None] = mapped_column(String(500))
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ContactSubmission(Base):
    """Turnstile-verified recruiter contact messages with hashed IP tracking."""

    __tablename__ = "contact_submissions"
    __table_args__ = (
        CheckConstraint("char_length(message) <= 2000", name="ck_contact_submissions_msg_len"),
        CheckConstraint(
            "status IN ('received', 'notified', 'archived')",
            name="ck_contact_submissions_status",
        ),
        Index("ix_contact_submissions_ip_created", "ip_sha256", text("created_at DESC")),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    sender_name: Mapped[str] = mapped_column(String(120), nullable=False)
    sender_email: Mapped[str] = mapped_column(String(160), nullable=False)
    sender_company: Mapped[str | None] = mapped_column(String(140))
    role_opportunity: Mapped[str | None] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    ip_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    turnstile_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE")
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'received'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

