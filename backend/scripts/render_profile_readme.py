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


def render_markdown_block(data: dict[str, Any]) -> str:
    """Render the bounded Markdown block for Shreyas's GitHub Profile README."""
    profile = data["candidate_profile"]
    projects = data["projects"]
    flagships = [p for p in projects if p.get("is_flagship")]
    colabs = [p for p in projects if not p.get("is_flagship")]
    hackathons = data["hackathons"]
    certificates = data["certificates"]

    lines: list[str] = [
        START_MARKER,
        f"## {profile['full_name']} — {profile['headline']}",
        "",
        (
            f"**Forward Deployed Engineer at Limelite Constructions (NZ)** | "
            f"**Former Tech Lead at Viswam.ai** (AI/ML) | "
            f"**{profile['education_degree']}** @ {profile['education_institution']} ({profile['graduation_year']})"
        ),
        "",
        (
            f"- **LinkedIn:** [{profile['linkedin_url']}]({profile['linkedin_url']})\n"
            f"- **GitHub:** [{profile['github_url']}]({profile['github_url']})\n"
            f"- **Email:** [shreyas.chemakoora@gmail.com](mailto:shreyas.chemakoora@gmail.com)"
        ),
        "",
        "### Flagship Engineering Systems",
        "| System | Architecture & Impact | Stack |",
        "| :--- | :--- | :--- |",
    ]

    for proj in flagships:
        title = proj["title"]
        url = proj.get("github_url")
        linked_title = f"[{title}]({url})" if url else title
        stack = ", ".join((proj.get("tech_stack") or [])[:5])
        lines.append(f"| **{linked_title}** | {proj['tagline']} | `{stack}` |")

    if colabs:
        lines.extend([
            "",
            "### Google Colab Research Labs",
            "| Research Lab / Notebook | Core Focus & Benchmark | Stack |",
            "| :--- | :--- | :--- |",
        ])
        for lab in colabs:
            title = lab["title"]
            url = lab.get("github_url")
            linked_title = f"[{title}]({url})" if url else title
            stack = ", ".join((lab.get("tech_stack") or [])[:4])
            lines.append(f"| **{linked_title}** | {lab['tagline']} | `{stack}` |")

    lines.extend(["", "### Hackathon Arena (Team CODEX)"])
    for hack in hackathons:
        lines.append(
            f"- **{hack['event_name']}** — *{hack['project_title']}* "
            f"({hack['role']} | {hack['award_status']})"
        )

    lines.extend(["", "### Verified Certifications Vault"])
    for cert in certificates:
        lines.append(f"- **{cert['title']}** — {cert['issuer']} (`{cert['category']}`)")

    lines.append(END_MARKER)
    return "\n".join(lines) + "\n"


def update_readme_content(existing_text: str, rendered_block: str) -> str:
    """Replace the PORTFOLIO-SYNC block in text or append if missing."""
    if _BLOCK_RE.search(existing_text):
        return _BLOCK_RE.sub(rendered_block.rstrip("\n"), existing_text)
    separator = "\n\n" if existing_text and not existing_text.endswith("\n\n") else ""
    return existing_text + separator + rendered_block


def update_readme_file(target_path: Path, rendered_block: str) -> None:
    """Replace the PORTFOLIO-SYNC block in target_path or append if missing."""
    if target_path.exists():
        existing = target_path.read_text(encoding="utf-8")
        updated = update_readme_content(existing, rendered_block)
    else:
        updated = rendered_block
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

            updated_text = update_readme_content(existing_text, rendered_block)
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

    updated_text = update_readme_content(existing_text, rendered_block)
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
    block = render_markdown_block(data)

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
