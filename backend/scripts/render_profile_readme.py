import argparse
import base64
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None

START_MARKER = "<!-- PORTFOLIO-SYNC:START -->"
END_MARKER = "<!-- PORTFOLIO-SYNC:END -->"
_BLOCK_RE = re.compile(
    rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
    re.DOTALL,
)

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR / "backend") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "backend"))


def render_readme_block(data: dict[str, Any]) -> str:
    """Render the rich, unified GitHub Profile README block driven 100% by portfolio_data.json."""
    profile = data["candidate_profile"]
    projects = data.get("projects", [])
    flagships = [p for p in projects if p.get("is_flagship")]
    colabs = [p for p in projects if not p.get("is_flagship")]
    experiences = data.get("experiences", [])
    hackathons = data.get("hackathons", [])
    certificates = data.get("certificates", [])
    featured_certs = [c for c in certificates if c.get("is_featured") is True]

    lines: list[str] = [
        START_MARKER,
        '<div align="center">',
        "",
        '<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1e293b,100:0891b2&height=210&section=header&text=Shreyas%20Reddy&fontSize=54&fontColor=f8fafc&animation=fadeIn&fontAlignY=35&desc=Forward%20Deployed%20Engineer%20%7C%20GenAI%20%26%20Full-Stack%20Systems&descAlignY=58&descSize=18" width="100%" />',
        "",
        '[![Typing SVG](https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=18&duration=3200&pause=1000&color=22D3EE&center=true&vCenter=true&width=760&lines=Forward+Deployed+Engineer+(Contract)+%40+Limelite+Constructions+(NZ);Zero-Trust+Multi-Agent+RAG+%26+LangGraph+Architectures;Full-Stack+AI+Systems%3A+Next.js+15+%E2%80%A2+FastAPI+%E2%80%A2+pgvector+%E2%80%A2+Flutter;1+of+10+Tech+Leads+(from+200+Interns)+%40+VISWAM.AI+(IIIT-H+%26+Swecha))](https://shreyas-portfolio-sandy.vercel.app)',
        "",
        "<br/>",
        "",
        '[![Interactive 3D Portfolio](https://img.shields.io/badge/%F0%9F%8C%90%20Interactive%203D%20Portfolio-shreyas--portfolio.vercel.app-0891B2?style=for-the-badge&labelColor=0F172A)](https://shreyas-portfolio-sandy.vercel.app) '
        f'[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)]({profile["linkedin_url"]}) '
        '[![Email](https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:shreyas.chemakoora@gmail.com) '
        "[![Education](https://img.shields.io/badge/Education-B.Tech%20CSE%20(AI)%20'27-10B981?style=for-the-badge&labelColor=0F172A)](https://shreyas-portfolio-sandy.vercel.app) "
        '[![Location](https://img.shields.io/badge/Location-Hyderabad%2C%20India-64748B?style=for-the-badge&labelColor=0F172A)](https://shreyas-portfolio-sandy.vercel.app)',
        "",
        "</div>",
        "",
        "---",
        "",
        "## 👨‍💻 About Me & Engineering Focus",
        "",
        f"- 🎓 **Undergraduate:** {profile['education_degree']} at **{profile['education_institution']}** (Graduating {profile['graduation_year']}, CGPA 7.24/10).",
        "- 🏗️ **Forward Deployed Engineer (Contract):** Architecting technical workflow solutions, automated PDF specification engines, and full-scale CRM automation remotely for **Limelite Constructions** (New Zealand).",
        "- 🚀 **Technical Leadership:** Former **Tech Lead** at **VISWAM.AI (Viswam.ai)** (Swecha & IIIT Hyderabad) — selected as 1 of 10 Tech Leads from ~200 interns to direct AI engineering, regional dataset corpus development, and intern team delivery.",
        "- 🛡️ **Core Architecture:** Designing production Retrieval-Augmented Generation (RAG) defenses (Zero-Trust, 128-bit cryptographic hex nonces, indirect injection interception), multi-agent LangGraph orchestrations, and full-stack systems with FastAPI, Next.js 15, PostgreSQL (`pgvector`), and Redis.",
        "",
        "---",
        "",
        "## 🛠️ Technical Stack & Tooling",
        "",
        "### Languages & Core",
        "[![Languages & Core](https://skillicons.dev/icons?i=python,postgres,typescript,java,c,dart&perline=6)](https://skillicons.dev)",
        "",
        "### Backend, Frontend & Mobile",
        "[![Backend, Frontend & Mobile](https://skillicons.dev/icons?i=fastapi,nextjs,react,threejs,flutter,redis,docker,aws,git,github,gitlab&perline=11)](https://skillicons.dev)",
        "",
        "### AI, RAG & Data Engineering",
        "![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white) "
        "![Qdrant](https://img.shields.io/badge/Qdrant-DC2626?style=flat-square&logo=qdrant&logoColor=white) "
        "![pgvector](https://img.shields.io/badge/pgvector-336791?style=flat-square&logo=postgresql&logoColor=white) "
        "![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=flat-square&logo=duckdb&logoColor=black) "
        "![Ollama](https://img.shields.io/badge/Ollama-000000?style=flat-square&logo=ollama&logoColor=white) "
        "![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=flat-square&logo=huggingface&logoColor=black) "
        "![Dify](https://img.shields.io/badge/Dify-155EEF?style=flat-square) "
        "![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white) "
        "![pandas](https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white) "
        "![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white) "
        "![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=flat-square&logo=powerbi&logoColor=black)",
        "",
        "---",
        "",
        "## 💼 Experience & Leadership Timeline",
        "",
    ]

    for exp in experiences:
        role = exp.get("role", "")
        org = exp.get("organization", "")
        loc = exp.get("location", "")
        emp_type = exp.get("employment_type", "Contract" if exp.get("is_current") else "Internship")
        start = exp.get("start_date", "")
        end = "PRESENT" if exp.get("is_current") else (exp.get("end_date") or "PRESENT")
        summary = exp.get("summary", "")
        highlights = exp.get("highlights", [])

        lines.extend([
            f"### {role} — {org}",
            f"`{emp_type}` • *{loc}* • **{start} — {end}**",
            "",
            summary,
            "",
        ])
        for hl in highlights[:3]:
            lines.append(f"- {hl}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 🏛️ Flagship Engineering Systems",
        "",
        "| System | Architecture & Defense Focus | Primary Tech Stack | Interactive Deep-Dive |",
        "| :--- | :--- | :--- | :--- |",
    ])

    for proj in flagships:
        title = proj["title"]
        slug = proj["slug"]
        url = proj.get("github_url") or f"https://github.com/Shreyas-Reddy707/{slug}"
        tagline = proj.get("tagline", "")
        stack = ", ".join(f"`{s}`" for s in (proj.get("tech_stack") or [])[:4])
        live_link = f"[Explore 3D Architecture ↗](https://shreyas-portfolio-sandy.vercel.app/projects#{slug})"
        lines.append(f"| **[{title}]({url})** | {tagline} | {stack} | {live_link} |")

    lines.append("")

    for idx, proj in enumerate(flagships):
        title = proj["title"]
        slug = proj["slug"]
        url = proj.get("github_url") or f"https://github.com/Shreyas-Reddy707/{slug}"
        tagline = proj.get("tagline", "")
        explainer = proj.get("ai_explainer") or {}
        arch_items = explainer.get("architecture_stack") or proj.get("tech_stack") or []
        arch_str = " • ".join(arch_items[:4])
        core_cap = explainer.get("problem_statement") or proj.get("summary") or tagline
        metrics = proj.get("metrics") or []
        metrics_str = " • ".join(f"{m.get('label')}: {m.get('value')}" for m in metrics if isinstance(m, dict) and m.get("label"))
        if not metrics_str:
            sec_hl = proj.get("security_highlights") or []
            metrics_str = " • ".join(sec_hl[:3]) if sec_hl else "Production Verification & Benchmarks"

        open_attr = " open" if idx < 2 else ""
        lines.extend([
            f"<details{open_attr}>",
            f"<summary><b>[Flagship System] {title}</b> — <i>{tagline}</i></summary>",
            "<br/>",
            "",
            "| Dimension | Implementation & Details |",
            "| :--- | :--- |",
            f"| **Architecture** | {arch_str} |",
            f"| **Core Capabilities / Defense** | {core_cap} |",
            f"| **Benchmarks / Security** | {metrics_str} |",
            f"| **Links & Verification** | [GitHub Repository]({url}) • [Live 3D Deep Dive](https://shreyas-portfolio-sandy.vercel.app/projects#{slug}) |",
            "",
            "</details>",
            "",
        ])

    if colabs:
        lines.extend([
            "---",
            "",
            "## 🔬 Google Colab Research Labs",
            "",
            "| Research Lab / Notebook | Core Focus & Methodology | Applied Tooling |",
            "| :--- | :--- | :--- |",
        ])
        for lab in colabs:
            title = lab["title"]
            url = lab.get("github_url") or f"https://github.com/Shreyas-Reddy707/{lab['slug']}"
            tagline = lab.get("tagline", "")
            stack = ", ".join(f"`{s}`" for s in (lab.get("tech_stack") or [])[:4])
            lines.append(f"| **[{title}]({url})** | {tagline} | {stack} |")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 🏆 Hackathon Arena (Team CODEX)",
        "",
    ])
    for hack in hackathons:
        event = hack.get("event_name", "")
        pt = hack.get("project_title", "")
        role = hack.get("role", "")
        status = hack.get("award_status", "")
        lines.append(f"- **{event}** — *{pt}* ({role} | {status})")

    lines.extend([
        "",
        "---",
        "",
        "## 📜 Curated Top Certifications",
        "",
    ])

    # Group featured certificates
    cloud_ai = []
    job_sims = []
    hack_builds = []

    for cert in featured_certs:
        issuer = cert.get("issuer", "")
        title = cert.get("title", "")
        cat = cert.get("category", "")
        item = f"- **{title}** — {issuer} (`{cat}`)"
        if "Tata" in issuer or "Deloitte" in issuer:
            job_sims.append(item)
        elif any(k in issuer for k in ["Microsoft", "Google", "NVIDIA", "AWS", "EY"]):
            cloud_ai.append(item)
        else:
            hack_builds.append(item)

    if cloud_ai:
        lines.extend(["#### Cloud & AI Credentials"] + cloud_ai + [""])
    if job_sims:
        lines.extend(["#### Industry Job Simulations"] + job_sims + [""])
    if hack_builds:
        lines.extend(["#### Hackathon Finals & Applied Builds"] + hack_builds + [""])

    lines.extend([
        "> 📄 **[View & Verify All 22 Official Certificate PDFs in the Interactive Vault ↗](https://shreyas-portfolio-sandy.vercel.app/certificates)**",
        "",
        "---",
        "",
        '<div align="center">',
        "",
        '<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1e293b,100:0891b2&height=110&section=footer" width="100%" />',
        "",
        "</div>",
        "",
        END_MARKER,
    ])

    return "\n".join(lines) + "\n"


render_markdown_block = render_readme_block


def merge_into_readme(existing_text: str, rendered_block: str) -> str:
    """Replace the entire README with the rendered block (bounded by sync markers)."""
    return rendered_block.strip() + "\n"


update_readme_content = merge_into_readme


def update_readme_file(target_path: Path, rendered_block: str) -> None:
    """Replace the entire target README file with the rendered block."""
    existing = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
    updated = merge_into_readme(existing, rendered_block)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(updated, encoding="utf-8")


def push_to_github_profile(rendered_block: str, username: str, pat: str) -> bool:
    """Push the rendered block to https://github.com/{username}/{username}/README.md via GitHub Contents API."""
    url = f"https://api.github.com/repos/{username}/{username}/contents/README.md"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "shreyas-portfolio-sync",
    }

    if httpx is not None:
        with httpx.Client(timeout=15.0) as client:
            sha: str | None = None
            existing_text = ""
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                sha = data.get("sha")
                raw_b64 = data.get("content", "")
                try:
                    existing_text = base64.b64decode(raw_b64).decode("utf-8")
                except Exception as exc:
                    print(f"Failed to safely decode existing README content: {exc}")
                    return False
                print(f"Fetched existing README.md for {username}/{username} (SHA: {sha})")
            elif resp.status_code == 404:
                print(f"README.md does not exist yet in {username}/{username}; creating fresh.")
            else:
                print(f"GitHub GET README failed: {resp.status_code} - {resp.text}")
                return False

            updated_text = merge_into_readme(existing_text, rendered_block)
            payload: dict[str, Any] = {
                "message": "chore(profile): synchronize portfolio manifest via automation",
                "content": base64.b64encode(updated_text.encode("utf-8")).decode("ascii"),
            }
            if sha:
                payload["sha"] = sha

            put_resp = client.put(url, headers=headers, json=payload)
            if put_resp.status_code in (200, 201):
                print(f"Successfully pushed updated README.md to {username}/{username} (status: {put_resp.status_code})")
                return True
            print(f"GitHub PUT README failed: {put_resp.status_code} - {put_resp.text}")
            return False

    # Fallback using Python standard library urllib when httpx is unavailable
    if not url.startswith("https://api.github.com/"):
        raise ValueError(f"Untrusted GitHub API URL: {url}")

    sha = None
    existing_text = ""
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15.0) as resp:  # noqa: S310
            data = json.loads(resp.read().decode("utf-8"))
            sha = data.get("sha")
            raw_b64 = data.get("content", "")
            try:
                existing_text = base64.b64decode(raw_b64).decode("utf-8")
            except Exception as exc:
                print(f"Failed to safely decode existing README content: {exc}")
                return False
            print(f"Fetched existing README.md for {username}/{username} (SHA: {sha})")
    except urllib.error.HTTPError as err:
        if err.code == 404:
            print(f"README.md does not exist yet in {username}/{username}; creating fresh.")
        else:
            err_body = err.read().decode("utf-8", errors="replace")
            print(f"GitHub GET README failed: {err.code} - {err_body}")
            return False
    except urllib.error.URLError as err:
        print(f"Network error connecting to GitHub API: {err}")
        return False

    updated_text = merge_into_readme(existing_text, rendered_block)
    payload_dict: dict[str, Any] = {
        "message": "chore(profile): synchronize portfolio manifest via automation",
        "content": base64.b64encode(updated_text.encode("utf-8")).decode("ascii"),
    }
    if sha:
        payload_dict["sha"] = sha

    put_data = json.dumps(payload_dict).encode("utf-8")
    put_headers = {**headers, "Content-Type": "application/json"}
    put_req = urllib.request.Request(url, data=put_data, headers=put_headers, method="PUT")
    try:
        with urllib.request.urlopen(put_req, timeout=15.0) as put_resp:  # noqa: S310
            code = put_resp.getcode()
            if code in (200, 201):
                print(f"Successfully pushed updated README.md to {username}/{username} (status: {code})")
                return True
            print(f"GitHub PUT README failed: {code}")
            return False
    except urllib.error.HTTPError as err:
        err_body = err.read().decode("utf-8", errors="replace")
        print(f"GitHub PUT README failed: {err.code} - {err_body}")
        return False
    except urllib.error.URLError as err:
        print(f"Network error pushing to GitHub API: {err}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Render GitHub Profile README sync block.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=BASE_DIR / "content" / "portfolio_data.json",
        help="Path to portfolio_data.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "docs" / "GITHUB_PROFILE_README_PREVIEW.md",
        help="Write rendered block to file (default: docs/GITHUB_PROFILE_README_PREVIEW.md)",
    )
    parser.add_argument("--target-readme", type=Path, help="Update an explicit target README.md in place")
    parser.add_argument("--push-github", action="store_true", help="Push block directly to GitHub Profile repository")
    args = parser.parse_args()

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    block = render_readme_block(data)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(block, encoding="utf-8")
        print(f"Rendered block written to {args.output}")

    if args.target_readme:
        update_readme_file(args.target_readme, block)
        print(f"Target README updated: {args.target_readme}")

    if args.push_github:
        from app.core.config import settings

        if not settings.GITHUB_PAT:
            print("ERROR: GITHUB_PAT is not configured in settings.")
            sys.exit(1)
        success = push_to_github_profile(
            rendered_block=block,
            username=settings.GITHUB_USERNAME,
            pat=settings.GITHUB_PAT,
        )
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
