import asyncio
import hashlib
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.portfolio import (
    CandidateProfile,
    Certificate,
    Experience,
    Hackathon,
    PortfolioEmbedding,
    Project,
)
from app.services.repo_explainer import compute_embedding_768


async def upsert_record_embedding(
    session: AsyncSession,
    *,
    source_type: str,
    source_id: uuid.UUID,
    source_slug: str,
    title: str,
    chunk_text: str,
    metadata_json: dict[str, Any],
    chunk_index: int = 0,
) -> bool:
    """Upsert a 768-dim embedding only when content_hash is new or changed."""
    content_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
    existing_hash = (
        await session.execute(
            select(PortfolioEmbedding.content_hash).where(
                PortfolioEmbedding.source_type == source_type,
                PortfolioEmbedding.source_id == source_id,
                PortfolioEmbedding.chunk_index == chunk_index,
            )
        )
    ).scalar_one_or_none()

    if existing_hash == content_hash:
        return False

    vector = await compute_embedding_768(chunk_text)
    stmt = pg_insert(PortfolioEmbedding).values(
        source_type=source_type,
        source_id=source_id,
        source_slug=source_slug,
        title=title[:200],
        chunk_index=chunk_index,
        chunk_text=chunk_text,
        metadata_json=metadata_json,
        content_hash=content_hash,
        embedding=vector,
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_portfolio_embeddings_source_chunk",
        set_={
            "source_slug": stmt.excluded.source_slug,
            "title": stmt.excluded.title,
            "chunk_text": stmt.excluded.chunk_text,
            "metadata_json": stmt.excluded.metadata_json,
            "content_hash": stmt.excluded.content_hash,
            "embedding": stmt.excluded.embedding,
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)
    return True


async def seed_all_embeddings(session: AsyncSession) -> dict[str, int]:
    """Index all seeded portfolio entities into portfolio_embeddings."""
    updated = 0
    skipped = 0

    profile = (
        await session.execute(
            select(CandidateProfile).where(CandidateProfile.singleton_key == "SHREYAS_REDDY")
        )
    ).scalar_one_or_none()
    if profile:
        text = (
            f"{profile.full_name} ({profile.display_name}). {profile.headline}. "
            f"{profile.subheadline}. Education: {profile.education_degree} at "
            f"{profile.education_institution} ({profile.graduation_year}), {profile.location}."
        )
        changed = await upsert_record_embedding(
            session,
            source_type="profile",
            source_id=profile.id,
            source_slug="shreyas-reddy",
            title=profile.full_name,
            chunk_text=text,
            metadata_json={"location": profile.location, "graduation_year": profile.graduation_year},
        )
        updated += int(changed)
        skipped += int(not changed)

    projects = (await session.execute(select(Project).where(Project.is_archived.is_(False)))).scalars().all()
    for p in projects:
        stack = ", ".join(p.tech_stack or [])
        highlights = " ".join(p.security_highlights or [])
        text = f"Project {p.title}: {p.tagline}. Category: {p.category}. {p.summary} Tech Stack: {stack}. {highlights}"
        changed = await upsert_record_embedding(
            session,
            source_type="project",
            source_id=p.id,
            source_slug=p.slug,
            title=p.title,
            chunk_text=text,
            metadata_json={"category": p.category, "is_flagship": p.is_flagship},
        )
        updated += int(changed)
        skipped += int(not changed)

    experiences = (await session.execute(select(Experience))).scalars().all()
    for e in experiences:
        highlights = " ".join(e.highlights or [])
        text = (
            f"Experience: {e.role} at {e.organization} ({e.start_date} to {e.end_date or 'Present'}). "
            f"{e.summary} {highlights}"
        )
        changed = await upsert_record_embedding(
            session,
            source_type="experience",
            source_id=e.id,
            source_slug=e.slug,
            title=f"{e.role} — {e.organization}",
            chunk_text=text,
            metadata_json={"organization": e.organization, "employment_type": e.employment_type},
        )
        updated += int(changed)
        skipped += int(not changed)

    hackathons = (await session.execute(select(Hackathon))).scalars().all()
    for h in hackathons:
        outcomes = " ".join(h.outcomes or [])
        text = (
            f"Hackathon {h.event_name} ({h.award_status}): {h.project_title}. Role: {h.role}. "
            f"Problem: {h.problem_statement} Architecture: {h.architecture_summary} {outcomes}"
        )
        changed = await upsert_record_embedding(
            session,
            source_type="hackathon",
            source_id=h.id,
            source_slug=h.slug,
            title=f"{h.event_name}: {h.project_title}",
            chunk_text=text,
            metadata_json={"event_name": h.event_name, "team_name": h.team_name},
        )
        updated += int(changed)
        skipped += int(not changed)

    certificates = (await session.execute(select(Certificate))).scalars().all()
    for c in certificates:
        skills = ", ".join(c.skills_covered or [])
        text = (
            f"Certificate: {c.title} issued by {c.issuer} ({c.category}). "
            f"{c.summary} Skills: {skills}."
        )
        changed = await upsert_record_embedding(
            session,
            source_type="certificate",
            source_id=c.id,
            source_slug=c.slug,
            title=c.title,
            chunk_text=text,
            metadata_json={"issuer": c.issuer, "category": c.category},
        )
        updated += int(changed)
        skipped += int(not changed)

    await session.commit()
    return {"updated": updated, "skipped": skipped}


async def _main() -> None:
    async with AsyncSessionLocal() as session:
        result = await seed_all_embeddings(session)
        print(f"seed_embeddings complete: updated={result['updated']}, skipped={result['skipped']}")


if __name__ == "__main__":
    asyncio.run(_main())

