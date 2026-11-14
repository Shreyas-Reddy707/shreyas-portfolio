# ARCHITECTURE.md — System, 3D WebGL, & Security Topology (`shreyas-portfolio`)

## 1. Executive System Boundary & Architectural Mandate
`shreyas-portfolio` is a zero-login, self-updating, 3D spatial developer portfolio and bi-directional GitHub synchronization platform built for **Chemakoora Shreyas Reddy**.

The architecture solves four critical failure modes found in typical cloud-generated portfolios (such as Emergent builds):
1. **Zero WebGL Context Crashes:** Eliminates multi-canvas GPU memory leaks (`CONTEXT_LOST_WEBGL`) by mounting a single persistent root `<Canvas>` in Next.js 15 App Router and projecting per-page 3D scenes into DOM containers via `@react-three/drei` `<View>` portals.
2. **Zero Authentication Attack Surface:** Eliminates `/admin` and `/login` routes entirely. All portfolio state mutations occur via cryptographically signed **GitOps** webhooks (`X-Hub-Signature-256` HMAC-SHA256) from GitHub.
3. **Zero Rate-Limit or Bot Outages:** Visitors never trigger direct uncached requests to `api.github.com` or raw LLM endpoints. All public reads are served via Next.js Incremental Static Regeneration (ISR) and Redis cache, protected by Cloudflare WAF, Invisible Turnstile, and sliding-window IP rate limiters.
4. **Bi-Directional GitHub Profile Consistency:** Pushing a new repository, hackathon, or certificate automatically updates both the 3D portfolio database (with an AI-generated Repo Explainer) and Shreyas's public GitHub Profile `README.md` (`<github_username>/<github_username>/README.md`).

---

## 2. Monorepo Directory Topology
Active Project Root: `C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio`

    shreyas-portfolio/
    ├── AGENTS.md                           # Root AI agent invariants & terminal hygiene rules
    ├── docker-compose.yml                  # Local Postgres 15 (pgvector) + Redis 7 containers
    ├── .env.example                        # Template for fail-fast environment variables
    ├── .gitignore                          # Excludes .env, .venv, node_modules, .next, __pycache__
    ├── .pre-commit-config.yaml             # Automated gitleaks, bandit, ruff, and pyright hooks
    ├── content/
    │   └── portfolio_data.json             # GitOps source-of-truth manifest (projects, certs, hackathons)
    ├── docs/
    │   ├── ARCHITECTURE.md                 # This file — system, 3D, sync, and security topology
    │   ├── SCHEMA.md                       # PostgreSQL + pgvector ER schema & Alembic index spec
    │   ├── API_AND_SECURITY.md             # FastAPI contracts, HMAC rules, rate limits, & Bruno cases
    │   └── TASKS.md                        # 5-phase deterministic implementation checklist
    ├── bruno/                              # Plain-text .bru API & security abuse test suite
    │   ├── bruno.json
    │   ├── environments/local.bru
    │   ├── 01_health_and_manifest.bru
    │   ├── 02_webhook_hmac_reject_401.bru
    │   ├── 03_agent_rate_limit_429.bru
    │   └── 04_contact_turnstile_403.bru
    ├── .github/
    │   └── workflows/
    │       ├── ci-security-gate.yml        # Runs ruff, pyright, bandit, gitleaks, & pytest on PRs
    │       └── sync-github-profile.yml     # Pulls /api/v1/public/manifest & updates Profile README.md
    ├── backend/                            # Scoped Python 3.12 virtualenv (backend/.venv)
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── alembic.ini
    │   ├── alembic/                        # Async SQLAlchemy 2.0 migrations & seed scripts
    │   ├── app/
    │   │   ├── main.py                     # FastAPI entry, CORS, 1MB payload cap, security headers
    │   │   ├── core/
    │   │   │   ├── config.py               # Fail-fast pydantic-settings validation
    │   │   │   ├── database.py             # AsyncEngine & AsyncSession (localhost:5432/postgres)
    │   │   │   ├── redis_guard.py          # Sliding-window rate limiter, cache, & LLM circuit breaker
    │   │   │   └── security.py             # HMAC-SHA256 verification, Turnstile verify, SSRF guard
    │   │   ├── models/                     # SQLAlchemy 2.0 UUID models + pgvector(768)
    │   │   ├── schemas/                    # Strict Pydantic v2 Read/Webhook/Agent/Contact schemas
    │   │   ├── services/
    │   │   │   ├── github_sync.py          # Fetches repo README/languages & upserts Postgres
    │   │   │   ├── repo_explainer.py       # Bounded AI worker generating structured repo breakdowns
    │   │   │   └── rag_agent.py            # "Ask Shreyas AI" pgvector retrieval with hex nonce delimiters
    │   │   └── api/v1/
    │   │       ├── public.py               # GET /portfolio, /projects, /manifest, /contact-reveal
    │   │       ├── webhooks.py             # POST /webhooks/github (HMAC + Delivery UUID idempotency)
    │   │       ├── agent.py                # POST /agent/chat (Turnstile + 5 req/10m + circuit breaker)
    │   │       └── contact.py              # POST /contact (Turnstile + 3 req/hr)
    │   └── tests/                          # Pytest async unit & security abuse tests
    └── frontend/                           # Scoped Next.js 15 App Router (frontend/node_modules)
        ├── package.json
        ├── next.config.ts
        ├── tailwind.config.ts
        ├── public/
        │   ├── robots.txt
        │   ├── llms.txt                    # AI-agent readable summary of Shreyas's engineering profile
        │   └── models/                     # Compressed Draco/GLB meshes & KTX2 textures
        └── src/
            ├── app/
            │   ├── layout.tsx              # Hosts PersistentRootCanvas + Recruiter Command Bar
            │   ├── page.tsx                # "/" — 3D Neural Command Hub & Pillar Node Graph
            │   ├── projects/page.tsx       # "/projects" — Flagship Blueprints & Auto-Synced GitHub Vault
            │   ├── experience/page.tsx     # "/experience" — 3D Z-Axis Career & Viswam.ai Timeline
            │   ├── hackathons/page.tsx     # "/hackathons" — 3D Arena (SIH 2025, SOAI, Sentinel)
            │   ├── certificates/page.tsx   # "/certificates" — 3D Verified Credentials Vault
            │   ├── privacy/page.tsx        # "/privacy" — Zero-tracking & Turnstile disclosure
            │   └── terms/page.tsx          # "/terms" — Portfolio usage terms
            └── components/
                ├── canvas/
                │   ├── PersistentCanvas.tsx # Single root <Canvas> with <View.Port /> & AdaptiveDpr
                │   ├── SceneErrorBoundary.tsx # Graceful 2D schematic fallback if WebGL is unavailable
                │   ├── NeuralHubScene.tsx   # Force-directed 3D system graph for "/"
                │   ├── ProjectBlueprintsScene.tsx # 3D depth-parallax cards for "/projects"
                │   ├── TimelineAxisScene.tsx # Scroll-synced 3D camera path for "/experience"
                │   ├── HackathonArenaScene.tsx # 3D spatial showcase for "/hackathons"
                │   └── CertVaultScene.tsx   # Interactive 3D holographic grid for "/certificates"
                └── ui/
                    ├── RecruiterBar.tsx     # Always-visible GitHub, LinkedIn, Resume PDF, & Protected Contact
                    ├── AskShreyasDrawer.tsx # Floating bounded RAG recruiter assistant
                    └── ContactModal.tsx     # Invisible Turnstile-gated email/phone reveal & message form

---

## 3. $0 Student-Tier Cloud & Local Container Mapping

| Architectural Tier | Local Development (`docker-compose.yml`) | Production ($0 Student Cloud Tier) | Cost |Fail-Safe & Scaling Guarantee |
| :--- | :--- | :--- | :--- | :--- |
| **Edge DNS & Bot WAF** | Localhost direct (`127.0.0.1`) | Cloudflare Free DNS + WAF + Invisible Turnstile | $0/mo | Absorbs Layer-7 floods before hitting Next.js or FastAPI. |
| **Frontend & 3D Host** | `http://localhost:3000` (`npm run dev`) | Vercel Hobby / Cloudflare Pages | $0/mo | Global CDN edge caching; ISR serves pages even if backend sleeps. |
| **Backend API Gateway** | `http://localhost:8000` (`uvicorn`) | Render Free Web Service / Koyeb Student Tier | $0/mo | Stateless async FastAPI workers; boots with fail-fast config validation. |
| **Primary Database** | `postgres:5432` (`pgvector/pgvector:pg15`) | Neon Serverless Postgres Free Tier (`pgvector`) | $0/mo | Zero-config `localhost:5432/postgres` locally; SSL-enforced pooled URL in prod. |
| **Rate Limit & Cache** | `redis:6379` (`redis:7-alpine`) | Upstash Serverless Redis Free Tier (10k req/day) | $0/mo | Atomic Lua sliding-window rate limits + 1-hour public response cache. |
| **AI Model Routing** | Local `Ollama` (`llama3.2` / `nomic-embed-text`) | Google Gemini 2.5 Flash Free Tier + Groq Fallback | $0/mo | Repo Explainer runs only once per commit; chat capped by daily Redis budget. |
| **Telemetry & Audit** | Console structured JSON + Playwright MCP | Sentry Student Pack + Langfuse Free Tier | $0/mo | Captures WebGL context events, FastAPI 500s, and RAG token usage with PII redacted. |

### Zero-Config Local Docker Standard (`localhost:5432/postgres`)
To ensure **DBeaver** and the global Antigravity `postgres` MCP server inspect tables without reconfiguring ports or credentials across projects:
- **Container Name:** `shreyas_portfolio_postgres` on port `5432:5432`
- **Credentials:** `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgres`, `POSTGRES_DB=postgres`
- **Volume:** `shreyas_portfolio_pgdata`
- **Healthcheck:** `pg_isready -U postgres -d postgres` (interval `5s`, retries `5`)
- **Redis Container:** `shreyas_portfolio_redis` on port `6379:6379` with volume `shreyas_portfolio_redisdata`

---

## 4. Single-Canvas 3D WebGL Architecture (Anti-Crash Design)

### 4.1 The Multi-Canvas Trap vs. Persistent `<View.Port />` Architecture
Standard 3D portfolio templates instantiate a new `<Canvas>` component inside each route. Because Chromium and WebKit enforce a strict ceiling of 8 to 16 active WebGL contexts per browser process, switching between 5 portfolio tabs rapidly exhausts GPU memory and throws `WEBGL_lose_context` (`CONTEXT_LOST_WEBGL`), leaving recruiters staring at blank white boxes.

`shreyas-portfolio` enforces a **Single Persistent Root Canvas** architecture:
1. **Root Mount (`src/app/layout.tsx`):** Mounts exactly **one** `<PersistentCanvas />` fixed behind the DOM (`position: fixed; inset: 0; pointer-events: none; z-index: 0`) containing `<View.Port />` from `@react-three/drei`.
2. **Route Portals (`<View track={containerRef}>`):** Each page (`/`, `/projects`, `/experience`, `/hackathons`, `/certificates`) renders a lightweight HTML `<div ref={containerRef} />` in normal document flow and binds its 3D scene via `<View>`. `@react-three/drei` uses `gl.setScissor` and `gl.setViewport` to render only the visible DOM rectangle inside the single shared WebGL context.
3. **GPU Frame Budgeting & Thermal Guard:**
   - `dpr={[1, 1.5]}` caps pixel ratio on 4K/Retina displays so integrated laptop GPUs maintain 60 FPS.
   - `<AdaptiveDpr pixelated />` and `<AdaptiveEvents />` dynamically step down resolution during fast scroll transitions.
   - A `visibilitychange` listener switches `frameloop` to `"never"` whenever the browser tab is hidden (`document.hidden === true`), dropping background GPU utilization to 0%.
   - Geometries and materials are shared via module-level singletons and explicitly disposed on route exit.
4. **Hardware Fallback (`<SceneErrorBoundary />`):** If a recruiter's corporate browser blocks WebGL or runs in software rendering mode, `<SceneErrorBoundary />` catches context initialization errors and renders a crisp 2D SVG CAD blueprint grid so content remains 100% accessible.

### 4.2 Page-by-Page 3D Scene & Functional Specification
1. **`/` — Neural Command Hub (`NeuralHubScene.tsx`):**
   - **3D Visual:** Interactive force-directed architectural node graph representing Shreyas's three engineering pillars: *Agentic AI & RAG Systems*, *Zero-Trust Cybersecurity*, and *Full-Stack Cloud Infrastructure*. Hovering a node illuminates connected project nodes and displays real-time telemetry badges (`Geist Mono`).
   - **DOM Overlay:** Hero headline, live GitHub activity pulse, and the persistent **Recruiter Action Bar** (1-click LinkedIn, GitHub, Resume PDF download, and Turnstile-protected Email/Phone copy).
2. **`/projects` — Flagship Systems & Auto-Synced GitHub Vault (`ProjectBlueprintsScene.tsx`):**
   - **3D Visual:** Interactive 3D wireframe architecture cards with mouse-tracked tilt and layered depth planes showing system layers (e.g., SecureRAG's 5 security layers or DataMind's Next.js -> FastAPI -> pgvector pipeline).
   - **DOM Overlay:**
     - **Section A (Flagship Pinned Systems):** Deep-dive interactive architecture tabs for **SecureRAG**, **DataMind**, **Project Sentinel**, **Denoising Prior to Edge Detection**, **Telugu Digital Archive (`telarc`)**, and **Folkbattle**.
     - **Section B (Live Auto-Synced GitHub Vault):** Displays all public GitHub repositories automatically synced via webhook, complete with language breakdown, star/fork counters, last push timestamp, and the **AI-Generated Repo Explainer** (Problem Solved, Architecture Stack, and Engineering Highlights).
3. **`/experience` — 3D Spatial Career & Leadership Timeline (`TimelineAxisScene.tsx`):**
   - **3D Visual:** Scroll-linked camera flight along a 3D Z-axis spline with illuminated milestone monuments.
   - **DOM Overlay:** Detailed engineering impact metrics for **Tech Lead — AI & Software Development Intern at Viswam.ai (June 2025 – Aug 2025)** directing technical strategy for 200+ interns, **Core Lead at Team CODEX**, and **B.Tech CSE (AI) at ICFAI Tech (2023–2027)**.
4. **`/hackathons` — Hackathon Arena & Proof-of-Work (`HackathonArenaScene.tsx`):**
   - **3D Visual:** Rotating 3D wireframe polyhedrons and interactive system topology nodes per hackathon.
   - **DOM Overlay:** Case studies, problem statements, team architectures, and repository/demo links for **Smart India Hackathon (SIH) 2025**, **SOAI Hackathon 2025 (Folkbattle)**, and **Cybersecurity Hackathon 2025 (Project Sentinel)**.
5. **`/certificates` — Verified Credentials Vault (`CertVaultScene.tsx`):**
   - **3D Visual:** InstancedMesh 3D metallic/glass credential plaques arranged in a filterable spatial matrix (`All`, `AI & ML`, `Cloud`, `Cybersecurity`, `Data Science`).
   - **DOM Overlay:** Instant verification links and credential metadata for **Microsoft Certified: Azure AI Fundamentals (AI-901)**, **Google Cloud Gen AI Academy**, **NVIDIA DLI (Autonomous Robotics & Prompt Engineering)**, **Kaggle AI Agents Intensive**, **NASSCOM FutureSkills Prime**, and **IBM SkillsBuild Cybersecurity Fundamentals**.

---

## 5. Bi-Directional GitHub Auto-Sync Engine (GitOps Pipeline)

### 5.1 Flow A: Inbound Sync (GitHub -> Portfolio Database & AI Repo Explainer)
Whenever Shreyas pushes commits, creates/updates a public repository, or edits `/content/portfolio_data.json`:
1. **Webhook Delivery:** GitHub dispatches an HTTP `POST` request to `/api/v1/webhooks/github` with headers `X-GitHub-Event`, `X-GitHub-Delivery`, and `X-Hub-Signature-256`.
2. **Cryptographic HMAC Verification (`security.py`):**
   - FastAPI reads the raw request body bytes (`await request.body()`) before any JSON parsing.
   - Computes `expected = "sha256=" + hmac.new(GITHUB_WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()`.
   - Verifies `hmac.compare_digest(expected, x_hub_signature_256)`. Any missing or mismatched signature is rejected immediately with `401 Unauthorized` and logged with request metadata.
3. **Replay & Idempotency Lock (`redis_guard.py` + `webhook_deliveries`):**
   - Checks if `X-GitHub-Delivery` UUID exists in Redis (`SETNX webhook:delivery:<uuid> 1 EX 86400`) and PostgreSQL `webhook_deliveries`. Duplicate deliveries return `200 OK {"status": "duplicate_ignored"}` immediately.
4. **Metadata Fetch & Bounded AI Repo Explainer (`github_sync.py` & `repo_explainer.py`):**
   - Uses `httpx.AsyncClient` with `GITHUB_PAT` (scoped strictly to public metadata) to fetch the updated repository's `README.md`, language breakdown, topics, and latest commit SHA.
   - If the `README.md` hash changed, passes the sanitized text inside **128-bit hex nonce delimiters** to the bounded AI worker (`Gemini 2.5 Flash` in prod / `Ollama` in dev, `max_tokens=450`, `temperature=0.1`, Pydantic structured output) to generate a concise 3-part **Repo Explainer**: `problem_statement`, `architecture_stack`, and `engineering_highlights`.
   - Upserts the `projects` table and regenerates the `pgvector(768)` embedding in `portfolio_embeddings`.
5. **Cache Invalidation:** Purges the Redis key `cache:public:portfolio:v1` and sends a signed revalidation webhook to Next.js (`/api/revalidate`) so the live website updates within 2 seconds.

### 5.2 Flow B: Outbound Sync (Portfolio -> GitHub Profile `README.md`)
To keep Shreyas's GitHub Profile (`github.com/<username>`) synchronized with the portfolio website automatically:
1. **Manifest Endpoint (`GET /api/v1/public/manifest`):** Exposes a deterministic, schema-validated JSON payload containing Shreyas's top featured projects, latest auto-synced repositories, hackathon achievements, experience summary, and certifications.
2. **GitHub Action Workflow (`.github/workflows/sync-github-profile.yml`):**
   - Triggered automatically via `repository_dispatch` from FastAPI after any successful inbound webhook sync, or on a scheduled daily cron (`0 0 * * *`).
   - Fetches `/api/v1/public/manifest` (falling back to `/content/portfolio_data.json` if offline).
   - Renders clean Markdown tables for Flagship Projects, Tech Stack, Hackathons, and Certifications.
   - Replaces the block between `<!-- PORTFOLIO-SYNC:START -->` and `<!-- PORTFOLIO-SYNC:END -->` in `<github_username>/<github_username>/README.md` and commits only if `git diff --quiet` detects actual changes (preventing empty commit spam).

---

## 6. Defense-in-Depth Security, Rate-Limiting, & Anti-Crash Architecture

### 6.1 Multi-Tier Rate Limiting & Quota Circuit Breakers (`redis_guard.py`)
All state-changing or compute-heavy routes enforce atomic Redis sliding-window counters keyed by normalized client IP (`CF-Connecting-IP` when behind Cloudflare, falling back to socket IP):

| Route | Method | Rate Limit Window | Payload Cap | Additional Security Gate | Failure Code |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/api/v1/public/*` | `GET` | `60 req / 60 sec` per IP | N/A | Redis cached (`3600s` TTL); zero direct DB hit on cache hit | `429 Too Many Requests` |
| `/api/v1/webhooks/github` | `POST` | `30 req / 60 sec` | `1 MB` | Mandatory `X-Hub-Signature-256` HMAC + `X-GitHub-Delivery` lock | `401` / `413` / `429` |
| `/api/v1/agent/chat` | `POST` | `5 req / 600 sec` per IP | `4 KB` (`500 chars`) | Invisible Cloudflare Turnstile token + Global Daily Token Circuit Breaker (`50,000 tokens/day`) | `403` / `422` / `429` |
| `/api/v1/contact` | `POST` | `3 req / 3600 sec` per IP | `16 KB` | Invisible Cloudflare Turnstile token + strict Pydantic email/text sanitization | `403` / `422` / `429` |

### 6.2 Anti-Scraping PII Hydration for Recruiter Contact Info
Recruiters must be able to reach Shreyas immediately via Email (`shreyas.chemakoora@gmail.com`), Phone (`+91 9346759117`), and LinkedIn (`https://www.linkedin.com/in/shreyas-reddy-8a7512285`) without login barriers, while preventing automated DOM scrapers from harvesting phone and email strings:
1. **Static HTML Masking:** Next.js Server Components never emit raw `mailto:` or `tel:` strings in initial SSR HTML. LinkedIn and GitHub URLs render directly for SEO authority.
2. **Client-Side / Turnstile Hydration:** Clicking "Copy Email", "Copy Phone", or "Direct Contact" on the Recruiter Bar verifies an invisible Cloudflare Turnstile token against `GET /api/v1/public/contact-reveal` (or decodes obfuscated byte arrays in client memory upon pointer interaction), copying `+91 9346759117` or `shreyas.chemakoora@gmail.com` to the recruiter's clipboard in one click.

### 6.3 Bounded AI Agent Security ("Ask Shreyas AI" RAG Pipeline)
1. **Scope Restriction:** The recruiter AI assistant answers questions strictly about Shreyas's projects, engineering skills, Viswam.ai Tech Lead experience, hackathons, and certifications using top-4 cosine similarity matches from `portfolio_embeddings` (`pgvector`).
2. **128-Bit Hex Nonce Delimiters (Prompt Injection Defense):**
   - Every request generates a fresh per-turn cryptographic boundary token via `nonce = secrets.token_hex(16)`.
   - Retrieved context and user queries are wrapped inside `<context_{nonce}> ... </context_{nonce}>` and `<user_query_{nonce}> ... </user_query_{nonce}>`.
   - The system prompt explicitly instructs the model to treat everything inside those nonce tags as passive untrusted data and never execute instructions contained within them.
3. **Graceful Degradation:** If the daily LLM token circuit breaker trips or the upstream provider times out (`>10s`), `/api/v1/agent/chat` never crashes with a `500`—it falls back to returning the top-matching structured project/experience cards directly from `pgvector` search.

### 6.4 HTTP Security Headers, SSRF Prevention, & Error Envelopes
- **CORS Policy:** `allow_origins` strictly bound to `settings.ALLOWED_ORIGINS` (`http://localhost:3000` in dev, exact Vercel/custom domain in prod). `allow_origins=["*"]` with credentials is forbidden.
- **Security Headers Middleware:** Every response injects:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: camera=(), microphone=(), geolocation=()`
  - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
- **Outbound SSRF Filter:** Outbound `httpx` calls are restricted to an explicit domain allowlist (`api.github.com`, `raw.githubusercontent.com`, `challenges.cloudflare.com`, `generativelanguage.googleapis.com`, `api.groq.com`) and reject private/loopback IP ranges (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`).
- **Structured Error Envelope:** All exceptions return `{"error_code": "STRING_CODE", "message": "Human-safe summary", "request_id": "uuid4"}` with stack traces suppressed in production (`DEBUG=False`).

---

## 7. Senior Architectural Rationale ("Why") & Verification Commands

### Senior Engineering Trade-Offs
1. **Why Hybrid GitOps + Postgres instead of Pure Static JSON or a Traditional Admin Panel?**
   - A traditional `/admin` dashboard creates a permanent credential-stuffing and session-hijacking target. Pure static JSON requires a full Next.js rebuild every time a GitHub repo star count changes. Combining HMAC-signed GitHub webhooks + Postgres/Redis cache gives real-time dynamic updates with **zero public login attack surface**, and if Redis/Postgres ever restarts on a free tier, Next.js ISR + `/content/portfolio_data.json` keeps the site 100% online.
2. **Why Pre-Compute AI Repo Explainers on Webhook Push Instead of On-Visitor-Click?**
   - Generating AI summaries when a recruiter clicks a repo wastes LLM quota, introduces a 2–4 second loading spinner, and allows bots to drain API credits. Generating the summary **once** inside the authenticated GitHub webhook worker and caching it in PostgreSQL makes visitor reads instantaneous (`<15ms`) and caps AI cost to near zero.

### PowerShell Verification Commands (Run in Antigravity IDE Terminal)
Save this file and run the following commands in `PS C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio>` to verify `docs/ARCHITECTURE.md` is locked in place:

    # 1. Verify docs/ARCHITECTURE.md exists and check file size:
    Get-Item .\docs\ARCHITECTURE.md | Select-Object Name, Length, LastWriteTime

    # 2. Verify both AGENTS.md and docs/ARCHITECTURE.md are tracked in the spec pack:
    Get-ChildItem -Path .\AGENTS.md, .\docs\ARCHITECTURE.md | Format-Table FullName, Length -AutoSize