# TASKS.md — Phased Implementation & Verification Roadmap (`shreyas-portfolio`)

## 1. Execution Rules for the Antigravity IDE Agent (Non-Negotiable)

1. **Strictly One Phase at a Time:** Never attempt to build multiple phases in a single turn. Complete all checkboxes in the active phase, run its **Deterministic Verification Gate**, and wait for human confirmation before advancing to the next phase.
2. **Spec Pack Source of Truth:** Before generating any file, cross-check against `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/SCHEMA.md`, and `docs/API_AND_SECURITY.md`.
3. **Terminal & Dependency Hygiene:**
   - Default shell: `PS C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio>`
   - **Rule A (Global CLI/MCPs):** Never run bare `npm install` in the root or `/backend` folder. Global CLIs/MCPs must use `npm install -g <pkg>` or `npx -y`.
   - **Rule B (Scoped Project Dependencies):** Python dependencies live strictly inside `backend/.venv`. Frontend Node/Three.js packages live strictly inside `frontend/node_modules`.
4. **Automated vs. Manual Gate Separation:** The IDE agent executes all `[AUTO]` tasks autonomously and pauses only at `[MANUAL]` checkpoints requiring human browser clicks, API key entry, or visual DBeaver/CodeRabbit inspection.

---

## 2. Pre-Flight Gate: Automated vs. Manual Connection Setup

### 2.1 Automated Setup (`[AUTO]` — Antigravity IDE Agent)
- [x] `[AUTO]` Create monorepo directory tree (`backend/`, `frontend/`, `content/`, `docs/`, `bruno/`, `.github/workflows/`).
- [x] `[AUTO]` Generate root `.gitignore` excluding `.env`, `.venv/`, `node_modules/`, `.next/`, `__pycache__/`, and `.pytest_cache/`.
- [x] `[AUTO]` Generate root `.env.example` with safe local defaults (`DATABASE_URL`, `REDIS_URL`, Cloudflare Turnstile test keys `1x00000000000000000000AA` / `1x0000000000000000000000000000000AA`, and generated 32-byte hex placeholders).

### 2.2 Manual Human Checklist (`[MANUAL]` — Shreyas)
- [ ] `[MANUAL]` **MCP Scope Check:** In Antigravity IDE, keep **`context7`**, **`postgres`**, **`sentry`**, **`figma`**, and **`playwright`** enabled; disable `dart-flutter` to save context tokens.
- [ ] `[MANUAL]` **Stop Conflicting Local Containers:** If another project is currently running on port `5432` or `6379`, run `docker compose down` in that project first.
- [ ] `[MANUAL]` **Populate `.env`:** Copy `.env.example` to `.env`. For Phase 1 and Phase 2 local testing, the built-in Cloudflare Turnstile dummy test keys work out of the box; add your fine-grained `GITHUB_PAT` and `GEMINI_API_KEY` / `GROQ_API_KEY` before Phase 3.

---

## 3. Phase 1: Infrastructure, Postgres + `pgvector` Schema, & Ground-Truth Seed

**Goal:** Boot the zero-config local Docker stack (`localhost:5432/postgres` and `localhost:6379`), run async Alembic migrations to create all 8 tables with B-tree and HNSW indexes, and seed Shreyas's verified portfolio data from `/content/portfolio_data.json`.

### 3.1 Tasks
- [x] **Task 1.1 (`[AUTO]` Root Docker Compose):** Create `docker-compose.yml` defining:
  - `shreyas_portfolio_postgres` (`pgvector/pgvector:pg15`, port `5432:5432`, user/pass/db `postgres`, volume `shreyas_portfolio_pgdata`, `pg_isready` healthcheck).
  - `shreyas_portfolio_redis` (`redis:7-alpine`, port `6379:6379`, volume `shreyas_portfolio_redisdata`, `redis-cli ping` healthcheck).
- [x] **Task 1.2 (`[AUTO]` Python Virtualenv & Dependencies):** Inside `backend/`, initialize `backend/.venv` and create `pyproject.toml` / `requirements.txt` with `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]>=2.0`, `asyncpg`, `psycopg[binary]`, `alembic`, `pgvector`, `pydantic>=2.0`, `pydantic-settings`, `redis`, `httpx`, `pytest`, `pytest-asyncio`, `ruff`, `pyright`, and `bandit`.
- [x] **Task 1.3 (`[AUTO]` Ground-Truth Seed Manifest):** Create `/content/portfolio_data.json` containing all verified records specified in `docs/SCHEMA.md` Section 7:
  - Candidate Profile: Chemakoora Shreyas Reddy, ICFAI Tech B.Tech CSE (AI) 2027, LinkedIn (`https://www.linkedin.com/in/shreyas-reddy-8a7512285`), masked and cleartext contact fields (`shreyas.chemakoora@gmail.com`, `+91 9346759117`).
  - 6 Flagship Projects: **SecureRAG**, **DataMind**, **Project Sentinel**, **Denoising Prior to Edge Detection**, **Telugu Digital Archive (`telarc`)**, and **Folkbattle** with 3D archetype configs and pre-populated `ai_explainer` JSONB objects.
  - 3 Experiences: **Tech Lead at Viswam.ai** (200+ interns directed), **Core Technical Lead at Team CODEX**, and **B.Tech CSE (AI) at ICFAI Tech**.
  - 3 Hackathons: **Smart India Hackathon (SIH) 2025**, **Cybersecurity Hackathon 2025 (Project Sentinel)**, and **SOAI Hackathon 2025 (Folkbattle)**.
  - 6 Verified Certificates: **Microsoft Azure AI-901**, **Google Cloud Gen AI Academy**, **NVIDIA DLI (Autonomous Robotics & Prompt Engineering)**, **Kaggle AI Agents Intensive**, **NASSCOM FutureSkills Prime**, and **IBM SkillsBuild Cybersecurity Fundamentals**.
- [x] **Task 1.4 (`[AUTO]` SQLAlchemy 2.0 Models & Database Engine):**
  - Create `backend/app/core/config.py` (fail-fast `Settings` class from `docs/API_AND_SECURITY.md`).
  - Create `backend/app/core/database.py` (async engine + `AsyncSession` generator).
  - Create `backend/app/models/portfolio.py` implementing all 8 tables (`candidate_profile`, `projects`, `experiences`, `hackathons`, `certificates`, `portfolio_embeddings`, `webhook_deliveries`, `contact_submissions`).
- [x] **Task 1.5 (`[AUTO]` Alembic Migrations & Seed Execution):**
  - Configure `backend/alembic.ini` and `backend/alembic/env.py` to load `settings.DATABASE_URL`.
  - Generate `0001_initial_schema_and_pgvector.py` (enables `pgcrypto` + `vector`, creates 8 tables + all B-tree/partial/HNSW indexes).
  - Generate `0002_seed_shreyas_ground_truth.py` (idempotently upserts `/content/portfolio_data.json` via `ON CONFLICT DO UPDATE`).
  - Run `alembic upgrade head`.

### 3.2 Phase 1 Deterministic Verification Gate
Run inside `PS C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio>`:

    # 1. Boot containers and verify healthy status:
    docker compose up -d
    docker ps --filter "name=shreyas_portfolio"

    # 2. Verify pgvector extension and all 8 tables exist:
    docker exec -it shreyas_portfolio_postgres psql -U postgres -d postgres -c "\dx"
    docker exec -it shreyas_portfolio_postgres psql -U postgres -d postgres -c "\dt"

    # 3. Verify seeded flagship project, experience, hackathon, and certificate counts:
    docker exec -it shreyas_portfolio_postgres psql -U postgres -d postgres -c "SELECT (SELECT COUNT(*) FROM projects) AS projects, (SELECT COUNT(*) FROM experiences) AS experiences, (SELECT COUNT(*) FROM hackathons) AS hackathons, (SELECT COUNT(*) FROM certificates) AS certificates;"

- [ ] `[MANUAL]` **DBeaver Check:** Open **DBeaver** (`localhost:5432/postgres`), refresh tables, and visually inspect the ER diagram and HNSW index `ix_portfolio_embeddings_hnsw_cosine`.

---

## 4. Phase 2: FastAPI Security Perimeter, Redis Rate Limiter, & Bruno Abuse Suite

**Goal:** Build the hardened FastAPI backend with 0 login routes, `1 MB` payload cap, OWASP security headers, Redis sliding-window rate limiting, Turnstile PII protection, HMAC-SHA256 GitHub webhook verification, and deterministic Bruno tests.

### 4.1 Tasks
- [x] **Task 2.1 (`[AUTO]` Redis Sliding-Window Guard & Cache):** Implement `backend/app/core/redis_guard.py`:
  - Atomic sorted-set sliding-window rate limiter (`check_rate_limit(scope, ip_sha256, limit, window_sec)`).
  - Public portfolio JSON cache helper (`get_or_set_cache` with `3600s` TTL and `invalidate_portfolio_cache()`).
  - Webhook delivery idempotency lock (`acquire_webhook_delivery_lock(delivery_id)`).
  - Daily global AI token circuit breaker (`consume_ai_tokens(count)` capped at `settings.DAILY_AI_TOKEN_BUDGET`).
- [x] **Task 2.2 (`[AUTO]` Cryptographic Security & SSRF Helpers):** Implement `backend/app/core/security.py`:
  - `hash_client_ip(ip: str) -> str` using `HMAC-SHA256` with `settings.IP_HASH_PEPPER`.
  - `verify_github_webhook_signature(request: Request) -> bytes` using `hmac.compare_digest` on raw request bytes.
  - `verify_turnstile_token(token: str, remote_ip: str) -> bool` calling `https://challenges.cloudflare.com/turnstile/v0/siteverify`.
  - `validate_outbound_url(url: str)` blocking private/loopback RFC1918 and cloud metadata IPs (`127.0.0.0/8`, `10.0.0.0/8`, `169.254.169.254`).
- [x] **Task 2.3 (`[AUTO]` Strict Pydantic v2 Schemas):** Create `backend/app/schemas/portfolio.py` with `ConfigDict(extra="forbid", str_strip_whitespace=True)` on all request schemas (`ContactRevealRequest`, `AgentChatRequest`, `ContactSubmissionRequest`) and clean read schemas that exclude `email_cleartext` and `phone_cleartext` from public bundle endpoints.
- [x] **Task 2.4 (`[AUTO]` Public, Contact, & Webhook Routers):**
  - `backend/app/api/v1/public.py`: `GET /api/v1/health`, `GET /api/v1/public/portfolio`, `GET /api/v1/public/projects/{slug}`, `GET /api/v1/public/manifest`, and `POST /api/v1/public/contact-reveal`.
  - `backend/app/api/v1/contact.py`: `POST /api/v1/contact` (`3 req / hr` rate limit + Turnstile verification).
  - `backend/app/api/v1/webhooks.py`: `POST /api/v1/webhooks/github` (HMAC verification + `X-GitHub-Delivery` replay protection + audit logging in `webhook_deliveries`).
- [x] **Task 2.5 (`[AUTO]` FastAPI Main App & Middleware Stack):** Create `backend/app/main.py` registering the 5 middleware layers (Request ID + PII-redacted JSON logging, `1 MB` payload ceiling returning `413`, strict CORS, OWASP security headers, and unified error envelopes).
- [x] **Task 2.6 (`[AUTO]` Bruno API & Security Abuse Collection):** Generate `/bruno/bruno.json`, `/bruno/environments/local.bru`, and all 6 `.bru` test files specified in `docs/API_AND_SECURITY.md` Section 7.

### 4.2 Phase 2 Deterministic Verification Gate
Run inside `PS C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio>`:

    # 1. Start FastAPI server from backend/.venv:
    .\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000

    # 2. Verify Health & Public Portfolio (confirm cleartext PII is NOT exposed):
    curl -i http://localhost:8000/api/v1/health
    curl -s http://localhost:8000/api/v1/public/portfolio | Select-String -Pattern "email_cleartext"

    # 3. Verify Forged GitHub Webhook is rejected with 401 Unauthorized:
    curl -i -X POST http://localhost:8000/api/v1/webhooks/github -H "Content-Type: application/json" -H "X-Hub-Signature-256: sha256=0000" -d "{\"zen\":\"hack\"}"

- [ ] `[MANUAL]` **Bruno Security Gate:** Open **Bruno**, load `/bruno`, and verify all 6 tests pass (`200` happy path, `401` forged webhook HMAC, `200` duplicate webhook idempotency, `422` mass-assignment block, `403` invalid Turnstile token, `429` rate-limit trip).

---

## 5. Phase 3: Bounded AI Agent ("Ask Shreyas AI") & Bi-Directional GitHub Auto-Sync

**Goal:** Build the GitHub repository synchronization service, pre-computed AI Repo Explainer worker, `pgvector` HNSW RAG assistant with 128-bit hex nonce delimiters, and the automated GitHub Profile `README.md` sync Action.

### 5.1 Tasks
- [x] **Task 3.1 (`[AUTO]` 128-Bit Nonce Guard & AI Provider Router):** Implement `backend/app/services/repo_explainer.py`:
  - Supports local `Ollama` (`llama3.2` / `nomic-embed-text`) in development and `Gemini 2.5 Flash` / `Groq` in production.
  - Wraps untrusted repository README text inside `secrets.token_hex(16)` delimiters and extracts structured `problem_statement`, `architecture_stack`, and `engineering_highlights` JSON.
  - Computes 768-dim vectors only when `sha256(chunk_text)` differs from `portfolio_embeddings.content_hash`.
- [x] **Task 3.2 (`[AUTO]` Live GitHub Repository Sync Service):** Implement `backend/app/services/github_sync.py`:
  - Fetches Shreyas's public repositories from `https://api.github.com/users/{GITHUB_USERNAME}/repos` via SSRF-guarded `httpx.AsyncClient`.
  - Preserves flagship metadata (`is_flagship = TRUE`) while dynamically upserting all public repositories (`is_auto_synced = TRUE`), updating star/fork counts, generating missing AI Repo Explainers, indexing `portfolio_embeddings`, and purging Redis cache.
- [x] **Task 3.3 (`[AUTO]` Bounded "Ask Shreyas AI" RAG Endpoint):** Implement `backend/app/services/rag_agent.py` and `backend/app/api/v1/agent.py` (`POST /api/v1/agent/chat`):
  - Enforces Turnstile verification, `5 req / 10 min` IP rate limit, `500-char` input cap, `max_steps=3`, `10s` timeout, and `build_nonce_guarded_prompt()`.
  - Queries top-4 cosine matches from `portfolio_embeddings` using `pgvector` `<=>` operator.
  - Includes automatic zero-crash fallback returning structured citations directly from PostgreSQL if the daily LLM token circuit breaker trips.
- [x] **Task 3.4 (`[AUTO]` Bi-Directional GitHub Profile `README.md` Sync Action):**
  - Create `backend/scripts/render_profile_readme.py` and `.github/workflows/sync-github-profile.yml`.
  - Fetches `/api/v1/public/manifest` (or `/content/portfolio_data.json`), formats Markdown tables for Flagship Systems, Auto-Synced Repos, Hackathons, and Certifications, and updates `<!-- PORTFOLIO-SYNC:START --> ... <!-- PORTFOLIO-SYNC:END -->` in `<github_username>/<github_username>/README.md`.
- [x] **Task 3.5 (`[AUTO]` Async Pytest Suite):** Create `backend/tests/test_security_and_sync.py` testing HMAC verification, hex nonce prompt wrapping, SSRF private-IP blocking, rate-limit sliding window, and fallback RAG retrieval.

### 5.2 Phase 3 Deterministic Verification Gate
Run inside `PS C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio>`:

    # 1. Run initial seed embedding indexer & verify pgvector rows:
    Push-Location backend; .\.venv\Scripts\python.exe -m app.services.seed_embeddings; Pop-Location
    docker exec -it shreyas_portfolio_postgres psql -U postgres -d postgres -c "SELECT source_type, COUNT(*) FROM portfolio_embeddings GROUP BY source_type;"

    # 2. Run Pytest security and sync unit tests:
    .\backend\.venv\Scripts\pytest.exe backend/tests -v

---

## 6. Phase 4: Next.js 15 + Persistent 3D WebGL Scenes across All 5 Tabs

**Goal:** Build the complete Next.js 15 frontend with a single shared React Three Fiber `<PersistentCanvas />` (`@react-three/drei` `<View.Port />`), Anti-Vibecode architectural UI, Recruiter Command Bar, and Technical SEO.

### 6.1 Tasks
- [x] **Task 4.1 (`[AUTO]` Scoped Next.js 15 & Three.js Setup):** Inside `frontend/`, initialize Next.js 15 (App Router, TypeScript, Tailwind CSS) and install `three`, `@types/three`, `@react-three/fiber`, `@react-three/drei`, `framer-motion`, and `lucide-react` strictly inside `frontend/package.json`.
- [x] **Task 4.2 (`[AUTO]` Design Tokens & Anti-Vibecode Theme):** Configure `frontend/tailwind.config.ts` and `globals.css`:
  - Deep carbon slate `#0B0F17` primary canvas background, `#111827` surface cards, `#1E293B` hairlines, `#06B6D4` precision cyan, `#10B981` emerald status badges, `#FAFAFA` primary text, and `Geist` + `Geist Mono` font pairing.
- [x] **Task 4.3 (`[AUTO]` Single Persistent `<Canvas>` & Error Boundary):**
  - Build `frontend/src/components/canvas/PersistentCanvas.tsx` with `<Canvas dpr={[1, 1.5]}>`, `<AdaptiveDpr pixelated />`, `<AdaptiveEvents />`, `document.hidden` pause listener, and `<View.Port />`.
  - Build `frontend/src/components/canvas/SceneErrorBoundary.tsx` providing a clean 2D CAD wireframe SVG fallback if WebGL is disabled.
  - Mount inside `frontend/src/app/layout.tsx` alongside the persistent `RecruiterBar.tsx` and floating `AskShreyasDrawer.tsx`.
- [x] **Task 4.4 (`[AUTO]` Build All 5 3D Scenes & Route Pages):**
  - **`/` (`page.tsx` + `NeuralHubScene.tsx`):** Interactive 3D force-directed system node graph connecting *Agentic AI & RAG*, *Cybersecurity & Zero-Trust*, and *Full-Stack & Cloud*, plus 1-click Recruiter Bar (LinkedIn, GitHub, Resume PDF, Turnstile-verified Email & Phone copy).
  - **`/projects` (`projects/page.tsx` + `ProjectBlueprintsScene.tsx`):** 3D wireframe architecture cards for the 6 Flagship Systems (**SecureRAG**, **DataMind**, **Project Sentinel**, **Denoising Workbench**, **`telarc`**, **Folkbattle**) + Live Auto-Synced GitHub Vault displaying AI-Generated Repo Explainers.
  - **`/experience` (`experience/page.tsx` + `TimelineAxisScene.tsx`):** Scroll-driven 3D Z-axis career spline highlighting **Viswam.ai Tech Lead (200+ interns)**, **Team CODEX**, and **ICFAI Tech B.Tech CSE (AI)**.
  - **`/hackathons` (`hackathons/page.tsx` + `HackathonArenaScene.tsx`):** 3D spatial arena showcasing **Smart India Hackathon (SIH) 2025**, **Cybersecurity Hackathon 2025**, and **SOAI Hackathon 2025**.
  - **`/certificates` (`certificates/page.tsx` + `CertVaultScene.tsx`):** Interactive 3D credential matrix with category filtering (*All*, *AI & Agents*, *Cloud Architecture*, *Cybersecurity*, *Data Science*) and direct credential verification links.
- [x] **Task 4.5 (`[AUTO]` Technical SEO, Legal Routes, & AI Discoverability):**
  - Generate `/privacy` and `/terms` routes, `sitemap.ts`, `robots.ts`, `public/llms.txt` (structured summary of Shreyas's profile for AI recruiter agents), OpenGraph tags, and JSON-LD `Person` + `SoftwareSourceCode` schema markup.
  - Add `/api/revalidate/route.ts` verified with `NEXTJS_REVALIDATE_SECRET` for instant ISR updates on GitHub webhook sync.

### 6.2 Phase 4 Deterministic Verification Gate
Run inside `PS C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio\frontend>`:

    # 1. Verify TypeScript compilation and production Next.js build:
    npm run build

    # 2. Start frontend dev server on http://localhost:3000:
    npm run dev

- [x] **Playwright MCP Audit (`[AUTO]`):** Run Playwright MCP across `/`, `/projects`, `/experience`, `/hackathons`, and `/certificates`, switching between tabs 10 times consecutively to verify:
  1. Zero browser `console.error` messages and zero `CONTEXT_LOST_WEBGL` warnings.
  2. Exactly **one** `<canvas>` element exists in the DOM across all route transitions.
  3. Mobile viewport (`390x844`) and Desktop viewport (`1440x900`) render cleanly with zero horizontal overflow.

---

## 7. Phase 5: Security Audit (`gitleaks`/`bandit`), CodeRabbit PR, & $0 Cloud Launch

**Goal:** Pass static analysis and secret-scanning gates, review diffs with GitLens and CodeRabbit, deploy to $0 student cloud tiers, and connect the live GitHub Webhook.

### 7.1 Tasks
- [ ] **Task 5.1 (`[AUTO]` Pre-Commit & CI Security Gate):** Create `.pre-commit-config.yaml` and `.github/workflows/ci-security-gate.yml` enforcing `ruff check`, `pyright`, `bandit -r backend/app`, and `gitleaks detect`.
- [ ] **Task 5.2 (`[AUTO]` Production Dockerfile & Deployment Manifests):** Create hardened multi-stage `backend/Dockerfile` running as a non-root user (`appuser`, UID `10001`) and `render.yaml` / `vercel.json` configuration files.
- [ ] **Task 5.3 (`[MANUAL]` GitLens & CodeRabbit Review):**
  - Inspect all staged changes in Antigravity IDE using **GitLens**.
  - Push branch via **GitHub Desktop** and open a Pull Request for automated **CodeRabbit** architectural and security review.
- [ ] **Task 5.4 (`[MANUAL]` $0 Student Cloud Deployment & Live Webhook Wiring):**
  - Provision free **Neon Postgres** (`pgvector`) and **Upstash Redis** instances; paste production URLs into **Render / Koyeb** environment variables and run `alembic upgrade head`.
  - Deploy `frontend/` to **Vercel** (or Cloudflare Pages) with `NEXT_PUBLIC_API_URL` and Cloudflare **Invisible Turnstile** keys.
  - In GitHub Settings -> Developer Settings -> Webhooks (or repository webhooks), add `https://<your-backend-domain>/api/v1/webhooks/github` with `Content-Type: application/json` and your `GITHUB_WEBHOOK_SECRET`.

---

## 8. Senior Engineering "Why" & Final Spec Pack Verification

### Senior Engineering Trade-Offs
1. **Why Enforce a 5-Phase Gate Instead of Generating Backend and 3D Frontend Simultaneously?**
   - Building React Three Fiber scenes before the Pydantic schemas and `JSONB` contracts (`model_3d_config`, `ai_explainer`) are locked in PostgreSQL causes mismatched TypeScript interfaces and broken props. Verifying the database (Phase 1) and API security contracts in Bruno (Phase 2) first guarantees the 3D frontend binds to 100% real, schema-validated data on the first build.
2. **Why Verify Single-Canvas Persistence with a 10-Tab-Switch Playwright Loop?**
   - Memory leaks in WebGL only manifest after 8 to 12 route transitions when browser garbage collection fails to free orphaned GPU contexts. Automating a 10-switch loop in Playwright catches accidental duplicate `<Canvas>` mounts before any recruiter ever visits the site.

### PowerShell Verification Commands (Confirm All 5 Spec Files Are Complete)
Save this file and run the following commands in `PS C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio>` to confirm your complete Spec Pack is locked and ready for Phase 1 execution:

    # Verify all 5 foundational specification files exist and check sizes:
    Get-ChildItem -Path .\AGENTS.md, .\docs\ARCHITECTURE.md, .\docs\SCHEMA.md, .\docs\API_AND_SECURITY.md, .\docs\TASKS.md | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize