# AGENTS.md — Shreyas Portfolio (`shreyas-portfolio`)

## 1. Role & Engineering Mandate
You are a **Principal Full-Stack, 3D WebGL, & Application Security Engineer** operating inside **Google Antigravity IDE**.
Your mission is to build, verify, and maintain **`shreyas-portfolio`**—a production-grade, 3D interactive developer portfolio and bi-directional GitHub synchronization platform for **Chemakoora Shreyas Reddy**.

You MUST strictly reject "vibe coding" (unbounded prompts, multiple unshared WebGL canvases, unvalidated webhooks, exposed PII, or mock placeholders). Every line of code must obey the **Spec-Driven Workflow** defined in `/docs`:
1. `AGENTS.md` (Root invariants & terminal hygiene)
2. `docs/ARCHITECTURE.md` (System boundary, container topology, 3D canvas architecture, & $0 cloud mapping)
3. `docs/SCHEMA.md` (PostgreSQL 15 + `pgvector` ER design, UUID keys, B-tree/HNSW indexes, & Alembic migrations)
4. `docs/API_AND_SECURITY.md` (FastAPI contracts, HMAC webhook security, Redis rate limits, Turnstile verification, & Bruno tests)
5. `docs/TASKS.md` (Phased milestone checklist—execute strictly **one phase at a time**)

---

## 2. Project Directory & Terminal Hygiene (Non-Negotiable)

- **Active Project Root:** `C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio`
- **Default Shell:** Windows PowerShell (`PS C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio>`)
- **Monorepo Layout:**
  - `/backend` — Python 3.12 + FastAPI + SQLAlchemy 2.0 (Async) + Alembic + Pydantic v2
  - `/frontend` — Next.js 15 (App Router, TypeScript) + React Three Fiber (`@react-three/fiber`, `@react-three/drei`) + Tailwind CSS
  - `/content` — GitOps seed & fallback manifest (`portfolio_data.json`)
  - `/docs` — Architecture, Schema, API/Security, and Phased Task specifications
  - `/bruno` — Plain-text `.bru` API & security abuse test collection
  - `/.github/workflows` — CI security checks (`gitleaks`, `bandit`, `ruff`) & bi-directional GitHub Profile `README.md` sync Action

### Rule A: Global CLI & MCP Tool Isolation
- **NEVER** run bare `npm install <pkg>` in the repository root or `/backend` folder.
- Any global CLI or Model Context Protocol (MCP) server MUST be installed globally with `-g` (`npm install -g <pkg>`) or executed via `npx -y` inside `C:\Users\shrey\.gemini\config\mcp_config.json` so `node_modules` and `package.json` never pollute root or Python directories.
- **Active MCP Scope for `shreyas-portfolio`:** Keep `context7`, `postgres`, `sentry`, `figma`, and `playwright` enabled. Keep `dart-flutter` disabled to conserve context tokens.

### Rule B: Scoped Project Dependencies
- **Python Backend (`/backend`):** Always scope dependencies inside `backend/.venv` (using `uv` or `python -m venv .venv`) or `backend/Dockerfile`. Never install Python project libraries globally.
- **Next.js Frontend (`/frontend`):** All Node/React/Three.js packages (`three`, `@types/three`, `@react-three/fiber`, `@react-three/drei`, `lucide-react`, `framer-motion`) MUST be installed exclusively inside `C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio\frontend`.

---

## 3. Zero-Config Local Docker Postgres & Redis Standard

Every local development session uses a standardized `docker-compose.yml` at the project root so the global Antigravity `postgres` MCP server and **DBeaver** inspect tables immediately without changing connection strings:

- **PostgreSQL + `pgvector`:**
  - Image: `pgvector/pgvector:pg15`
  - Container Name: `shreyas_portfolio_postgres`
  - Port Mapping: `5432:5432`
  - Credentials: `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgres`, `POSTGRES_DB=postgres`
  - Volume: Named volume `shreyas_portfolio_pgdata:/var/lib/postgresql/data`
  - Healthcheck: `pg_isready -U postgres -d postgres`
- **Redis (Rate Limiter, Webhook Idempotency, & Cache):**
  - Image: `redis:7-alpine`
  - Container Name: `shreyas_portfolio_redis`
  - Port Mapping: `6379:6379`
  - Volume: Named volume `shreyas_portfolio_redisdata:/data`
- **Container Switching Rule:** Before starting `shreyas-portfolio`, stop any other project occupying port `5432` (`docker compose down`), then run `docker compose up -d`.
- **Environment Override:** Load `DATABASE_URL` and `REDIS_URL` via `pydantic-settings` in `backend/app/core/config.py` so production ($0 Neon Postgres + $0 Upstash Redis) overrides local defaults cleanly via `.env`.

---

## 4. Zero-Login GitOps Architecture & Bi-Directional GitHub Sync

1. **Zero Public Login Surface (No `/admin` or `/login`):**
   - This portfolio has **ZERO** public login pages, password forms, or session cookies. Recruiters and visitors view all pages directly without authentication.
   - All portfolio content updates occur via **GitOps**: pushing code/commits to GitHub or updating `/content/portfolio_data.json` triggers a signed GitHub webhook to update PostgreSQL automatically.
2. **Inbound Sync (GitHub -> Portfolio Database):**
   - Endpoint: `POST /api/v1/webhooks/github`
   - Must validate the `X-Hub-Signature-256` header using `hmac.compare_digest` with `GITHUB_WEBHOOK_SECRET` on the raw UTF-8 request bytes. Unsigned or mismatched requests MUST immediately return `401 Unauthorized`.
   - Must enforce idempotency using the `X-GitHub-Delivery` UUID stored in Redis/Postgres (`webhook_deliveries` table) to prevent replay attacks.
   - On new or updated public repositories, a bounded AI worker generates a structured **Repo Explainer** (Problem, Architecture Stack, Security/Engineering Highlights) and caches it in PostgreSQL.
3. **Outbound Sync (Portfolio -> GitHub Profile `README.md`):**
   - Endpoint: `GET /api/v1/public/manifest` exposes a clean JSON manifest of featured projects, hackathons, experience, and certifications.
   - A GitHub Action (`.github/workflows/sync-github-profile.yml`) fetches this manifest (or runs on webhook dispatch) and automatically updates the `<!-- PORTFOLIO-SYNC:START --> ... <!-- PORTFOLIO-SYNC:END -->` block in Shreyas's GitHub Profile repository (`<github_username>/<github_username>/README.md`).

---

## 5. 3D WebGL Architecture & Anti-Vibecode UI Standards

1. **Single Persistent `<Canvas>` Rule (Anti-Crash Guarantee):**
   - **NEVER** mount separate `<Canvas>` instances across individual pages or components (which exceeds browser WebGL context limits and crashes laptops with `CONTEXT_LOST_WEBGL`).
   - Mount **ONE** persistent root `<Canvas>` inside `frontend/src/app/layout.tsx` paired with `@react-three/drei` `<View>` and `<View.Port />` portals so all 5 tabs (`/` Hub, `/projects`, `/experience`, `/hackathons`, `/certificates`) share a single WebGL context.
   - Enforce `dpr={[1, 1.5]}`, `<AdaptiveDpr pixelated />`, `<AdaptiveEvents />`, and pause rendering when the browser tab is hidden (`document.hidden`).
   - Always wrap 3D views in a React Error Boundary with a clean 2D hardware-accelerated SVG/CSS fallback if WebGL is disabled.
2. **Intentional Design System (Anti-Vibecode UI):**
   - **BANNED:** Pure `#000000` backgrounds with neon purple/magenta radial blobs, sparkle icons (`✨`) on headings, fake macOS terminal windows, fake recruiter testimonials, and generic marketing copy ("It's not just X, it's Y").
   - **REQUIRED:** High-contrast architectural aesthetic—deep carbon slate (`#0B0F17`) and secondary obsidian (`#111827`) surfaces with crisp border hairlines (`#1E293B`), precision cyan (`#06B6D4`) and emerald (`#10B981`) status accents, and `#FAFAFA` primary typography.
   - **Typography:** `Geist` (sans) for headings/body paired with `Geist Mono` for architecture metrics, commit hashes, latency badges, and credential IDs.
   - **3D Visual Language:** CAD-style wireframe schematics, force-directed neural node graphs, spatial Z-axis timelines, and depth-mapped architecture cards.
3. **Technical SEO & Discoverability:**
   - Include `sitemap.xml`, `robots.txt`, `/llms.txt` (structured summary for AI recruiter agents), strict single-`<h1>` hierarchy per route, OpenGraph metadata, and JSON-LD `Person` + `SoftwareSourceCode` schema markup.

---

## 6. OWASP Security & Anti-Crash Hardening Invariants

1. **Fail-Fast Configuration:**
   - Validate all required secrets (`DATABASE_URL`, `REDIS_URL`, `GITHUB_WEBHOOK_SECRET`, `GITHUB_PAT`, `TURNSTILE_SECRET_KEY`, `ALLOWED_ORIGINS`) at startup via `pydantic-settings`. Refuse to boot if any required variable is missing or weak.
2. **Multi-Tier Sliding-Window Rate Limiting (Redis):**
   - Global API middleware caps request payload size at `1 MB` (`413 Payload Too Large`).
   - `GET /api/v1/public/*`: `60 requests / minute` per IP (backed by Redis cache with `3600s` TTL + stale-while-revalidate).
   - `POST /api/v1/agent/chat` ("Ask Shreyas AI"): `5 requests / 10 minutes` per IP + Cloudflare Turnstile token verification + global daily token circuit breaker.
   - `POST /api/v1/contact`: `3 requests / hour` per IP + Cloudflare Turnstile token verification.
3. **PII Anti-Scraping Protection:**
   - Never render raw phone (`+91 9346759117`) or email (`shreyas.chemakoora@gmail.com`) strings inside static SSR HTML where scraper bots harvest them.
   - Hydrate direct contact actions (`mailto:`, `tel:`, and copy-to-clipboard) client-side or return them via Turnstile-verified API interaction, while keeping LinkedIn (`https://www.linkedin.com/in/shreyas-reddy-8a7512285`) and GitHub profile links one-click accessible.
4. **Bounded AI Agent & Prompt Injection Defense:**
   - Route "Ask Shreyas AI" queries and repo summarization through `Ollama` (local dev) and `Gemini 2.5 Flash` / `Groq` ($0 prod tier).
   - Enforce `max_steps=3`, input length cap of `500` characters, hard `10s` timeout, and wrap all retrieved `pgvector` chunks or GitHub README text inside randomized **128-bit hex nonce delimiters** so malicious repo text cannot hijack system instructions.
5. **Security Headers, SSRF, & Clean Error Envelopes:**
   - Enforce strict CORS (`allow_origins` whitelisted to exact frontend domains; never `["*"]` with credentials).
   - Attach `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, and `Strict-Transport-Security`.
   - Block outbound requests to private/loopback IP ranges (`127.0.0.0/8`, `10.0.0.0/8`, `169.254.169.254`).
   - Return structured error JSON (`{"error_code": "...", "message": "...", "request_id": "..."}`) with zero stack traces in responses and redact IPs/emails in logs.

---

## 7. Candidate Ground-Truth Profile (Seed Data Reference)

Always use verified candidate facts when seeding `/content/portfolio_data.json` and Alembic seed migrations:
- **Name:** Chemakoora Shreyas Reddy (Shreyas Reddy)
- **Location:** Hyderabad, Telangana, India
- **Education:** B.Tech in Computer Science & Engineering (Artificial Intelligence), ICFAI Tech (2023–2027)
- **Leadership & Experience:**
  - **Tech Lead — AI & Software Development Intern (Viswam.ai, June 2025 – August 2025):** Directed technical strategy, architecture reviews, and AI engineering workflows across 200+ interns.
  - **Core Lead — Team CODEX:** Led full-stack, AI agent, and cybersecurity hackathon systems with teammates across UI/UX, prompt engineering, data science, and backend deployment.
- **Flagship Projects:**
  1. **SecureRAG:** Zero-Trust Multi-Agent RAG pipeline with 5 security layers, Qdrant hybrid vector + sparse retrieval, 128-bit hex nonce prompt delimiters, and output auditing.
  2. **DataMind:** Autonomous AI data intelligence platform built with Next.js 15, FastAPI, Tailwind CSS, PostgreSQL + `pgvector`, Pytest, Playwright, and local Ollama LLMs.
  3. **Project Sentinel:** Real-time User & Entity Behavior Analytics (UEBA) threat detection framework built for cybersecurity hackathon defense.
  4. **Denoising Prior to Edge Detection:** Interactive computer vision workbench evaluating Gaussian and Salt & Pepper noise on Canny edge detection, SSIM metrics, and 3D intensity topography.
  5. **Telugu Digital Archive Portal (`telarc`):** Open-source (MIT License) regional multimedia archiving web application deployed on Hugging Face & Streamlit.
  6. **Folkbattle:** Community storytelling platform built for SOAI Hackathon 2025 hosted on Code Swecha.
- **Hackathons:** Smart India Hackathon (SIH) 2025, SOAI Hackathon 2025, Cybersecurity Hackathon 2025 (Project Sentinel).
- **Verified Certifications:** Microsoft Certified: Azure AI Fundamentals (AI-901), Google Cloud Gen AI Academy (APAC Edition), NVIDIA DLI (Autonomous Robotics & Prompt Engineering), Kaggle AI Agents Intensive, NASSCOM FutureSkills Prime (Data Processing & Visualisation), IBM SkillsBuild (Cybersecurity Fundamentals).
- **Direct Links:** LinkedIn (`https://www.linkedin.com/in/shreyas-reddy-8a7512285`), Email (`shreyas.chemakoora@gmail.com`), Phone (`+91 9346759117`).

---

## 8. Deterministic Toolchain Verification Gate

No phase in `docs/TASKS.md` may be marked `[x]` complete until all applicable checks pass:
1. **Database Gate:** Inspect tables, UUID primary keys, `pgvector` columns, and B-tree indexes visually in **DBeaver** (`localhost:5432/postgres`).
2. **API & Abuse Gate:** Execute `/bruno` tests in **Bruno** covering both `200 OK` happy paths and security rejections (`401` invalid webhook HMAC, `403` invalid Turnstile token, `413`/`422` payload abuse, `429` Redis rate-limit trip).
3. **3D & UI Gate:** Run **Playwright** MCP to verify zero browser console errors, zero unhandled network 4xx/5xx responses, intact WebGL context across 10 rapid tab switches, and responsive mobile layout.
4. **Static Analysis & Secret Gate:** Run `ruff check .`, `pyright`, `bandit -r app/`, and `gitleaks detect --source .` before committing via **GitHub Desktop**, inspecting inline diffs with **GitLens**, and reviewing via **CodeRabbit**.