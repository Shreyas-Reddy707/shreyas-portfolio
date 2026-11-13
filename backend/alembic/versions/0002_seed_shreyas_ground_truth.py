"""seed shreyas ground truth

Revision ID: 0002_seed_ground_truth
Revises: 0001_initial_schema
Create Date: 2026-11-12 17:46:00
"""
import json
from datetime import date
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.portfolio import (
    CandidateProfile,
    Certificate,
    Experience,
    Hackathon,
    Project,
)

revision: str = "0002_seed_ground_truth"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _load_manifest() -> dict:
    manifest_path = Path(__file__).resolve().parents[3] / "content" / "portfolio_data.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def upgrade() -> None:
    conn = op.get_bind()
    data = _load_manifest()

    # 1. Upsert Candidate Profile (Singleton)
    profile = data["candidate_profile"]
    profile_stmt = pg_insert(CandidateProfile).values(**profile)
    profile_stmt = profile_stmt.on_conflict_do_update(
        index_elements=["singleton_key"],
        set_={
            "full_name": profile_stmt.excluded.full_name,
            "display_name": profile_stmt.excluded.display_name,
            "headline": profile_stmt.excluded.headline,
            "subheadline": profile_stmt.excluded.subheadline,
            "location": profile_stmt.excluded.location,
            "education_degree": profile_stmt.excluded.education_degree,
            "education_institution": profile_stmt.excluded.education_institution,
            "graduation_year": profile_stmt.excluded.graduation_year,
            "github_username": profile_stmt.excluded.github_username,
            "github_url": profile_stmt.excluded.github_url,
            "linkedin_url": profile_stmt.excluded.linkedin_url,
            "email_masked": profile_stmt.excluded.email_masked,
            "phone_masked": profile_stmt.excluded.phone_masked,
            "email_cleartext": profile_stmt.excluded.email_cleartext,
            "phone_cleartext": profile_stmt.excluded.phone_cleartext,
            "resume_pdf_url": profile_stmt.excluded.resume_pdf_url,
            "availability_badge": profile_stmt.excluded.availability_badge,
            "hero_pillars": profile_stmt.excluded.hero_pillars,
            "hero_3d_config": profile_stmt.excluded.hero_3d_config,
            "updated_at": sa.func.now(),
        },
    )
    conn.execute(profile_stmt)

    # 2. Upsert Flagship Projects
    project_id_by_slug: dict[str, object] = {}
    for proj in data["projects"]:
        proj_stmt = pg_insert(Project).values(**proj)
        proj_stmt = proj_stmt.on_conflict_do_update(
            index_elements=["slug"],
            set_={
                "title": proj_stmt.excluded.title,
                "tagline": proj_stmt.excluded.tagline,
                "category": proj_stmt.excluded.category,
                "summary": proj_stmt.excluded.summary,
                "architecture_md": proj_stmt.excluded.architecture_md,
                "ai_explainer": proj_stmt.excluded.ai_explainer,
                "tech_stack": proj_stmt.excluded.tech_stack,
                "security_highlights": proj_stmt.excluded.security_highlights,
                "metrics": proj_stmt.excluded.metrics,
                "github_url": proj_stmt.excluded.github_url,
                "live_url": proj_stmt.excluded.live_url,
                "primary_language": proj_stmt.excluded.primary_language,
                "is_flagship": proj_stmt.excluded.is_flagship,
                "is_featured": proj_stmt.excluded.is_featured,
                "is_auto_synced": proj_stmt.excluded.is_auto_synced,
                "display_order": proj_stmt.excluded.display_order,
                "model_3d_config": proj_stmt.excluded.model_3d_config,
                "updated_at": sa.func.now(),
            },
        ).returning(Project.id, Project.slug)
        row = conn.execute(proj_stmt).one()
        project_id_by_slug[row.slug] = row.id

    # 3. Upsert Experiences
    for exp in data["experiences"]:
        exp_payload = {
            **exp,
            "start_date": date.fromisoformat(exp["start_date"]),
            "end_date": date.fromisoformat(exp["end_date"]) if exp.get("end_date") else None,
        }
        exp_stmt = pg_insert(Experience).values(**exp_payload)
        exp_stmt = exp_stmt.on_conflict_do_update(
            index_elements=["slug"],
            set_={
                "role": exp_stmt.excluded.role,
                "organization": exp_stmt.excluded.organization,
                "organization_url": exp_stmt.excluded.organization_url,
                "location": exp_stmt.excluded.location,
                "employment_type": exp_stmt.excluded.employment_type,
                "start_date": exp_stmt.excluded.start_date,
                "end_date": exp_stmt.excluded.end_date,
                "is_current": exp_stmt.excluded.is_current,
                "summary": exp_stmt.excluded.summary,
                "highlights": exp_stmt.excluded.highlights,
                "metrics": exp_stmt.excluded.metrics,
                "tech_stack": exp_stmt.excluded.tech_stack,
                "spline_node_config": exp_stmt.excluded.spline_node_config,
                "display_order": exp_stmt.excluded.display_order,
                "updated_at": sa.func.now(),
            },
        )
        conn.execute(exp_stmt)

    # 4. Upsert Hackathons (linking project_id when project_slug is present)
    for hack in data["hackathons"]:
        hack_copy = dict(hack)
        project_slug = hack_copy.pop("project_slug", None)
        hack_payload = {
            **hack_copy,
            "project_id": project_id_by_slug.get(project_slug) if project_slug else None,
            "event_date": date.fromisoformat(hack_copy["event_date"]),
        }
        hack_stmt = pg_insert(Hackathon).values(**hack_payload)
        hack_stmt = hack_stmt.on_conflict_do_update(
            index_elements=["slug"],
            set_={
                "event_name": hack_stmt.excluded.event_name,
                "organizer": hack_stmt.excluded.organizer,
                "project_title": hack_stmt.excluded.project_title,
                "project_id": hack_stmt.excluded.project_id,
                "award_status": hack_stmt.excluded.award_status,
                "team_name": hack_stmt.excluded.team_name,
                "role": hack_stmt.excluded.role,
                "team_members": hack_stmt.excluded.team_members,
                "event_date": hack_stmt.excluded.event_date,
                "problem_statement": hack_stmt.excluded.problem_statement,
                "architecture_summary": hack_stmt.excluded.architecture_summary,
                "tech_stack": hack_stmt.excluded.tech_stack,
                "outcomes": hack_stmt.excluded.outcomes,
                "github_url": hack_stmt.excluded.github_url,
                "live_url": hack_stmt.excluded.live_url,
                "proof_url": hack_stmt.excluded.proof_url,
                "model_3d_config": hack_stmt.excluded.model_3d_config,
                "display_order": hack_stmt.excluded.display_order,
                "updated_at": sa.func.now(),
            },
        )
        conn.execute(hack_stmt)

    # 5. Upsert Certificates
    for cert in data["certificates"]:
        cert_payload = {
            **cert,
            "issue_date": date.fromisoformat(cert["issue_date"]),
        }
        cert_stmt = pg_insert(Certificate).values(**cert_payload)
        cert_stmt = cert_stmt.on_conflict_do_update(
            index_elements=["slug"],
            set_={
                "title": cert_stmt.excluded.title,
                "issuer": cert_stmt.excluded.issuer,
                "category": cert_stmt.excluded.category,
                "issue_date": cert_stmt.excluded.issue_date,
                "credential_id": cert_stmt.excluded.credential_id,
                "verify_url": cert_stmt.excluded.verify_url,
                "certificate_asset_url": cert_stmt.excluded.certificate_asset_url,
                "skills_covered": cert_stmt.excluded.skills_covered,
                "summary": cert_stmt.excluded.summary,
                "badge_3d_config": cert_stmt.excluded.badge_3d_config,
                "is_featured": cert_stmt.excluded.is_featured,
                "display_order": cert_stmt.excluded.display_order,
                "updated_at": sa.func.now(),
            },
        )
        conn.execute(cert_stmt)


def downgrade() -> None:
    conn = op.get_bind()
    data = _load_manifest()
    conn.execute(
        sa.delete(Certificate).where(
            Certificate.slug.in_([c["slug"] for c in data["certificates"]])
        )
    )
    conn.execute(
        sa.delete(Hackathon).where(Hackathon.slug.in_([h["slug"] for h in data["hackathons"]]))
    )
    conn.execute(
        sa.delete(Experience).where(Experience.slug.in_([e["slug"] for e in data["experiences"]]))
    )
    conn.execute(sa.delete(Project).where(Project.slug.in_([p["slug"] for p in data["projects"]])))
    conn.execute(
        sa.delete(CandidateProfile).where(
            CandidateProfile.singleton_key == data["candidate_profile"]["singleton_key"]
        )
    )

