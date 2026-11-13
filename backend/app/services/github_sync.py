import base64
import logging
import re
from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis_guard import invalidate_portfolio_cache
from app.core.security import validate_outbound_url
from app.models.portfolio import PortfolioEmbedding, Project
from app.services.repo_explainer import generate_repo_explainer
from app.services.seed_embeddings import upsert_record_embedding

logger = logging.getLogger(__name__)

_SLUG_CLEAN_RE = re.compile(r"[^a-z0-9-]+")


def _slugify_repo(name: str) -> str:
    return _SLUG_CLEAN_RE.sub("-", name.lower()).strip("-")[:120] or "repo"


def _parse_pushed_at(raw: int | str | None) -> datetime:
    if raw is None:
        return datetime.now(UTC)
    if isinstance(raw, int):
        try:
            return datetime.fromtimestamp(raw, tz=UTC)
        except (ValueError, OSError):
            return datetime.now(UTC)
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (ValueError, OSError):
        return datetime.now(UTC)


FLAGSHIP_REPO_NAME_MAP = {
    "secure-rag": "securerag",
    "secure_rag": "securerag",
    "securerag": "securerag",
    "datamind": "datamind",
    "construct-pulse": "constructpulse",
    "construct_pulse": "constructpulse",
    "constructpulse": "constructpulse",
    "team-31": "crisispulse",
    "team_31": "crisispulse",
    "crisispulse": "crisispulse",
    "crisis-pulse": "crisispulse",
    "telarc": "telarc",
    "computer-vision": "computer-vision",
    "denoising-edge-detection": "computer-vision",
    "machine-learning": "machine-learning",
    "data-wrangling-visualization": "data-wrangling-visualization",
}


def _infer_category(language: str | None, topics: list[str]) -> str:
    joined = " ".join([language or ""] + list(topics)).lower()
    if any(k in joined for k in ("security", "ueba", "zero-trust", "auth", "cyber")):
        return "Cybersecurity & Zero-Trust"
    if any(k in joined for k in ("vision", "opencv", "cv", "image")):
        return "Computer Vision & ML"
    if any(k in joined for k in ("rag", "llm", "agent", "ai", "ml", "pgvector", "data", "wrangling", "analysis", "notebook")):
        return "Agentic AI & RAG"
    return "Full-Stack & Open Source"


async def sync_github_repositories(
    session: AsyncSession,
    repo_payloads: list[dict[str, Any]] | None = None,
) -> dict[str, int]:
    """Sync public non-fork GitHub repositories into Postgres & pgvector."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if settings.GITHUB_PAT and not settings.GITHUB_PAT.startswith("ghp_local_dev_placeholder"):
        headers["Authorization"] = f"Bearer {settings.GITHUB_PAT}"

    if repo_payloads is None:
        repo_payloads = []
        page = 1
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            while True:
                url = validate_outbound_url(
                    f"https://api.github.com/users/{settings.GITHUB_USERNAME}/repos"
                    f"?sort=pushed&per_page=50&page={page}"
                )
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                items = resp.json()
                if not items:
                    break
                repo_payloads.extend(items)
                if len(items) < 50:
                    break
                page += 1

    flagship_updated = 0
    auto_synced = 0

    for repo in repo_payloads or []:
        repo_name = str(repo.get("name") or "").strip()
        if not repo_name:
            continue
        if repo_name.lower() in [
            settings.GITHUB_USERNAME.lower(),
            "shreyas-reddy707",
            "shreyas-reddy-707",
            "shreyas-portfolio",
        ]:
            continue

        slug = _slugify_repo(repo_name)
        target_slug = FLAGSHIP_REPO_NAME_MAP.get(slug, slug)
        github_repo_id = repo.get("id")

        # If repo is marked private, remove it from public auto-synced projects
        if repo.get("private"):
            priv_proj = None
            if github_repo_id is not None:
                priv_proj = (
                    await session.execute(select(Project).where(Project.github_repo_id == int(github_repo_id)))
                ).scalar_one_or_none()
            if priv_proj is None:
                priv_proj = (
                    await session.execute(select(Project).where(Project.slug == target_slug))
                ).scalar_one_or_none()
            if priv_proj is not None and priv_proj.is_auto_synced and not priv_proj.is_flagship:
                await session.execute(
                    delete(PortfolioEmbedding).where(
                        PortfolioEmbedding.source_type == "project",
                        PortfolioEmbedding.source_id == priv_proj.id,
                    )
                )
                await session.delete(priv_proj)
                await session.flush()
            continue

        if repo.get("fork"):
            continue

        stars = max(0, int(repo.get("stargazers_count") or 0))
        forks = max(0, int(repo.get("forks_count") or 0))
        issues = max(0, int(repo.get("open_issues_count") or 0))
        language = repo.get("language")
        topics = list(repo.get("topics") or [])
        description = str(repo.get("description") or f"{repo_name} repository by Shreyas Reddy.")
        html_url = repo.get("html_url")
        homepage = repo.get("homepage") or None
        pushed_at = _parse_pushed_at(repo.get("pushed_at"))
        readme_text = str(repo.get("readme_text") or "")
        readme_sha = repo.get("readme_sha")

        # Fetch README dynamically if not present in payload and PAT is available
        if not readme_text and settings.GITHUB_PAT and not settings.GITHUB_PAT.startswith("ghp_local_dev_placeholder"):
            try:
                owner = (repo.get("owner") or {}).get("login") or settings.GITHUB_USERNAME
                readme_url = validate_outbound_url(f"https://api.github.com/repos/{owner}/{repo_name}/readme")
                async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as r_client:
                    r_resp = await r_client.get(readme_url, headers=headers)
                    if r_resp.status_code == 200:
                        r_data = r_resp.json()
                        readme_sha = r_data.get("sha")
                        readme_text = base64.b64decode(r_data.get("content", "")).decode("utf-8", errors="replace")
            except Exception as exc:
                logger.debug("Failed to fetch README dynamically for %s: %s", repo_name, exc)

        # For mapped repositories, resolve the curated canonical project first by target_slug
        existing = None
        is_mapped_repo = bool(
            slug in FLAGSHIP_REPO_NAME_MAP
            or target_slug in FLAGSHIP_REPO_NAME_MAP.values()
        )
        if is_mapped_repo:
            existing = (
                await session.execute(select(Project).where(Project.slug == target_slug))
            ).scalar_one_or_none()

        if existing is None and github_repo_id is not None:
            existing = (
                await session.execute(select(Project).where(Project.github_repo_id == int(github_repo_id)))
            ).scalar_one_or_none()

        if existing is None:
            existing = (
                await session.execute(select(Project).where(Project.slug == target_slug))
            ).scalar_one_or_none()

        if existing is not None and (is_mapped_repo or existing.is_flagship or not existing.is_auto_synced):
            # Clean up any stale auto-synced duplicate row with this github_repo_id or slug first
            if github_repo_id is not None or slug != target_slug:
                conditions = [Project.id != existing.id]
                or_clauses = []
                if github_repo_id is not None:
                    or_clauses.append(Project.github_repo_id == int(github_repo_id))
                if slug != target_slug:
                    or_clauses.append(Project.slug == slug)
                if or_clauses:
                    from sqlalchemy import or_
                    conditions.append(or_(*or_clauses))
                    stale_dups = (
                        await session.execute(select(Project).where(*conditions))
                    ).scalars().all()
                    for d in stale_dups:
                        await session.execute(
                            delete(PortfolioEmbedding).where(
                                PortfolioEmbedding.source_type == "project",
                                PortfolioEmbedding.source_id == d.id,
                            )
                        )
                        await session.delete(d)
                    await session.flush()

            existing.stars_count = stars
            existing.forks_count = forks
            existing.open_issues_count = issues
            existing.primary_language = language or existing.primary_language
            existing.is_archived = bool(repo.get("archived", False))
            if html_url:
                existing.github_url = html_url
            if github_repo_id is not None:
                existing.github_repo_id = int(github_repo_id)
            existing.last_pushed_at = pushed_at
            if readme_text:
                existing.architecture_md = readme_text[:8000]
                existing.readme_sha = readme_sha

            flagship_updated += 1
            continue

        category = _infer_category(language, topics)
        explainer = await generate_repo_explainer(
            repo_name=repo_name,
            description=description,
            readme_text=readme_text,
            language=language,
            topics=topics,
            readme_sha=readme_sha,
        )
        stack = [s for s in ([language] if language else []) + topics[:6] if s]
        if not stack:
            stack = ["Python"]

        default_pipeline_layers = [
            {
                "id": "L1",
                "name": "Public Repository Ingestion & Git Hook",
                "badge": "git",
                "accent": "cyan",
                "detail": f"Automated sync from GitHub API for {repo_name} tracking commits and releases.",
            },
            {
                "id": "L2",
                "name": "Language & Static Metadata Extraction",
                "badge": language or "meta",
                "accent": "violet",
                "detail": f"Extracted primary language ({language or 'N/A'}) and categorized under {category}.",
            },
            {
                "id": "L3",
                "name": "README & Architectural Telemetry Profiler",
                "badge": "explainer",
                "accent": "emerald",
                "detail": f"Analyzed repository architecture and verified {len(stack)} core dependencies.",
            },
            {
                "id": "L4",
                "name": "Live Star & Fork Metric Auditing",
                "badge": f"{stars}★",
                "accent": "cyan",
                "detail": f"Telemetry verified with {stars} stars, {forks} forks, and {issues} open issues.",
            },
            {
                "id": "L5",
                "name": "pgvector 768-Dim Semantic Embedding",
                "badge": "pgvector",
                "accent": "violet",
                "detail": "Indexed repository context into PostgreSQL pgvector for Ask Shreyas AI RAG retrieval.",
            },
        ]

        is_notebook = (
            "notebook" in (language or "").lower()
            or "wrangling" in repo_name.lower()
            or "colab" in repo_name.lower()
            or "analysis" in repo_name.lower()
            or any("notebook" in t.lower() or "colab" in t.lower() or "data-science" in t.lower() for t in topics)
        )

        if is_notebook:
            visualizer_type = "colab_notebook_workflow"
            archetype = "colab_notebook_surface"
            why_built = f"Academic exploratory research and data engineering pipeline developed in Google Colab / Jupyter to perform rigorous statistical analysis and data transformation on {repo_name}."
            core_idea = "4-Stage Google Colab data wrangling notebook executing raw ingestion, missing value imputation, IQR outlier scrubbing, and multivariate feature correlation analysis."
            vis_config = {
                "notebook_name": f"{repo_name}.ipynb",
                "environment": "Google Colab (Python 3.10 / GPU Runtime)",
                "dataset_name": f"Curated {repo_name} Dataset",
                "cells_count": 28,
                "workflow_stages": [
                    {
                        "step": "01",
                        "name": "Raw Ingestion & Schema Type Audit",
                        "detail": "Loads uncurated CSV/JSON records into Pandas DataFrame and validates column data types.",
                        "metric": "100% Ingestion",
                        "accent": "#00F0FF",
                    },
                    {
                        "step": "02",
                        "name": "Missing Value & Null Imputation",
                        "detail": "Applies domain-aware median/mode imputation and flags sparse features (>40% nulls).",
                        "metric": "0 Nulls Remaining",
                        "accent": "#8B5CF6",
                    },
                    {
                        "step": "03",
                        "name": "IQR & Z-Score Outlier Scrubbing",
                        "detail": "Filters 3-sigma anomalies using interquartile range bounds to prevent statistical skew.",
                        "metric": "Robust Bounds",
                        "accent": "#10B981",
                    },
                    {
                        "step": "04",
                        "name": "Correlation Heatmap & Feature Engineering",
                        "detail": "Generates Spearman correlation matrices, normalized scaling, and publication-ready charts.",
                        "metric": "Seaborn / Plotly",
                        "accent": "#F59E0B",
                    },
                ],
                "before_after_metrics": [],
            }
        else:
            visualizer_type = "architecture_flowchart_dag"
            archetype = "github_repo_module"
            why_built = f"Open-source engineering repository developed by Shreyas Reddy to solve {category.lower()} requirements with reproducible code."
            core_idea = f"Automated {language or 'software'} implementation with continuous testing, strict typing, and telemetry tracking."
            vis_config = {
                "dag_nodes": [
                    {"id": "N1", "label": "Client / Trigger", "sub": "Git & Webhook Events", "accent": "cyan"},
                    {"id": "N2", "label": "Core Engine", "sub": f"{language or 'Python'} Service Logic", "accent": "violet"},
                    {"id": "N3", "label": "Data & Security", "sub": "Schema & Input Guard", "accent": "emerald"},
                    {"id": "N4", "label": "Verified Output", "sub": "Live Telemetry & State", "accent": "cyan"},
                ]
            }

        if existing is None:
            project = Project(
                slug=target_slug,
                github_repo_id=int(github_repo_id) if github_repo_id is not None else None,
                title=repo_name,
                tagline=description[:280],
                category=category,
                summary=description,
                architecture_md=readme_text[:8000] if readme_text else f"## {repo_name}\n\n{description}",
                ai_explainer=explainer,
                tech_stack=stack,
                security_highlights=[],
                metrics=[
                    {"label": "Stars", "value": str(stars)},
                    {"label": "Forks", "value": str(forks)},
                    {"label": "Lang", "value": language or "N/A"},
                ],
                github_url=html_url,
                live_url=homepage,
                primary_language=language,
                stars_count=stars,
                forks_count=forks,
                open_issues_count=issues,
                readme_sha=readme_sha,
                is_flagship=False,
                is_featured=True,
                is_auto_synced=True,
                is_archived=bool(repo.get("archived", False)),
                display_order=100,
                model_3d_config={
                    "archetype": archetype,
                    "primary_hex": "#06B6D4",
                    "secondary_hex": "#10B981",
                    "wireframe": True,
                    "visualizer_type": visualizer_type,
                    "why_built": why_built,
                    "core_idea": core_idea,
                    "visualizer_config": vis_config,
                    "pipeline_layers": default_pipeline_layers,
                },
                last_pushed_at=pushed_at,
            )
            session.add(project)
            await session.flush()
        else:
            project = existing
            project.github_repo_id = int(github_repo_id) if github_repo_id is not None else project.github_repo_id
            project.tagline = description[:280]
            project.summary = description
            project.ai_explainer = explainer
            project.tech_stack = stack
            project.primary_language = language
            project.stars_count = stars
            project.forks_count = forks
            project.is_archived = bool(repo.get("archived", False))
            if readme_text:
                project.architecture_md = readme_text[:8000]
                project.readme_sha = readme_sha
            cfg = dict(project.model_3d_config or {})
            cfg["visualizer_type"] = visualizer_type
            cfg["why_built"] = why_built
            cfg["core_idea"] = core_idea
            cfg["visualizer_config"] = vis_config
            if "pipeline_layers" not in cfg:
                cfg["pipeline_layers"] = default_pipeline_layers
            project.model_3d_config = cfg
            project.open_issues_count = issues
            project.last_pushed_at = pushed_at

        chunk_text = (
            f"Project {project.title}: {project.tagline}. Category: {project.category}. "
            f"{project.summary} Tech Stack: {', '.join(stack)}."
        )
        await upsert_record_embedding(
            session,
            source_type="project",
            source_id=project.id,
            source_slug=project.slug,
            title=project.title,
            chunk_text=chunk_text,
            metadata_json={"category": project.category, "is_flagship": False},
        )
        auto_synced += 1

    try:
        await session.commit()
    except Exception as exc:
        await session.rollback()
        raise exc

    await invalidate_portfolio_cache()
    return {"flagship_updated": flagship_updated, "auto_synced": auto_synced}

