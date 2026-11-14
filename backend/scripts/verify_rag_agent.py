import asyncio
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import AsyncSessionLocal
from app.services.rag_agent import answer_recruiter_query

TEST_CASES = [
    {
        "id": "Q1",
        "query": "how many projects did he do?",
        "check": lambda citations: all(c["source_type"] == "project" for c in citations) and len(citations) > 0,
        "description": "Assert 100% of returned citations have source_type == 'project' (zero experience or profile)",
    },
    {
        "id": "Q2",
        "query": "what are the hackathons he participated in?",
        "check": lambda citations: (
            set(c["slug"] for c in citations) == {"sih-2025", "devnovate-hack-hyderabad-3", "wikiverse-iiith-2025"}
            and all(c["source_type"] == "hackathon" for c in citations)
        ),
        "description": "Assert citations contain ONLY the 3 hackathons (sih-2025, devnovate-hack-hyderabad-3, wikiverse-iiith-2025) and zero education/ICFAI rows",
    },
    {
        "id": "Q3",
        "query": "What does Shreyas do at Limelite Constructions and Viswam.ai?",
        "check": lambda citations: {"limelite-fde-nz", "viswam-ai-tech-lead"}.issubset(set(c["slug"] for c in citations)),
        "description": "Assert citations match the experience records (limelite-fde-nz, viswam-ai-tech-lead)",
    },
    {
        "id": "Q4",
        "query": "How does SecureRAG stop prompt injection?",
        "check": lambda citations: len(citations) > 0 and citations[0]["slug"] == "securerag",
        "description": "Assert securerag is the #1 citation",
    },
]

async def main():
    print("=" * 80)
    print("VERIFYING CITATION ACCURACY & DEEP-LINK METADATA ACROSS RECRUITER QUERIES")
    print("=" * 80)

    all_passed = True
    async with AsyncSessionLocal() as session:
        for tc in TEST_CASES:
            print(f"\n--- {tc['id']}: \"{tc['query']}\" ---")
            result = await answer_recruiter_query(session, query=tc["query"])
            citations = result.get("citations", [])
            provider = result.get("provider", "unknown")
            fallback = result.get("fallback_used", False)

            print(f"Provider: {provider} | Fallback Used: {fallback}")
            print(f"Citations Returned ({len(citations)}):")
            for c in citations:
                print(f"  - [{c['source_type']}] slug='{c['slug']}' -> '{c['title']}'")

            print("\nAnswer Snippet:")
            ans_lines = result["answer"].strip().split("\n")
            print("\n".join(ans_lines[:6]))
            if len(ans_lines) > 6:
                print("  ...")

            passed = tc["check"](citations)
            if passed:
                print(f"\n[PASS] {tc['description']}")
            else:
                print(f"\n[FAIL] {tc['description']}")
                all_passed = False
            print("-" * 60)

    if not all_passed:
        print("\nERROR: One or more citation verification checks failed!")
        sys.exit(1)
    else:
        print("\nALL 4 CITATION ACCURACY CHECKS PASSED!")

if __name__ == "__main__":
    asyncio.run(main())
