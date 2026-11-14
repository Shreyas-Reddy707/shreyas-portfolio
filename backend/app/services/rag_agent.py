import logging
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis_guard import consume_ai_tokens
from app.core.security import validate_outbound_url
from app.models.portfolio import (
    CandidateProfile,
    Certificate,
    Experience,
    Hackathon,
    PortfolioEmbedding,
    Project,
)
from app.services.repo_explainer import build_nonce_guarded_prompt, compute_embedding_768

logger = logging.getLogger(__name__)

# In-memory cache for full portfolio context string and entity catalog
_PORTFOLIO_DATA_CACHE: tuple[str, list[dict[str, Any]]] | None = None


def clear_portfolio_data_cache() -> None:
    """Clear the in-memory cached portfolio context and entity catalog."""
    global _PORTFOLIO_DATA_CACHE
    _PORTFOLIO_DATA_CACHE = None


async def build_full_portfolio_context(
    session: AsyncSession,
) -> tuple[str, list[dict[str, Any]]]:
    """Build a comprehensive, structured text summary and complete entity catalog for Shreyas's portfolio."""
    global _PORTFOLIO_DATA_CACHE
    if _PORTFOLIO_DATA_CACHE:
        return _PORTFOLIO_DATA_CACHE

    profile = (await session.execute(select(CandidateProfile))).scalar_one_or_none()
    projects = (
        await session.execute(
            select(Project)
            .where(Project.is_archived.is_(False))
            .order_by(Project.is_flagship.desc(), Project.display_order.asc())
        )
    ).scalars().all()
    experiences = (
        await session.execute(select(Experience).order_by(Experience.display_order.asc()))
    ).scalars().all()
    hackathons = (
        await session.execute(select(Hackathon).order_by(Hackathon.display_order.asc()))
    ).scalars().all()
    certificates = (
        await session.execute(select(Certificate).order_by(Certificate.display_order.asc()))
    ).scalars().all()

    sections: list[str] = []
    catalog: list[dict[str, Any]] = []

    # 1. Profile Overview
    if profile:
        sections.append(
            f"=== CANDIDATE PROFILE ===\n"
            f"Name: {profile.display_name} ({profile.full_name})\n"
            f"Headline: {profile.headline}\n"
            f"Location: {profile.location}\n"
            f"Education: {profile.education_degree} at {profile.education_institution} (Graduating {profile.graduation_year})\n"
            f"Current Availability: {profile.availability_badge}\n"
            f"GitHub: {profile.github_url}\n"
            f"LinkedIn: {profile.linkedin_url}"
        )
        catalog.append({
            "source_type": "profile",
            "slug": "shreyas-reddy",
            "title": f"Candidate: {profile.display_name}",
            "raw_title": profile.display_name,
            "keywords": ["shreyas", "shreyas reddy", "chemakoora", "candidate", "profile"],
            "display_order": 0,
        })

    # 2. Flagships & Colab Labs
    if projects:
        proj_lines = ["=== PROJECTS (5 FLAGSHIPS + 3 GOOGLE COLAB LABS) ==="]
        for p in projects:
            why_built = (p.ai_explainer or {}).get("problem_statement") or p.summary
            core_idea = (
                (p.model_3d_config or {}).get("core_concept")
                or (p.model_3d_config or {}).get("subtitle")
                or p.tagline
            )
            metrics_str = ", ".join(
                f"{m.get('label')}: {m.get('value')}"
                for m in (p.metrics or [])
                if isinstance(m, dict) and m.get("label")
            )
            tech_str = ", ".join(p.tech_stack or [])
            kind = "FLAGSHIP SYSTEM" if p.is_flagship else "GOOGLE COLAB LAB / REPO"

            proj_lines.append(
                f"\n[{kind}] {p.title} ({p.slug})\n"
                f"- Category: {p.category}\n"
                f"- Tagline: {p.tagline}\n"
                f"- Why Built: {why_built}\n"
                f"- Core Idea: {core_idea}\n"
                f"- Tech Stack: {tech_str}\n"
                f"- Key Metrics: {metrics_str or 'Production Prototype'}\n"
                f"- GitHub URL: {p.github_url or 'N/A'}"
            )

            # Build aliases/keywords for citation matching
            kws = [p.title.lower(), p.slug.lower()]
            if p.slug == "securerag":
                kws.extend(["securerag", "secure rag", "zero-trust rag", "zero trust rag", "indirect prompt injection"])
            elif p.slug == "datamind":
                kws.extend(["datamind", "datamind v2", "automl", "duckdb"])
            elif p.slug == "constructpulse":
                kws.extend(["constructpulse", "construction", "jobsite", "logistics"])
            elif p.slug == "crisispulse":
                kws.extend(["crisispulse", "crisis", "disaster", "wikinews", "geospatial"])
            elif p.slug == "telarc":
                kws.extend(["telarc", "telugu archive", "telugu nlp", "multimodal corpus"])
            elif p.slug == "denoising-edge-detection":
                kws.extend(["computer vision", "denoising", "canny", "ssim", "edge detection"])
            elif p.slug == "machine-learning":
                kws.extend(["machine learning", "predictive modeling", "scikit-learn", "roc-auc"])
            elif p.slug == "deep-learning":
                kws.extend(["deep learning", "neural architectures", "cnn", "loss surface"])

            catalog.append({
                "source_type": "project",
                "slug": p.slug,
                "title": f"Project: {p.title}",
                "raw_title": p.title,
                "keywords": kws,
                "display_order": p.display_order,
            })
        sections.append("\n".join(proj_lines))

    # 3. Work Experience & Education Milestones
    if experiences:
        exp_lines = ["=== WORK EXPERIENCE & EDUCATION ==="]
        for exp in experiences:
            highlights_str = "; ".join(exp.highlights or [])
            metrics_str = ", ".join(
                f"{m.get('label')}: {m.get('value')}"
                for m in (exp.metrics or [])
                if isinstance(m, dict) and m.get("label")
            )
            tech_str = ", ".join(exp.tech_stack or [])
            status = "CURRENT ROLE" if exp.is_current else "COMPLETED"

            exp_lines.append(
                f"\n[{status}] {exp.role} at {exp.organization}\n"
                f"- Location & Type: {exp.location} ({exp.employment_type})\n"
                f"- Summary: {exp.summary}\n"
                f"- Key Achievements: {highlights_str}\n"
                f"- Metrics: {metrics_str or 'Engineering Execution'}\n"
                f"- Technologies: {tech_str}"
            )

            exp_kws = [exp.slug.lower(), exp.role.lower(), exp.organization.lower()]
            if "limelite" in exp.slug.lower():
                exp_kws.extend(["limelite", "limelite constructions", "forward deployed", "new zealand", "nz", "rave build"])
            elif "viswam" in exp.slug.lower():
                exp_kws.extend(["viswam", "viswam.ai", "tech lead", "swecha", "intern pod", "telugu corpus"])
            elif "icfai" in exp.slug.lower():
                exp_kws.extend(["icfai", "icfai tech", "b.tech", "cgpa", "education", "degree", "university"])

            catalog.append({
                "source_type": "experience",
                "slug": exp.slug,
                "title": f"Experience: {exp.role} — {exp.organization}",
                "raw_title": f"{exp.role} — {exp.organization}",
                "keywords": exp_kws,
                "display_order": exp.display_order,
            })
        sections.append("\n".join(exp_lines))

    # 4. Hackathons
    if hackathons:
        hack_lines = ["=== HACKATHONS & PROOF-OF-WORK BUILDS ==="]
        for h in hackathons:
            outcomes_str = "; ".join(h.outcomes or [])
            tech_str = ", ".join(h.tech_stack or [])
            hack_lines.append(
                f"\n- Event: {h.event_name} ({h.organizer})\n"
                f"  Project: {h.project_title}\n"
                f"  Award/Status: {h.award_status}\n"
                f"  Role: {h.role} ({h.team_name})\n"
                f"  Architecture: {h.architecture_summary}\n"
                f"  Outcomes: {outcomes_str}\n"
                f"  Tech: {tech_str}"
            )

            hack_kws = [h.slug.lower(), h.event_name.lower(), h.project_title.lower()]
            if "sih" in h.slug.lower():
                hack_kws.extend(["sih", "smart india hackathon", "sih 2025", "ministry of education"])
            elif "devnovate" in h.slug.lower():
                hack_kws.extend(["devnovate", "hack with hyderabad", "hack with hyderabad 3.0"])
            elif "wikiverse" in h.slug.lower():
                hack_kws.extend(["wikiverse", "wiki verse", "iiit hyderabad", "iiit-h"])

            catalog.append({
                "source_type": "hackathon",
                "slug": h.slug,
                "title": f"Hackathon: {h.event_name}",
                "raw_title": h.event_name,
                "keywords": hack_kws,
                "display_order": h.display_order,
            })
        sections.append("\n".join(hack_lines))

    # 5. All 22 Verified Certifications
    if certificates:
        cert_lines = [f"=== VERIFIED CREDENTIALS VAULT ({len(certificates)} CERTIFICATIONS) ==="]
        for c in certificates:
            skills_str = ", ".join(c.skills_covered or [])
            cert_lines.append(
                f"- {c.title} | Issuer: {c.issuer} | Category: {c.category} | Skills: {skills_str}"
            )
            catalog.append({
                "source_type": "certificate",
                "slug": c.slug,
                "title": f"Certificate: {c.title}",
                "raw_title": c.title,
                "keywords": [c.slug.lower(), c.title.lower(), c.issuer.lower()],
                "display_order": c.display_order,
            })
        sections.append("\n".join(cert_lines))

    _PORTFOLIO_DATA_CACHE = ("\n\n".join(sections), catalog)
    return _PORTFOLIO_DATA_CACHE


def detect_query_intent(query: str) -> set[str]:
    """Detect targeted source_type scopes based on query keywords."""
    q = query.lower()
    intents: set[str] = set()

    hackathon_kw = ["hackathon", "hackathons", "sih", "devnovate", "wikiverse", "competition"]
    project_kw = [
        "project", "projects", "repo", "repositories", "built", "flagship",
        "colab", "securerag", "datamind", "constructpulse", "crisispulse",
        "telarc", "denoising", "computer vision", "machine learning", "deep learning"
    ]
    experience_kw = [
        "experience", "work", "intern", "internship", "job", "role",
        "limelite", "viswam", "company", "education", "college",
        "university", "cgpa", "degree"
    ]
    certificate_kw = [
        "certificate", "certificates", "certification", "certifications",
        "credential", "credentials", "azure", "aws", "nvidia", "nasscom",
        "deloitte", "tata", "ibm", "infosys"
    ]

    if any(k in q for k in hackathon_kw):
        intents.add("hackathon")
    if any(k in q for k in project_kw):
        intents.add("project")
    if any(k in q for k in experience_kw):
        intents.add("experience")
    if any(k in q for k in certificate_kw):
        intents.add("certificate")

    if not intents or len(intents) > 2:
        return {"project", "experience", "hackathon", "certificate", "profile"}
    return intents


def resolve_accurate_citations(
    query: str,
    answer_text: str,
    catalog: list[dict[str, Any]],
    vector_rows: list[PortfolioEmbedding],
) -> list[dict[str, str]]:
    """Deterministically select accurate, answer-grounded citations matching query intent."""
    allowed_types = detect_query_intent(query)
    ans_lower = answer_text.lower()
    query_lower = query.lower()

    scored_matches: list[tuple[int, dict[str, Any]]] = []
    seen_slugs: set[str] = set()

    for item in catalog:
        if item["source_type"] not in allowed_types:
            continue

        matched_pos: int | None = None

        # Check for occurrence in answer text (prioritized by appearance order)
        for kw in item["keywords"]:
            pos = ans_lower.find(kw)
            if pos != -1:
                if matched_pos is None or pos < matched_pos:
                    matched_pos = pos

        # If not explicitly in answer, check if query specifically asked for it
        if matched_pos is None:
            for kw in item["keywords"]:
                if kw in query_lower:
                    matched_pos = 900000 + item.get("display_order", 0)
                    break

        if matched_pos is not None and item["slug"] not in seen_slugs:
            seen_slugs.add(item["slug"])
            scored_matches.append((matched_pos, item))

    # Sort primarily by the order entities were discussed in the answer
    scored_matches.sort(key=lambda x: x[0])
    selected = [item for _, item in scored_matches if item["source_type"] in allowed_types]

    # If no matches were found through text scanning, use vector_rows filtered by allowed types
    if not selected:
        for r in vector_rows:
            if r.source_type in allowed_types and r.source_slug not in seen_slugs:
                seen_slugs.add(r.source_slug)
                cat_item = next((c for c in catalog if c["slug"] == r.source_slug), None)
                title = cat_item["title"] if cat_item else f"{r.source_type.title()}: {r.title}"
                selected.append({
                    "source_type": r.source_type,
                    "slug": r.source_slug,
                    "title": title,
                })
                if len(selected) >= 4:
                    break

    return [
        {"source_type": item["source_type"], "slug": item["slug"], "title": item["title"]}
        for item in selected[:4]
    ]


async def _call_groq_api(system_instruction: str, user_payload: str) -> str | None:
    """Call Groq API using llama-3.3-70b-versatile with fallback to available models."""
    if not settings.GROQ_API_KEY:
        return None

    url = validate_outbound_url("https://api.groq.com/openai/v1/chat/completions")
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    models_to_try = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
    ]

    for model_name in models_to_try:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
                resp = await client.post(
                    url,
                    headers=headers,
                    json={
                        "model": model_name,
                        "temperature": 0.2,
                        "max_tokens": 450,
                        "messages": [
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_payload},
                        ],
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    ans = data["choices"][0]["message"]["content"].strip()
                    if ans:
                        logger.info("Groq API successfully generated response via %s", model_name)
                        return ans
                else:
                    logger.warning("Groq (%s) returned HTTP %d: %s", model_name, resp.status_code, resp.text[:180])
        except Exception as exc:
            logger.warning("Groq (%s) call failed: %s", model_name, exc)

    return None


async def _call_gemini_api(system_instruction: str, user_payload: str) -> str | None:
    """Call Google Gemini 2.5 Flash API."""
    if not settings.GEMINI_API_KEY:
        return None

    try:
        url = validate_outbound_url(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        )
        headers = {
            "x-goog-api-key": settings.GEMINI_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": user_payload}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500},
        }

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    ans = parts[0]["text"].strip()
                    if ans:
                        logger.info("Gemini 2.5 Flash successfully generated response.")
                        return ans
            else:
                logger.warning("Gemini API returned HTTP %d: %s", resp.status_code, resp.text[:200])
    except Exception as exc:
        logger.warning("Gemini API call failed: %s", exc)

    return None


async def _call_ollama_api(system_instruction: str, user_payload: str) -> str | None:
    """Call local Ollama if configured in development."""
    try:
        url = validate_outbound_url(f"{settings.OLLAMA_BASE_URL}/api/chat")
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            resp = await client.post(
                url,
                json={
                    "model": "llama3.2",
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_payload},
                    ],
                },
            )
            if resp.status_code == 200:
                ans = resp.json().get("message", {}).get("content", "").strip()
                if ans:
                    return ans
    except Exception as exc:
        logger.debug("Ollama call skipped/failed: %s", exc)

    return None


async def call_llm_with_failover(
    system_instruction: str, user_payload: str
) -> tuple[str | None, str]:
    """Call Groq or Gemini with automatic instant failover.

    Returns (answer_text, provider_used).
    """
    if settings.AI_PROVIDER == "groq":
        provider_sequence = ["groq", "gemini"]
    elif settings.AI_PROVIDER == "gemini":
        provider_sequence = ["gemini", "groq"]
    elif settings.AI_PROVIDER == "ollama":
        provider_sequence = ["ollama", "groq", "gemini"]
    else:
        provider_sequence = ["groq", "gemini"]

    for provider in provider_sequence:
        if provider == "groq" and settings.GROQ_API_KEY:
            ans = await _call_groq_api(system_instruction, user_payload)
            if ans:
                return ans, "groq"
        elif provider == "gemini" and settings.GEMINI_API_KEY:
            ans = await _call_gemini_api(system_instruction, user_payload)
            if ans:
                return ans, "gemini"
        elif provider == "ollama":
            ans = await _call_ollama_api(system_instruction, user_payload)
            if ans:
                return ans, "ollama"

    return None, "fallback"


def build_formatted_fallback(query: str, rows: list[PortfolioEmbedding]) -> str:
    """Construct a clean, point-to-point Markdown bullet response from retrieved chunks."""
    clean_bullets: list[str] = []

    for r in rows:
        chunk = r.chunk_text.strip()
        lines = [line.strip() for line in chunk.split("\n") if line.strip()]
        for line in lines:
            if line.startswith("- ") or line.startswith("• "):
                clean_bullets.append(line)
            elif ":" in line and not line.lower().startswith(("category:", "tech stack:", "order:")):
                parts = line.split(":", 1)
                clean_bullets.append(f"- **{parts[0].strip(' *')}:** {parts[1].strip()}")
        if len(clean_bullets) >= 4:
            break

    if not clean_bullets:
        return f"No matching portfolio records or engineering details found regarding '{query}'."

    bullets_rendered = "\n".join(clean_bullets[:4])
    return (
        f"Here is a point-to-point summary regarding '{query}':\n\n"
        f"{bullets_rendered}"
    )


async def answer_recruiter_query(
    session: AsyncSession,
    query: str,
    category_filter: str | None = None,
) -> dict[str, Any]:
    """Answer a recruiter query via full portfolio context + pgvector similarity + accurate citations."""
    import asyncio

    rows: list[PortfolioEmbedding] = []
    full_context, catalog = await build_full_portfolio_context(session)

    try:
        # Enforce strict shared 10-second total deadline covering embedding and LLM generation
        async with asyncio.timeout(10.0):
            has_embedding_budget = await consume_ai_tokens(50)
            if has_embedding_budget:
                query_vec = await compute_embedding_768(query)
            else:
                from app.services.repo_explainer import _deterministic_offline_embedding_768
                query_vec = _deterministic_offline_embedding_768(query)

            stmt = select(PortfolioEmbedding)
            if category_filter:
                stmt = stmt.where(PortfolioEmbedding.source_type == category_filter)
            stmt = stmt.order_by(PortfolioEmbedding.embedding.cosine_distance(query_vec)).limit(4)

            rows = list((await session.execute(stmt)).scalars().all())

            # Combine master context with the top pgvector specific chunks
            context_chunks = [full_context]
            if rows:
                context_chunks.extend([f"TOP SIMILARITY MATCH ({r.title}):\n{r.chunk_text}" for r in rows])

            system_instruction, user_payload = build_nonce_guarded_prompt(query, context_chunks)
            within_budget = await consume_ai_tokens(400)

            if within_budget:
                answer_text, provider_used = await call_llm_with_failover(system_instruction, user_payload)
                if answer_text:
                    citations = resolve_accurate_citations(query, answer_text, catalog, rows)
                    return {
                        "answer": answer_text,
                        "citations": citations,
                        "fallback_used": False,
                        "provider": provider_used,
                    }
    except Exception as exc:
        logger.warning("Answer generation timed out or failed: %s; using deterministic fallback", exc)

    # Deterministic Clean Markdown Fallback
    fallback_text = build_formatted_fallback(query, rows)
    citations = resolve_accurate_citations(query, fallback_text, catalog, rows)
    return {
        "answer": fallback_text,
        "citations": citations,
        "fallback_used": True,
        "provider": "deterministic-fallback",
    }
