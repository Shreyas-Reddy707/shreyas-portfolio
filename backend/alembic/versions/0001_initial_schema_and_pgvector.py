"""initial schema and pgvector

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-12 17:45:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')

    op.create_table(
        "candidate_profile",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "singleton_key",
            sa.String(length=32),
            server_default=sa.text("'SHREYAS_REDDY'"),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(length=120),
            server_default=sa.text("'Chemakoora Shreyas Reddy'"),
            nullable=False,
        ),
        sa.Column(
            "display_name",
            sa.String(length=80),
            server_default=sa.text("'Shreyas Reddy'"),
            nullable=False,
        ),
        sa.Column("headline", sa.String(length=255), nullable=False),
        sa.Column("subheadline", sa.Text(), nullable=False),
        sa.Column(
            "location",
            sa.String(length=120),
            server_default=sa.text("'Hyderabad, Telangana, India'"),
            nullable=False,
        ),
        sa.Column(
            "education_degree",
            sa.String(length=180),
            server_default=sa.text(
                "'B.Tech in Computer Science & Engineering (Artificial Intelligence)'"
            ),
            nullable=False,
        ),
        sa.Column(
            "education_institution",
            sa.String(length=180),
            server_default=sa.text("'ICFAI Foundation for Higher Education (ICFAI Tech)'"),
            nullable=False,
        ),
        sa.Column(
            "graduation_year", sa.Integer(), server_default=sa.text("2027"), nullable=False
        ),
        sa.Column("github_username", sa.String(length=80), nullable=False),
        sa.Column("github_url", sa.String(length=255), nullable=False),
        sa.Column(
            "linkedin_url",
            sa.String(length=255),
            server_default=sa.text("'https://www.linkedin.com/in/shreyas-reddy-8a7512285'"),
            nullable=False,
        ),
        sa.Column(
            "email_masked",
            sa.String(length=120),
            server_default=sa.text("'shreyas.chemakoora [at] gmail.com'"),
            nullable=False,
        ),
        sa.Column(
            "phone_masked",
            sa.String(length=64),
            server_default=sa.text("'+91 93467-XXXXX'"),
            nullable=False,
        ),
        sa.Column(
            "email_cleartext",
            sa.String(length=160),
            server_default=sa.text("'shreyas.chemakoora@gmail.com'"),
            nullable=False,
        ),
        sa.Column(
            "phone_cleartext",
            sa.String(length=32),
            server_default=sa.text("'+91 9346759117'"),
            nullable=False,
        ),
        sa.Column(
            "resume_pdf_url",
            sa.String(length=255),
            server_default=sa.text("'/resume/Shreyas_Reddy_Resume.pdf'"),
            nullable=False,
        ),
        sa.Column(
            "availability_badge",
            sa.String(length=120),
            server_default=sa.text(
                "'Open to AI Engineering & Full-Stack Internships / Grad Roles'"
            ),
            nullable=False,
        ),
        sa.Column(
            "hero_pillars",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "hero_3d_config",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("last_github_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "singleton_key = 'SHREYAS_REDDY'", name="ck_candidate_profile_singleton"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("singleton_key"),
    )

    op.create_table(
        "projects",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("github_repo_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("tagline", sa.String(length=280), nullable=False),
        sa.Column(
            "category",
            sa.String(length=64),
            server_default=sa.text("'Agentic AI & RAG'"),
            nullable=False,
        ),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("architecture_md", sa.Text(), nullable=False),
        sa.Column(
            "ai_explainer",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "tech_stack",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "security_highlights",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("github_url", sa.String(length=255), nullable=True),
        sa.Column("live_url", sa.String(length=255), nullable=True),
        sa.Column("primary_language", sa.String(length=64), nullable=True),
        sa.Column("stars_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("forks_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("open_issues_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("readme_sha", sa.String(length=64), nullable=True),
        sa.Column("latest_commit_sha", sa.String(length=64), nullable=True),
        sa.Column("is_flagship", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("is_featured", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("is_auto_synced", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("is_archived", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("display_order", sa.Integer(), server_default=sa.text("100"), nullable=False),
        sa.Column(
            "model_3d_config",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "last_pushed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "category IN ('Agentic AI & RAG', 'Cybersecurity & Zero-Trust', "
            "'Computer Vision & ML', 'Full-Stack & Open Source')",
            name="ck_projects_category",
        ),
        sa.CheckConstraint("stars_count >= 0", name="ck_projects_stars_nonneg"),
        sa.CheckConstraint("forks_count >= 0", name="ck_projects_forks_nonneg"),
        sa.CheckConstraint("open_issues_count >= 0", name="ck_projects_issues_nonneg"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_repo_id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "ix_projects_featured_order",
        "projects",
        [
            sa.text("is_flagship DESC"),
            sa.text("is_featured DESC"),
            sa.text("display_order ASC"),
            sa.text("last_pushed_at DESC"),
        ],
        unique=False,
        postgresql_where=sa.text("is_archived = FALSE"),
    )
    op.create_index("ix_projects_category", "projects", ["category", "display_order"], unique=False)
    op.create_index(
        "ix_projects_last_pushed_at", "projects", [sa.text("last_pushed_at DESC")], unique=False
    )

    op.create_table(
        "experiences",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=160), nullable=False),
        sa.Column("organization", sa.String(length=160), nullable=False),
        sa.Column("organization_url", sa.String(length=255), nullable=True),
        sa.Column(
            "location",
            sa.String(length=120),
            server_default=sa.text("'Hyderabad, India'"),
            nullable=False,
        ),
        sa.Column("employment_type", sa.String(length=64), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column(
            "highlights",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "tech_stack",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "spline_node_config",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("display_order", sa.Integer(), server_default=sa.text("10"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "employment_type IN ('Leadership Internship', 'Technical Team Lead', "
            "'Education', 'Full-Time', 'Part-Time', 'Contract', 'Freelance', 'Internship', 'Open Source')",
            name="ck_experiences_employment_type",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "ix_experiences_timeline",
        "experiences",
        [sa.text("display_order ASC"), sa.text("start_date DESC")],
        unique=False,
    )

    op.create_table(
        "hackathons",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("event_name", sa.String(length=180), nullable=False),
        sa.Column("organizer", sa.String(length=160), nullable=False),
        sa.Column("project_title", sa.String(length=160), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("award_status", sa.String(length=120), nullable=False),
        sa.Column(
            "team_name",
            sa.String(length=80),
            server_default=sa.text("'Team CODEX'"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=120), nullable=False),
        sa.Column(
            "team_members",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("problem_statement", sa.Text(), nullable=False),
        sa.Column("architecture_summary", sa.Text(), nullable=False),
        sa.Column(
            "tech_stack",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "outcomes",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("github_url", sa.String(length=255), nullable=True),
        sa.Column("live_url", sa.String(length=255), nullable=True),
        sa.Column("proof_url", sa.String(length=255), nullable=True),
        sa.Column(
            "model_3d_config",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("display_order", sa.Integer(), server_default=sa.text("10"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_hackathons_project_id", "hackathons", ["project_id"], unique=False)
    op.create_index(
        "ix_hackathons_order_date",
        "hackathons",
        [sa.text("display_order ASC"), sa.text("event_date DESC")],
        unique=False,
    )

    op.create_table(
        "certificates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("issuer", sa.String(length=140), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("credential_id", sa.String(length=128), nullable=True),
        sa.Column("verify_url", sa.String(length=255), nullable=True),
        sa.Column("certificate_asset_url", sa.String(length=255), nullable=True),
        sa.Column(
            "skills_covered",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column(
            "badge_3d_config",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("is_featured", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("display_order", sa.Integer(), server_default=sa.text("10"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "category IN ('AI & Agents', 'Cloud Architecture', 'Cybersecurity', "
            "'Data Science & Big Data')",
            name="ck_certificates_category",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "ix_certificates_category_order",
        "certificates",
        ["category", sa.text("display_order ASC"), sa.text("issue_date DESC")],
        unique=False,
    )

    op.create_table(
        "portfolio_embeddings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("chunk_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("embedding", Vector(768), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "source_type IN ('profile', 'project', 'experience', 'hackathon', 'certificate')",
            name="ck_portfolio_embeddings_source_type",
        ),
        sa.CheckConstraint("chunk_index >= 0", name="ck_portfolio_embeddings_chunk_nonneg"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_type",
            "source_id",
            "chunk_index",
            name="uq_portfolio_embeddings_source_chunk",
        ),
    )
    op.create_index(
        "ix_portfolio_embeddings_source",
        "portfolio_embeddings",
        ["source_type", "source_id"],
        unique=False,
    )
    op.create_index(
        "ix_portfolio_embeddings_content_hash",
        "portfolio_embeddings",
        ["content_hash"],
        unique=False,
    )
    op.create_index(
        "ix_portfolio_embeddings_hnsw_cosine",
        "portfolio_embeddings",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )

    op.create_table(
        "webhook_deliveries",
        sa.Column("delivery_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("repository_full_name", sa.String(length=200), nullable=True),
        sa.Column(
            "signature_verified", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False
        ),
        sa.Column("payload_sha256", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_detail", sa.String(length=500), nullable=True),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('processed', 'ignored', 'failed', 'rejected_hmac')",
            name="ck_webhook_deliveries_status",
        ),
        sa.PrimaryKeyConstraint("delivery_id"),
    )
    op.create_index(
        "ix_webhook_deliveries_processed_at",
        "webhook_deliveries",
        [sa.text("processed_at DESC")],
        unique=False,
    )

    op.create_table(
        "contact_submissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("sender_name", sa.String(length=120), nullable=False),
        sa.Column("sender_email", sa.String(length=160), nullable=False),
        sa.Column("sender_company", sa.String(length=140), nullable=True),
        sa.Column("role_opportunity", sa.String(length=160), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("ip_sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "turnstile_verified", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default=sa.text("'received'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("char_length(message) <= 2000", name="ck_contact_submissions_msg_len"),
        sa.CheckConstraint(
            "status IN ('received', 'notified', 'archived')",
            name="ck_contact_submissions_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_contact_submissions_ip_created",
        "contact_submissions",
        ["ip_sha256", sa.text("created_at DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_contact_submissions_ip_created", table_name="contact_submissions")
    op.drop_table("contact_submissions")

    op.drop_index("ix_webhook_deliveries_processed_at", table_name="webhook_deliveries")
    op.drop_table("webhook_deliveries")

    op.drop_index(
        "ix_portfolio_embeddings_hnsw_cosine",
        table_name="portfolio_embeddings",
        postgresql_using="hnsw",
    )
    op.drop_index("ix_portfolio_embeddings_content_hash", table_name="portfolio_embeddings")
    op.drop_index("ix_portfolio_embeddings_source", table_name="portfolio_embeddings")
    op.drop_table("portfolio_embeddings")

    op.drop_index("ix_certificates_category_order", table_name="certificates")
    op.drop_table("certificates")

    op.drop_index("ix_hackathons_order_date", table_name="hackathons")
    op.drop_index("ix_hackathons_project_id", table_name="hackathons")
    op.drop_table("hackathons")

    op.drop_index("ix_experiences_timeline", table_name="experiences")
    op.drop_table("experiences")

    op.drop_index("ix_projects_last_pushed_at", table_name="projects")
    op.drop_index("ix_projects_category", table_name="projects")
    op.drop_index("ix_projects_featured_order", table_name="projects")
    op.drop_table("projects")

    op.drop_table("candidate_profile")

