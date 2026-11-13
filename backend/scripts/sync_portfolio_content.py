import asyncio
import json
import shutil
import subprocess
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.redis_guard import invalidate_portfolio_cache
from app.models.portfolio import (
    CandidateProfile,
    Certificate,
    Experience,
    Hackathon,
    PortfolioEmbedding,
    Project,
)
from app.services.github_sync import sync_github_repositories
from app.services.seed_embeddings import seed_all_embeddings

# Map of raw source file names to clean URL-safe filenames in frontend/public/certificates/
CERTIFICATE_FILE_MAPPING = {
    # 15 from C:\Users\shrey\Documents\Shreyas\Certificates
    "Deloitte Data Analytics Job Simulation.pdf": "deloitte-data-analytics-sim.pdf",
    "EY & Microsoft AI Skills Passport.pdf": "ey-microsoft-ai-skills-passport.pdf",
    "Google Gen AI APAC Edition Academy.pdf": "google-gen-ai-apac-academy.pdf",
    "Google Study Jams 2025.pdf": "google-study-jams-2025.pdf",
    "Intellipaat AI Bootcamp.pdf": "intellipaat-ai-bootcamp.pdf",
    "Microsoft Azure AI Fundamentals.pdf": "microsoft-azure-ai-fundamentals.pdf",
    "Nasscom Acquiring Data.pdf": "nasscom-acquiring-data.pdf",
    "Nasscom Data Processing & Visualisation.pdf": "nasscom-data-processing-visualisation.pdf",
    "Nasscom Exploratory Data Analysis.pdf": "nasscom-exploratory-data-analysis.pdf",
    "Nvidia Prompt Engineering.pdf": "nvidia-prompt-engineering.pdf",
    "Outskills Generative AI Mastermind .pdf": "outskills-genai-mastermind.pdf",
    "Tata Data Visualisation Job Simulation.pdf": "tata-data-visualisation-sim.pdf",
    "Tata GenAI Powered Data Analytics Job Simulation.pdf": "tata-genai-data-analytics.pdf",
    "Udemy AWS Certified Cloud Practitioner CLF-C02 2026.pdf": "aws-certified-cloud-practitioner.pdf",
    "Viswam AI.pdf": "viswam-ai-internship.pdf",
    # 10 from C:\Users\shrey\Documents\Shreyas\Certificates\Extra Certifications
    "Devnovate Hack With Hyderabad 3.0.pdf": "devnovate-hack-with-hyderabad-3.pdf",
    "IBM Cloud Computing Fundamentals.pdf": "ibm-cloud-computing-fundamentals.pdf",
    "IBM Cyber Security Fundamentals.pdf": "ibm-cyber-security-fundamentals.pdf",
    "IBM Digital Literacy.pdf": "ibm-digital-literacy.pdf",
    "Infosys AI - HCI Methodologies.pdf": "infosys-ai-hci-methodologies.pdf",
    "Infosys AI - HCI Overview.pdf": "infosys-ai-hci-overview.pdf",
    "Infosys Big Data & Hadoop 3.pdf": "infosys-big-data-hadoop.pdf",
    "Infosys Blockchain.pdf": "infosys-blockchain.pdf",
    "Microsoft Practice Assingment Badges.pdf": "microsoft-practice-assignment-badge.pdf",
    "SIH.pdf": "sih-2025-proof.pdf",
}

SRC_CERTS_DIR_1 = Path(r"C:\Users\shrey\Documents\Shreyas\Certificates")
SRC_CERTS_DIR_2 = Path(r"C:\Users\shrey\Documents\Shreyas\Certificates\Extra Certifications")
SRC_RESUME_FILE = Path(r"C:\Users\shrey\Documents\Shreyas\companies\Shreyas_Reddy_Resume.pdf")

DEST_CERTS_DIR = BASE_DIR / "frontend" / "public" / "certificates"
DEST_RESUME_DIR = BASE_DIR / "frontend" / "public" / "resume"
DEST_RESUME_FILE = DEST_RESUME_DIR / "Shreyas_Reddy_Resume.pdf"


def copy_certificates_and_resume() -> dict[str, int]:
    """Copy all 25 certificate PDFs and the resume PDF into frontend/public."""
    DEST_CERTS_DIR.mkdir(parents=True, exist_ok=True)
    DEST_RESUME_DIR.mkdir(parents=True, exist_ok=True)

    copied_certs = 0
    missing_certs: list[str] = []

    for src_name, dest_name in CERTIFICATE_FILE_MAPPING.items():
        src_path_1 = SRC_CERTS_DIR_1 / src_name
        src_path_2 = SRC_CERTS_DIR_2 / src_name
        dest_path = DEST_CERTS_DIR / dest_name

        found = False
        for src_path in (src_path_1, src_path_2):
            if src_path.exists():
                shutil.copy2(src_path, dest_path)
                copied_certs += 1
                found = True
                break
        if not found:
            # Check if destination already exists
            if dest_path.exists():
                copied_certs += 1
            else:
                missing_certs.append(src_name)

    copied_resume = 0
    if SRC_RESUME_FILE.exists():
        shutil.copy2(SRC_RESUME_FILE, DEST_RESUME_FILE)
        copied_resume = 1
    elif DEST_RESUME_FILE.exists():
        copied_resume = 1

    print(f"PDF Assets: Copied {copied_certs}/25 certificates, Resume: {'OK' if copied_resume else 'MISSING'}")
    if missing_certs:
        print(f"Warning: Missing source certificates: {missing_certs}")

    return {"certs": copied_certs, "resume": copied_resume}


async def sync_database_from_manifest(manifest_path: Path) -> dict[str, Any]:
    """Synchronize PostgreSQL from content/portfolio_data.json."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)

    async with AsyncSessionLocal() as session:
        # 1. CandidateProfile
        profile_data = data["candidate_profile"]
        profile_stmt = pg_insert(CandidateProfile).values(
            singleton_key=profile_data["singleton_key"],
            full_name=profile_data["full_name"],
            display_name=profile_data["display_name"],
            headline=profile_data["headline"],
            subheadline=profile_data["subheadline"],
            location=profile_data["location"],
            education_degree=profile_data["education_degree"],
            education_institution=profile_data["education_institution"],
            graduation_year=profile_data["graduation_year"],
            github_username=profile_data["github_username"],
            github_url=profile_data["github_url"],
            linkedin_url=profile_data["linkedin_url"],
            email_masked=profile_data["email_masked"],
            phone_masked=profile_data["phone_masked"],
            email_cleartext=profile_data["email_cleartext"],
            phone_cleartext=profile_data["phone_cleartext"],
            resume_pdf_url=profile_data["resume_pdf_url"],
            availability_badge=profile_data["availability_badge"],
            hero_pillars=profile_data["hero_pillars"],
            hero_3d_config=profile_data.get("hero_3d_config", {}),
        ).on_conflict_do_update(
            index_elements=[CandidateProfile.singleton_key],
            set_={
                "full_name": profile_data["full_name"],
                "display_name": profile_data["display_name"],
                "headline": profile_data["headline"],
                "subheadline": profile_data["subheadline"],
                "location": profile_data["location"],
                "education_degree": profile_data["education_degree"],
                "education_institution": profile_data["education_institution"],
                "graduation_year": profile_data["graduation_year"],
                "github_username": profile_data["github_username"],
                "github_url": profile_data["github_url"],
                "linkedin_url": profile_data["linkedin_url"],
                "email_masked": profile_data["email_masked"],
                "phone_masked": profile_data["phone_masked"],
                "email_cleartext": profile_data["email_cleartext"],
                "phone_cleartext": profile_data["phone_cleartext"],
                "resume_pdf_url": profile_data["resume_pdf_url"],
                "availability_badge": profile_data["availability_badge"],
                "hero_pillars": profile_data["hero_pillars"],
                "hero_3d_config": profile_data.get("hero_3d_config", {}),
                "updated_at": datetime.now(UTC),
            },
        )
        await session.execute(profile_stmt)
        print("CandidateProfile synced.")

        # 2. Flagship & Seed Projects
        projects_data = data["projects"]
        manifest_project_slugs = [p["slug"] for p in projects_data]

        # Explicitly purge any meta profile or duplicate repository
        meta_projects = (
            await session.execute(
                select(Project).where(
                    Project.slug.in_([
                        "shreyas-reddy707",
                        "shreyas-reddy-707",
                        "shreyas-portfolio",
                        "denoising-edge-detection",
                        settings.GITHUB_USERNAME.lower(),
                    ])
                )
            )
        ).scalars().all()
        for mp in meta_projects:
            print(f"Purging duplicate/meta project: {mp.slug}")
            await session.execute(
                delete(PortfolioEmbedding).where(
                    PortfolioEmbedding.source_type == "project",
                    PortfolioEmbedding.source_slug == mp.slug,
                )
            )
            await session.delete(mp)
        await session.flush()

        # Clean stale projects not in manifest
        stale_projects = (
            await session.execute(
                select(Project).where(
                    Project.slug.notin_(manifest_project_slugs),
                )
            )
        ).scalars().all()

        for sp in stale_projects:
            print(f"Removing stale project: {sp.slug}")
            await session.execute(
                delete(PortfolioEmbedding).where(
                    PortfolioEmbedding.source_type == "project",
                    PortfolioEmbedding.source_slug == sp.slug,
                )
            )
            await session.delete(sp)

        for proj in projects_data:
            stmt = pg_insert(Project).values(
                slug=proj["slug"],
                title=proj["title"],
                tagline=proj["tagline"],
                category=proj["category"],
                summary=proj["summary"],
                architecture_md=proj["architecture_md"],
                ai_explainer=proj.get("ai_explainer", {}),
                tech_stack=proj.get("tech_stack", []),
                security_highlights=proj.get("security_highlights", []),
                metrics=proj.get("metrics", []),
                github_url=proj.get("github_url"),
                live_url=proj.get("live_url"),
                primary_language=proj.get("primary_language"),
                is_flagship=proj.get("is_flagship", False),
                is_featured=proj.get("is_featured", True),
                display_order=proj.get("display_order", 10),
                model_3d_config=proj.get("model_3d_config", {}),
            ).on_conflict_do_update(
                index_elements=[Project.slug],
                set_={
                    "title": proj["title"],
                    "tagline": proj["tagline"],
                    "category": proj["category"],
                    "summary": proj["summary"],
                    "architecture_md": proj["architecture_md"],
                    "ai_explainer": proj.get("ai_explainer", {}),
                    "tech_stack": proj.get("tech_stack", []),
                    "security_highlights": proj.get("security_highlights", []),
                    "metrics": proj.get("metrics", []),
                    "github_url": proj.get("github_url"),
                    "live_url": proj.get("live_url"),
                    "primary_language": proj.get("primary_language"),
                    "is_flagship": proj.get("is_flagship", False),
                    "is_featured": proj.get("is_featured", True),
                    "is_auto_synced": proj.get("is_auto_synced", False),
                    "display_order": proj.get("display_order", 10),
                    "model_3d_config": proj.get("model_3d_config", {}),
                    "updated_at": datetime.now(UTC),
                },
            )
            await session.execute(stmt)
        print(f"Projects synced ({len(manifest_project_slugs)} projects).")

        # 3. Experiences
        experiences_data = data["experiences"]
        manifest_exp_slugs = [e["slug"] for e in experiences_data]

        stale_exps = (
            await session.execute(
                select(Experience).where(Experience.slug.notin_(manifest_exp_slugs))
            )
        ).scalars().all()
        for se in stale_exps:
            print(f"Removing stale experience: {se.slug}")
            await session.execute(
                delete(PortfolioEmbedding).where(
                    PortfolioEmbedding.source_type == "experience",
                    PortfolioEmbedding.source_slug == se.slug,
                )
            )
            await session.delete(se)

        for exp in experiences_data:
            s_date = date.fromisoformat(exp["start_date"])
            e_date = date.fromisoformat(exp["end_date"]) if exp.get("end_date") else None
            stmt = pg_insert(Experience).values(
                slug=exp["slug"],
                role=exp["role"],
                organization=exp["organization"],
                organization_url=exp.get("organization_url"),
                location=exp.get("location", "Hyderabad, India"),
                employment_type=exp["employment_type"],
                start_date=s_date,
                end_date=e_date,
                is_current=exp.get("is_current", False),
                summary=exp["summary"],
                highlights=exp.get("highlights", []),
                metrics=exp.get("metrics", []),
                tech_stack=exp.get("tech_stack", []),
                spline_node_config=exp.get("spline_node_config", {}),
                display_order=exp.get("display_order", 10),
            ).on_conflict_do_update(
                index_elements=[Experience.slug],
                set_={
                    "role": exp["role"],
                    "organization": exp["organization"],
                    "organization_url": exp.get("organization_url"),
                    "location": exp.get("location", "Hyderabad, India"),
                    "employment_type": exp["employment_type"],
                    "start_date": s_date,
                    "end_date": e_date,
                    "is_current": exp.get("is_current", False),
                    "summary": exp["summary"],
                    "highlights": exp.get("highlights", []),
                    "metrics": exp.get("metrics", []),
                    "tech_stack": exp.get("tech_stack", []),
                    "spline_node_config": exp.get("spline_node_config", {}),
                    "display_order": exp.get("display_order", 10),
                    "updated_at": datetime.now(UTC),
                },
            )
            await session.execute(stmt)
        print(f"Experiences synced ({len(manifest_exp_slugs)} experiences).")

        # 4. Hackathons
        hackathons_data = data["hackathons"]
        manifest_hack_slugs = [h["slug"] for h in hackathons_data]

        stale_hacks = (
            await session.execute(
                select(Hackathon).where(Hackathon.slug.notin_(manifest_hack_slugs))
            )
        ).scalars().all()
        for sh in stale_hacks:
            print(f"Removing stale hackathon: {sh.slug}")
            await session.execute(
                delete(PortfolioEmbedding).where(
                    PortfolioEmbedding.source_type == "hackathon",
                    PortfolioEmbedding.source_slug == sh.slug,
                )
            )
            await session.delete(sh)

        for hack in hackathons_data:
            ev_date = date.fromisoformat(hack["event_date"])
            stmt = pg_insert(Hackathon).values(
                slug=hack["slug"],
                event_name=hack["event_name"],
                organizer=hack["organizer"],
                project_title=hack["project_title"],
                award_status=hack["award_status"],
                team_name=hack.get("team_name", "Team CODEX"),
                role=hack["role"],
                team_members=hack.get("team_members", []),
                event_date=ev_date,
                problem_statement=hack["problem_statement"],
                architecture_summary=hack["architecture_summary"],
                tech_stack=hack.get("tech_stack", []),
                outcomes=hack.get("outcomes", []),
                github_url=hack.get("github_url"),
                live_url=hack.get("live_url"),
                proof_url=hack.get("proof_url"),
                model_3d_config=hack.get("model_3d_config", {}),
                display_order=hack.get("display_order", 10),
            ).on_conflict_do_update(
                index_elements=[Hackathon.slug],
                set_={
                    "event_name": hack["event_name"],
                    "organizer": hack["organizer"],
                    "project_title": hack["project_title"],
                    "award_status": hack["award_status"],
                    "team_name": hack.get("team_name", "Team CODEX"),
                    "role": hack["role"],
                    "team_members": hack.get("team_members", []),
                    "event_date": ev_date,
                    "problem_statement": hack["problem_statement"],
                    "architecture_summary": hack["architecture_summary"],
                    "tech_stack": hack.get("tech_stack", []),
                    "outcomes": hack.get("outcomes", []),
                    "github_url": hack.get("github_url"),
                    "live_url": hack.get("live_url"),
                    "proof_url": hack.get("proof_url"),
                    "model_3d_config": hack.get("model_3d_config", {}),
                    "display_order": hack.get("display_order", 10),
                    "updated_at": datetime.now(UTC),
                },
            )
            await session.execute(stmt)
        print(f"Hackathons synced ({len(manifest_hack_slugs)} hackathons).")

        # 5. Certificates
        certificates_data = data["certificates"]
        manifest_cert_slugs = [c["slug"] for c in certificates_data]

        stale_certs = (
            await session.execute(
                select(Certificate).where(Certificate.slug.notin_(manifest_cert_slugs))
            )
        ).scalars().all()
        for sc in stale_certs:
            print(f"Removing stale certificate: {sc.slug}")
            await session.execute(
                delete(PortfolioEmbedding).where(
                    PortfolioEmbedding.source_type == "certificate",
                    PortfolioEmbedding.source_slug == sc.slug,
                )
            )
            await session.delete(sc)

        for cert in certificates_data:
            iss_date = date.fromisoformat(cert["issue_date"])
            stmt = pg_insert(Certificate).values(
                slug=cert["slug"],
                title=cert["title"],
                issuer=cert["issuer"],
                category=cert["category"],
                issue_date=iss_date,
                credential_id=cert.get("credential_id"),
                verify_url=cert.get("verify_url"),
                certificate_asset_url=cert.get("certificate_asset_url"),
                skills_covered=cert.get("skills_covered", []),
                summary=cert["summary"],
                badge_3d_config=cert.get("badge_3d_config", {}),
                is_featured=cert.get("is_featured", True),
                display_order=cert.get("display_order", 10),
            ).on_conflict_do_update(
                index_elements=[Certificate.slug],
                set_={
                    "title": cert["title"],
                    "issuer": cert["issuer"],
                    "category": cert["category"],
                    "issue_date": iss_date,
                    "credential_id": cert.get("credential_id"),
                    "verify_url": cert.get("verify_url"),
                    "certificate_asset_url": cert.get("certificate_asset_url"),
                    "skills_covered": cert.get("skills_covered", []),
                    "summary": cert["summary"],
                    "badge_3d_config": cert.get("badge_3d_config", {}),
                    "is_featured": cert.get("is_featured", True),
                    "display_order": cert.get("display_order", 10),
                    "updated_at": datetime.now(UTC),
                },
            )
            await session.execute(stmt)
        print(f"Certificates synced ({len(manifest_cert_slugs)} certificates).")

        # Clean up any stale auto-synced duplicate rows
        stale_slugs = ["construct-pulse", "secure-rag", "team-31"]
        for ss in stale_slugs:
            await session.execute(
                delete(PortfolioEmbedding).where(
                    PortfolioEmbedding.source_type == "project",
                    PortfolioEmbedding.source_slug == ss,
                )
            )
            await session.execute(
                delete(Project).where(Project.slug == ss, Project.is_flagship.is_(False))
            )

        await session.commit()

        # 6. Run GitHub sync if configured
        if settings.GITHUB_USERNAME and settings.GITHUB_PAT:
            try:
                print("Running GitHub repository sync...")
                gh_result = await sync_github_repositories(session)
                print(f"GitHub sync completed: {gh_result}")
            except Exception as e:
                print(f"GitHub sync warning: {e}")

        # 7. Refresh embeddings
        print("Refreshing pgvector embeddings...")
        embed_result = await seed_all_embeddings(session)
        print(f"Embeddings refreshed: {embed_result}")

        # 8. Flush Redis cache
        await invalidate_portfolio_cache()
        print("Redis portfolio cache invalidated.")

    return {
        "projects": len(manifest_project_slugs),
        "experiences": len(manifest_exp_slugs),
        "hackathons": len(manifest_hack_slugs),
        "certificates": len(manifest_cert_slugs),
    }


def update_profile_readme() -> None:
    """Run render_profile_readme.py to keep docs/GITHUB_PROFILE_README_PREVIEW.md in sync."""
    readme_script = BASE_DIR / "backend" / "scripts" / "render_profile_readme.py"
    manifest_file = BASE_DIR / "content" / "portfolio_data.json"
    preview_output = BASE_DIR / "docs" / "GITHUB_PROFILE_README_PREVIEW.md"

    if readme_script.exists() and manifest_file.exists():
        try:
            cmd = [
                sys.executable,
                str(readme_script),
                "--manifest",
                str(manifest_file),
                "--output",
                str(preview_output),
            ]
            subprocess.run(cmd, check=True)
            print("Local docs/GITHUB_PROFILE_README_PREVIEW.md preview block updated.")
        except Exception as e:
            print(f"Profile README preview sync warning: {e}")


async def main() -> None:
    print("=== Starting Comprehensive Portfolio Content & Asset Sync ===")
    copy_results = copy_certificates_and_resume()
    manifest_path = BASE_DIR / "content" / "portfolio_data.json"
    db_results = await sync_database_from_manifest(manifest_path)
    update_profile_readme()
    print("=== Sync Finished Successfully ===")
    print(f"Summary: {copy_results}, {db_results}")


if __name__ == "__main__":
    asyncio.run(main())

