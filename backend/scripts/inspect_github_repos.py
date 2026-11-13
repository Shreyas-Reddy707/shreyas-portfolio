import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "backend"))

import httpx
from app.core.config import settings


async def main():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.GITHUB_PAT:
        headers["Authorization"] = f"Bearer {settings.GITHUB_PAT}"
    url = f"https://api.github.com/users/{settings.GITHUB_USERNAME}/repos?per_page=100"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, headers=headers)
        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text}")
            return
        repos = r.json()
        print(f"=== Total repos for {settings.GITHUB_USERNAME}: {len(repos)} ===")
        for repo in repos:
            print(f"- Name: {repo.get('name')}")
            print(f"  URL: {repo.get('html_url')}")
            print(f"  Language: {repo.get('language')}")
            print(f"  Description: {repo.get('description')}")
            print(f"  Stars: {repo.get('stargazers_count')} | Forks: {repo.get('forks_count')} | Forked: {repo.get('fork')}")
            print()

if __name__ == "__main__":
    asyncio.run(main())
