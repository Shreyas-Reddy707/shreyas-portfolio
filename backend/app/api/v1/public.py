from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis_guard import (
    check_rate_limit,
    get_cached_json,
    get_redis,
    set_cached_json,
)
from app.core.security import extract_client_ip, hash_client_ip, verify_turnstile_token
from app.models.portfolio import (
    CandidateProfile,
    Certificate,
    Experience,
    Hackathon,
    Project,
)
from app.schemas.portfolio import (
    CandidateProfilePublic,
    CertificatePublic,
    ContactRevealRequest,
    ContactRevealResponse,
    ExperiencePublic,
    GitHubProfileManifestResponse,
    HackathonPublic,
    HealthResponse,
    PortfolioBundleResponse,
    ProjectPublic,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    """Verify live connectivity to Postgres, pgvector, and Redis."""
    ip_hash = hash_client_ip(request)
    await check_rate_limit("health", ip_hash, limit=120, window_seconds=60)

    pg_ok = False
    pgvector_ok = False
    redis_ok = False

    try:
        await db.execute(text("SELECT 1"))
        pg_ok = True
        ext = await db.execute(
            text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        )
        pgvector_ok = ext.scalar_one_or_none() is not None
    except Exception:
        pg_ok = False

    try:
        redis_client = await get_redis()
        redis_ok = bool(await redis_client.ping())
    except Exception:
        redis_ok = False

    return HealthResponse(
        status="ok" if (pg_ok and redis_ok and pgvector_ok) else "degraded",
        environment=settings.APP_ENV,
        postgres_connected=pg_ok,
        redis_connected=redis_ok,
        pgvector_enabled=pgvector_ok,
        timestamp=datetime.now(UTC),
    )


@router.get("/public/portfolio", response_model=PortfolioBundleResponse)
async def get_public_portfolio(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> PortfolioBundleResponse:
    """Return full portfolio bundle from Redis cache or PostgreSQL (zero cleartext PII)."""
    ip_hash = hash_client_ip(request)
    await check_rate_limit("public_portfolio", ip_hash, limit=60, window_seconds=60)

    cache_key = "cache:public:portfolio:v1"
    cached = await get_cached_json(cache_key)
    if cached is not None:
        return PortfolioBundleResponse.model_validate(cached)

    profile_row = (
        await db.execute(
            select(CandidateProfile).where(CandidateProfile.singleton_key == "SHREYAS_REDDY")
        )
    ).scalar_one_or_none()
    if profile_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "PROFILE_NOT_FOUND", "message": "Candidate profile not seeded."},
        )

    projects = (
        await db.execute(
            select(Project)
            .where(Project.is_archived.is_(False))
            .order_by(
                Project.is_flagship.desc(),
                Project.is_featured.desc(),
                Project.display_order.asc(),
                Project.last_pushed_at.desc(),
            )
        )
    ).scalars().all()

    experiences = (
        await db.execute(
            select(Experience).order_by(
                Experience.display_order.asc(), Experience.start_date.desc()
            )
        )
    ).scalars().all()

    hackathons = (
        await db.execute(
            select(Hackathon).order_by(
                Hackathon.display_order.asc(), Hackathon.event_date.desc()
            )
        )
    ).scalars().all()

    certificates = (
        await db.execute(
            select(Certificate).order_by(
                Certificate.display_order.asc(), Certificate.issue_date.desc()
            )
        )
    ).scalars().all()

    flagship = [ProjectPublic.model_validate(p) for p in projects if p.is_flagship]
    auto_synced = [ProjectPublic.model_validate(p) for p in projects if not p.is_flagship]

    bundle = PortfolioBundleResponse(
        profile=CandidateProfilePublic.model_validate(profile_row),
        flagship_projects=flagship,
        auto_synced_repos=auto_synced,
        experiences=[ExperiencePublic.model_validate(e) for e in experiences],
        hackathons=[HackathonPublic.model_validate(h) for h in hackathons],
        certificates=[CertificatePublic.model_validate(c) for c in certificates],
        last_synced_at=profile_row.last_github_sync_at or datetime.now(UTC),
    )

    await set_cached_json(cache_key, bundle.model_dump(mode="json"), ttl_seconds=3600)
    return bundle


@router.get("/public/projects/{slug}", response_model=ProjectPublic)
async def get_public_project_by_slug(
    request: Request,
    slug: str = Path(..., pattern=r"^[a-z0-9-]{2,120}$"),
    db: AsyncSession = Depends(get_db),
) -> ProjectPublic:
    """Fetch a single project and its pre-computed AI Repo Explainer by slug."""
    ip_hash = hash_client_ip(request)
    await check_rate_limit("public_project_detail", ip_hash, limit=60, window_seconds=60)

    project = (
        await db.execute(
            select(Project).where(Project.slug == slug, Project.is_archived.is_(False))
        )
    ).scalar_one_or_none()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "PROJECT_NOT_FOUND", "message": f"Project '{slug}' not found."},
        )
    return ProjectPublic.model_validate(project)


@router.get("/public/manifest", response_model=GitHubProfileManifestResponse)
async def get_github_profile_manifest(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> GitHubProfileManifestResponse:
    """Expose deterministic JSON & Markdown manifest for GitHub Profile README sync."""
    ip_hash = hash_client_ip(request)
    await check_rate_limit("public_manifest", ip_hash, limit=30, window_seconds=60)

    cache_key = "cache:public:manifest:v1"
    cached = await get_cached_json(cache_key)
    if cached is not None:
        return GitHubProfileManifestResponse.model_validate(cached)

    profile = (
        await db.execute(
            select(CandidateProfile).where(CandidateProfile.singleton_key == "SHREYAS_REDDY")
        )
    ).scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "PROFILE_NOT_FOUND", "message": "Candidate profile not seeded."},
        )

    projects = (
        await db.execute(
            select(Project)
            .where(Project.is_archived.is_(False))
            .order_by(Project.display_order.asc(), Project.last_pushed_at.desc())
        )
    ).scalars().all()
    hackathons = (
        await db.execute(select(Hackathon).order_by(Hackathon.display_order.asc()))
    ).scalars().all()
    certificates = (
        await db.execute(select(Certificate).order_by(Certificate.display_order.asc()))
    ).scalars().all()

    flagship_list = [
        {
            "title": p.title,
            "tagline": p.tagline,
            "tech_stack": p.tech_stack[:5],
            "github_url": p.github_url,
        }
        for p in projects
        if p.is_flagship
    ]
    auto_list = [
        {
            "title": p.title,
            "tagline": p.tagline,
            "primary_language": p.primary_language,
            "stars_count": p.stars_count,
            "github_url": p.github_url,
        }
        for p in projects
        if not p.is_flagship
    ][:6]

    lines = [
        "### Flagship Engineering Systems",
        "| System | Architecture & Impact | Stack |",
        "| :--- | :--- | :--- |",
    ]
    for fp in flagship_list:
        stack_str = ", ".join(fp["tech_stack"])
        link = f"[{fp['title']}]({fp['github_url']})" if fp["github_url"] else fp["title"]
        lines.append(f"| **{link}** | {fp['tagline']} | `{stack_str}` |")

    manifest = GitHubProfileManifestResponse(
        generated_at=datetime.now(UTC),
        candidate={
            "name": profile.full_name,
            "headline": profile.headline,
            "github_url": profile.github_url,
            "linkedin_url": profile.linkedin_url,
        },
        flagship_projects=flagship_list,
        recent_auto_synced_repos=auto_list,
        hackathons=[
            {"event_name": h.event_name, "project_title": h.project_title, "role": h.role}
            for h in hackathons
        ],
        certificates=[
            {"title": c.title, "issuer": c.issuer, "category": c.category}
            for c in certificates
        ],
        markdown_block="\n".join(lines),
    )

    await set_cached_json(cache_key, manifest.model_dump(mode="json"), ttl_seconds=1800)
    return manifest


@router.post("/public/contact-reveal", response_model=ContactRevealResponse)
async def reveal_contact_info(
    request: Request,
    payload: ContactRevealRequest,
    db: AsyncSession = Depends(get_db),
) -> ContactRevealResponse:
    """Verify Cloudflare Turnstile token before revealing cleartext email and phone."""
    ip_hash = hash_client_ip(request)
    await check_rate_limit("contact_reveal", ip_hash, limit=10, window_seconds=600)

    await verify_turnstile_token(payload.turnstile_token, extract_client_ip(request))

    profile = (
        await db.execute(
            select(CandidateProfile).where(CandidateProfile.singleton_key == "SHREYAS_REDDY")
        )
    ).scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "PROFILE_NOT_FOUND", "message": "Candidate profile not seeded."},
        )

    phone_digits = profile.phone_cleartext.replace(" ", "").replace("-", "")
    return ContactRevealResponse(
        email=profile.email_cleartext,
        phone=profile.phone_cleartext,
        mailto_uri=f"mailto:{profile.email_cleartext}",
        tel_uri=f"tel:{phone_digits}",
        linkedin_url=profile.linkedin_url,
    )

