# SCHEMA.md — PostgreSQL 15 + `pgvector` Database & Alembic Specification (`shreyas-portfolio`)

## 1. Database Engine, Extensions, & Zero-Config Connection Standard

`shreyas-portfolio` uses **PostgreSQL 15** with the **`pgvector`** and **`pgcrypto`** extensions as its primary relational and vector store, paired with **SQLAlchemy 2.0 (Async)** and **Alembic** for deterministic schema migrations.

### 1.1 Local Docker & DBeaver Connection Standard (`localhost:5432/postgres`)
To ensure the global Antigravity `postgres` MCP server and **DBeaver** inspect tables immediately with zero connection edits:
- **Docker Image:** `pgvector/pgvector:pg15`
- **Container Name:** `shreyas_portfolio_postgres`
- **Host / Port:** `localhost:5432`
- **Database / User / Password:** `postgres` / `postgres` / `postgres`
- **Async SQLAlchemy URL (`.env`):** `postgresql+asyncpg://postgres:postgres@localhost:5432/postgres`
- **Sync Alembic / DBeaver URL:** `postgresql+psycopg://postgres:postgres@localhost:5432/postgres`
- **Docker Named Volume:** `shreyas_portfolio_pgdata`
- **Production ($0 Cloud Tier):** Neon Serverless PostgreSQL Free Tier (`?sslmode=require`), managed strictly via the exact same Alembic revision chain.

### 1.2 Mandatory PostgreSQL Extensions
Every initial migration (`0001_initial_schema_and_pgvector.py`) MUST execute:

    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "vector";

---

## 2. Entity-Relationship (ER) Overview & Design Invariants

### 2.1 Core Schema Invariants
1. **Zero-Login GitOps Ownership:** Because `shreyas-portfolio` has zero public login or multi-tenant user registration tables, there is no `users` or `sessions` table to brute-force. All write mutations originate exclusively from:
   - Deterministic Alembic / CLI seed scripts (`/content/portfolio_data.json`), or
   - Cryptographically verified GitHub Webhooks (`X-Hub-Signature-256` HMAC-SHA256).
2. **UUID v4 Primary Keys:** Every domain entity uses `UUID PRIMARY KEY DEFAULT gen_random_uuid()` (except `webhook_deliveries`, which uses GitHub's globally unique `delivery_id` UUID string as its natural primary key).
3. **Timestamps in UTC:** All temporal columns use `TIMESTAMPTZ NOT NULL DEFAULT NOW()` with an automated trigger or SQLAlchemy `onupdate=func.now()` for `updated_at`.
4. **Hybrid Relational + Validated JSONB:** Relational columns enforce strict uniqueness, sorting, and foreign-key integrity, while structured `JSONB` columns (`tech_stack`, `ai_explainer`, `model_3d_config`, `metrics`) eliminate N+1 join overhead during high-speed portfolio reads.

### 2.2 Table Inventory (8 Tables)
1. **`candidate_profile`** — Singleton table (`singleton_key = 'SHREYAS_REDDY'`) holding headline, bio, education, social links, obfuscated contact payloads, and 3D Neural Hub node telemetry.
2. **`projects`** — Stores both curated Flagship Systems (SecureRAG, DataMind, Project Sentinel, Denoising Workbench, `telarc`, Folkbattle) and live auto-synced public GitHub repositories with pre-computed AI Repo Explainers and 3D scene configs.
3. **`experiences`** — Stores career leadership and academic milestones (Viswam.ai Tech Lead for 200+ interns, Team CODEX Core Lead, ICFAI Tech B.Tech CSE AI) with 3D Z-axis spline coordinates.
4. **`hackathons`** — Stores Hackathon Arena case studies (Smart India Hackathon 2025, SOAI Hackathon 2025, Cybersecurity Hackathon 2025) with problem statements, architecture summaries, and proof links.
5. **`certificates`** — Stores verified credentials (Azure AI-901, Google Cloud Gen AI Academy, NVIDIA DLI, Kaggle AI Agents Intensive, NASSCOM FutureSkills Prime, IBM SkillsBuild) with category filters and 3D plaque metadata.
6. **`portfolio_embeddings`** — Stores 768-dimensional `pgvector` embeddings across all projects, experiences, hackathons, and certificates to power the bounded "Ask Shreyas AI" recruiter assistant.
7. **`webhook_deliveries`** — Immutable idempotency and audit ledger for `POST /api/v1/webhooks/github` (`X-GitHub-Delivery`), preventing webhook replay attacks.
8. **`contact_submissions`** — Rate-limited, Cloudflare Turnstile-verified recruiter messages with SHA-256 hashed IP tracking for abuse auditing without storing raw visitor IPs.

### 2.3 ASCII Entity-Relationship Diagram

    +------------------------+       +----------------------------------+
    |   candidate_profile    |       |       webhook_deliveries         |
    |------------------------|       |----------------------------------|
    | PK id (UUID)           |       | PK delivery_id (VARCHAR 64)      |
    | UQ singleton_key       |       |    event_type (VARCHAR 50)       |
    |    full_name           |       |    repo_full_name (VARCHAR 255)  |
    |    headline            |       |    signature_valid (BOOLEAN)     |
    |    hero_3d_config JSONB|       |    status (VARCHAR 32)           |
    +------------------------+       +----------------------------------+

    +------------------------+       +----------------------------------+
    |        projects        |       |      portfolio_embeddings        |
    |------------------------|       |----------------------------------|
    | PK id (UUID)           |       | PK id (UUID)                     |
    | UQ slug (VARCHAR 120)  |       |    source_type (VARCHAR 32)      |
    | UQ github_repo_id BIGINT|<--.  |    source_id (UUID)              |
    |    title, tagline      |    |  |    source_slug (VARCHAR 120)     |
    |    ai_explainer JSONB  |    +--|    chunk_index (INT)             |
    |    tech_stack JSONB    |       |    chunk_text (TEXT)             |
    |    model_3d_config JSON|       |    content_hash (CHAR 64)        |
    |    is_flagship BOOL    |       |    embedding VECTOR(768) [HNSW]  |
    +------------------------+       +----------------------------------+
                ^                              ^               ^
                | (Polymorphic RAG indexing via source_type + source_id)
    +------------------------+       +-----------------+  +-------------+
    |      experiences       |       |   hackathons    |  | certificates|
    |------------------------|       |-----------------|  |-------------|
    | PK id (UUID)           |       | PK id (UUID)    |  | PK id (UUID)|
    | UQ slug (VARCHAR 120)  |       | UQ slug         |  | UQ slug     |
    |    role, organization  |       |    event_name   |  |    title    |
    |    metrics JSONB       |       |    project_title|  |    issuer   |
    |    spline_config JSONB |       |    award_status |  |    category |
    +------------------------+       +-----------------+  +-------------+

---

## 3. Complete PostgreSQL DDL Specification

### 3.1 Table 1: `candidate_profile` (Singleton)
Enforces a single ground-truth row using a `CHECK (singleton_key = 'SHREYAS_REDDY')` constraint.

    CREATE TABLE candidate_profile (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        singleton_key VARCHAR(32) NOT NULL UNIQUE DEFAULT 'SHREYAS_REDDY'
            CHECK (singleton_key = 'SHREYAS_REDDY'),
        full_name VARCHAR(120) NOT NULL DEFAULT 'Chemakoora Shreyas Reddy',
        display_name VARCHAR(80) NOT NULL DEFAULT 'Shreyas Reddy',
        headline VARCHAR(255) NOT NULL,
        subheadline TEXT NOT NULL,
        location VARCHAR(120) NOT NULL DEFAULT 'Hyderabad, Telangana, India',
        education_degree VARCHAR(180) NOT NULL DEFAULT 'B.Tech in Computer Science & Engineering (Artificial Intelligence)',
        education_institution VARCHAR(180) NOT NULL DEFAULT 'ICFAI Foundation for Higher Education (ICFAI Tech)',
        graduation_year INTEGER NOT NULL DEFAULT 2027,
        github_username VARCHAR(80) NOT NULL,
        github_url VARCHAR(255) NOT NULL,
        linkedin_url VARCHAR(255) NOT NULL DEFAULT 'https://www.linkedin.com/in/shreyas-reddy-8a7512285',
        email_masked VARCHAR(120) NOT NULL DEFAULT 'shreyas.chemakoora [at] gmail.com',
        phone_masked VARCHAR(64) NOT NULL DEFAULT '+91 93467-XXXXX',
        email_cleartext VARCHAR(160) NOT NULL DEFAULT 'shreyas.chemakoora@gmail.com',
        phone_cleartext VARCHAR(32) NOT NULL DEFAULT '+91 9346759117',
        resume_pdf_url VARCHAR(255) NOT NULL DEFAULT '/resume/Shreyas_Reddy_Resume.pdf',
        availability_badge VARCHAR(120) NOT NULL DEFAULT 'Open to AI Engineering & Full-Stack Internships / Grad Roles',
        hero_pillars JSONB NOT NULL DEFAULT '[]'::jsonb,
        hero_3d_config JSONB NOT NULL DEFAULT '{}'::jsonb,
        last_github_sync_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

### 3.2 Table 2: `projects` (Flagship Systems + Auto-Synced GitHub Vault)
Stores both curated deep-dive flagship projects (`is_flagship = TRUE`) and public repositories synced dynamically from GitHub webhooks (`is_auto_synced = TRUE`).

    CREATE TABLE projects (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        slug VARCHAR(120) NOT NULL UNIQUE,
        github_repo_id BIGINT UNIQUE,
        title VARCHAR(160) NOT NULL,
        tagline VARCHAR(280) NOT NULL,
        category VARCHAR(64) NOT NULL DEFAULT 'Full-Stack & Open Source'
            CHECK (category IN ('Agentic AI & RAG', 'Cybersecurity & Zero-Trust', 'Computer Vision & ML', 'Full-Stack & Open Source')),
        summary TEXT NOT NULL,
        architecture_md TEXT NOT NULL,
        ai_explainer JSONB NOT NULL DEFAULT '{}'::jsonb,
        tech_stack JSONB NOT NULL DEFAULT '[]'::jsonb,
        security_highlights JSONB NOT NULL DEFAULT '[]'::jsonb,
        metrics JSONB NOT NULL DEFAULT '[]'::jsonb,
        github_url VARCHAR(255),
        live_url VARCHAR(255),
        primary_language VARCHAR(64),
        stars_count INTEGER NOT NULL DEFAULT 0 CHECK (stars_count >= 0),
        forks_count INTEGER NOT NULL DEFAULT 0 CHECK (forks_count >= 0),
        open_issues_count INTEGER NOT NULL DEFAULT 0 CHECK (open_issues_count >= 0),
        readme_sha VARCHAR(64),
        latest_commit_sha VARCHAR(64),
        is_flagship BOOLEAN NOT NULL DEFAULT FALSE,
        is_featured BOOLEAN NOT NULL DEFAULT TRUE,
        is_auto_synced BOOLEAN NOT NULL DEFAULT FALSE,
        is_archived BOOLEAN NOT NULL DEFAULT FALSE,
        display_order INTEGER NOT NULL DEFAULT 100,
        model_3d_config JSONB NOT NULL DEFAULT '{}'::jsonb,
        last_pushed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

### 3.3 Table 3: `experiences` (3D Z-Axis Career & Leadership Timeline)

    CREATE TABLE experiences (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        slug VARCHAR(120) NOT NULL UNIQUE,
        role VARCHAR(160) NOT NULL,
        organization VARCHAR(160) NOT NULL,
        organization_url VARCHAR(255),
        location VARCHAR(120) NOT NULL DEFAULT 'Hyderabad, India',
        employment_type VARCHAR(64) NOT NULL
            CHECK (employment_type IN ('Leadership Internship', 'Technical Team Lead', 'Education', 'Full-Time', 'Open Source')),
        start_date DATE NOT NULL,
        end_date DATE,
        is_current BOOLEAN NOT NULL DEFAULT FALSE,
        summary TEXT NOT NULL,
        highlights JSONB NOT NULL DEFAULT '[]'::jsonb,
        metrics JSONB NOT NULL DEFAULT '[]'::jsonb,
        tech_stack JSONB NOT NULL DEFAULT '[]'::jsonb,
        spline_node_config JSONB NOT NULL DEFAULT '{}'::jsonb,
        display_order INTEGER NOT NULL DEFAULT 10,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

### 3.4 Table 4: `hackathons` (3D Hackathon Arena & Proof-of-Work)

    CREATE TABLE hackathons (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        slug VARCHAR(120) NOT NULL UNIQUE,
        event_name VARCHAR(180) NOT NULL,
        organizer VARCHAR(160) NOT NULL,
        project_title VARCHAR(160) NOT NULL,
        project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
        award_status VARCHAR(120) NOT NULL,
        team_name VARCHAR(80) NOT NULL DEFAULT 'Team CODEX',
        role VARCHAR(120) NOT NULL,
        team_members JSONB NOT NULL DEFAULT '[]'::jsonb,
        event_date DATE NOT NULL,
        problem_statement TEXT NOT NULL,
        architecture_summary TEXT NOT NULL,
        tech_stack JSONB NOT NULL DEFAULT '[]'::jsonb,
        outcomes JSONB NOT NULL DEFAULT '[]'::jsonb,
        github_url VARCHAR(255),
        live_url VARCHAR(255),
        proof_url VARCHAR(255),
        model_3d_config JSONB NOT NULL DEFAULT '{}'::jsonb,
        display_order INTEGER NOT NULL DEFAULT 10,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

### 3.5 Table 5: `certificates` (3D Verified Credentials Vault)

    CREATE TABLE certificates (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        slug VARCHAR(120) NOT NULL UNIQUE,
        title VARCHAR(200) NOT NULL,
        issuer VARCHAR(140) NOT NULL,
        category VARCHAR(64) NOT NULL
            CHECK (category IN ('AI & Agents', 'Cloud Architecture', 'Cybersecurity', 'Data Science & Big Data')),
        issue_date DATE NOT NULL,
        credential_id VARCHAR(128),
        verify_url VARCHAR(255),
        certificate_asset_url VARCHAR(255),
        skills_covered JSONB NOT NULL DEFAULT '[]'::jsonb,
        summary TEXT NOT NULL,
        badge_3d_config JSONB NOT NULL DEFAULT '{}'::jsonb,
        is_featured BOOLEAN NOT NULL DEFAULT TRUE,
        display_order INTEGER NOT NULL DEFAULT 10,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

### 3.6 Table 6: `portfolio_embeddings` (`pgvector` Store for "Ask Shreyas AI")
Uses 768-dimensional vectors (compatible with both Google `text-embedding-004` on the $0 Gemini tier and local Ollama `nomic-embed-text`).

    CREATE TABLE portfolio_embeddings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        source_type VARCHAR(32) NOT NULL
            CHECK (source_type IN ('profile', 'project', 'experience', 'hackathon', 'certificate')),
        source_id UUID NOT NULL,
        source_slug VARCHAR(120) NOT NULL,
        title VARCHAR(200) NOT NULL,
        chunk_index INTEGER NOT NULL DEFAULT 0 CHECK (chunk_index >= 0),
        chunk_text TEXT NOT NULL,
        metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
        content_hash CHAR(64) NOT NULL,
        embedding vector(768) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CONSTRAINT uq_portfolio_embeddings_source_chunk UNIQUE (source_type, source_id, chunk_index)
    );

### 3.7 Table 7: `webhook_deliveries` (HMAC Idempotency & Replay Defense)

    CREATE TABLE webhook_deliveries (
        delivery_id VARCHAR(64) PRIMARY KEY,
        event_type VARCHAR(64) NOT NULL,
        repository_full_name VARCHAR(200),
        signature_verified BOOLEAN NOT NULL DEFAULT FALSE,
        payload_sha256 CHAR(64) NOT NULL,
        status VARCHAR(32) NOT NULL
            CHECK (status IN ('processed', 'ignored', 'failed', 'rejected_hmac')),
        error_detail VARCHAR(500),
        processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

### 3.8 Table 8: `contact_submissions` (Turnstile-Gated Recruiter Inquiries)

    CREATE TABLE contact_submissions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        sender_name VARCHAR(120) NOT NULL,
        sender_email VARCHAR(160) NOT NULL,
        sender_company VARCHAR(140),
        role_opportunity VARCHAR(160),
        message TEXT NOT NULL CHECK (char_length(message) <= 2000),
        ip_sha256 CHAR(64) NOT NULL,
        turnstile_verified BOOLEAN NOT NULL DEFAULT TRUE,
        status VARCHAR(32) NOT NULL DEFAULT 'received'
            CHECK (status IN ('received', 'notified', 'archived')),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

---

## 4. Indexing Strategy (B-Tree, Partial, & HNSW Vector Indexes)

Every lookup, sorting, foreign-key, and similarity search path is backed by an explicit index in migration `0001_initial_schema_and_pgvector.py` so public portfolio queries execute in `<3ms`:

    -- 1. Projects Indexes (Fast sorting for Flagship vs Auto-Synced GitHub Vault)
    CREATE INDEX ix_projects_featured_order
        ON projects (is_flagship DESC, is_featured DESC, display_order ASC, last_pushed_at DESC)
        WHERE is_archived = FALSE;

    CREATE INDEX ix_projects_category
        ON projects (category, display_order ASC);

    CREATE INDEX ix_projects_last_pushed_at
        ON projects (last_pushed_at DESC);

    -- 2. Experiences & Hackathons Timeline Indexes
    CREATE INDEX ix_experiences_timeline
        ON experiences (display_order ASC, start_date DESC);

    CREATE INDEX ix_hackathons_project_id
        ON hackathons (project_id);

    CREATE INDEX ix_hackathons_order_date
        ON hackathons (display_order ASC, event_date DESC);

    -- 3. Certificates Vault Category & Order Indexes
    CREATE INDEX ix_certificates_category_order
        ON certificates (category, display_order ASC, issue_date DESC);

    -- 4. Portfolio Embeddings HNSW Cosine Index & Source Lookup
    CREATE INDEX ix_portfolio_embeddings_source
        ON portfolio_embeddings (source_type, source_id);

    CREATE INDEX ix_portfolio_embeddings_content_hash
        ON portfolio_embeddings (content_hash);

    CREATE INDEX ix_portfolio_embeddings_hnsw_cosine
        ON portfolio_embeddings
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);

    -- 5. Webhook & Contact Security Audit Indexes
    CREATE INDEX ix_webhook_deliveries_processed_at
        ON webhook_deliveries (processed_at DESC);

    CREATE INDEX ix_contact_submissions_ip_created
        ON contact_submissions (ip_sha256, created_at DESC);

---

## 5. Strict JSONB Column Contracts (Pydantic-Validated Before Write)

Never insert unvalidated dictionaries into `JSONB` columns. FastAPI services MUST validate every `JSONB` payload through strict Pydantic v2 models before persistence:

### 5.1 `projects.ai_explainer` Contract
Generated once per repository update by `repo_explainer.py` and cached in PostgreSQL:

    {
      "problem_statement": "Traditional RAG pipelines remain vulnerable to indirect prompt injection, cross-tenant retrieval leakage, and unverified LLM hallucinations.",
      "architecture_stack": [
        "Qdrant Hybrid Vector + Sparse BM25 Retrieval",
        "128-Bit Cryptographic Hex Nonce Prompt Delimiters",
        "5-Layer Multi-Agent Input/Output Security Auditor",
        "FastAPI Async Orchestrator + Pydantic v2 Contracts"
      ],
      "engineering_highlights": [
        "Blocks indirect prompt injection payloads embedded inside retrieved documents using randomized per-turn hex nonces.",
        "Combines dense semantic embeddings with sparse lexical matching for high-precision technical retrieval.",
        "Enforces deterministic output auditing before returning synthesized responses."
      ],
      "generated_by": "gemini-2.5-flash",
      "readme_sha_synced": "a1b2c3d4e5f6"
    }

### 5.2 `projects.model_3d_config` & `certificates.badge_3d_config` Contract
Controls how the shared React Three Fiber `<PersistentCanvas />` renders each entity's 3D geometry inside its `<View>` portal:

    {
      "archetype": "zero_trust_shield",
      "primary_hex": "#06B6D4",
      "secondary_hex": "#10B981",
      "wireframe": true,
      "layers_count": 5,
      "rotation_speed": 0.35,
      "camera_position": [0.0, 0.4, 4.2]
    }

Allowed `archetype` enum values:
- `zero_trust_shield` (SecureRAG)
- `neural_data_core` (DataMind)
- `ueba_radar_grid` (Project Sentinel)
- `topography_surface` (Denoising Prior to Edge Detection)
- `cultural_archive_cube` (Telugu Digital Archive `telarc`)
- `story_node_constellation` (Folkbattle)
- `github_repo_module` (Default for auto-synced GitHub repositories)

---

## 6. Alembic Migration Sequence & Concurrency Locking Rules

### 6.1 Required Migration Files (`backend/alembic/versions/`)
1. **`0001_initial_schema_and_pgvector.py`**
   - Enables `pgcrypto` and `vector` extensions.
   - Creates all 8 tables (`candidate_profile`, `projects`, `experiences`, `hackathons`, `certificates`, `portfolio_embeddings`, `webhook_deliveries`, `contact_submissions`).
   - Creates all B-tree, partial, and HNSW indexes.
2. **`0002_seed_shreyas_ground_truth.py`**
   - Idempotently loads `/content/portfolio_data.json` into PostgreSQL using `INSERT ... ON CONFLICT (slug) DO UPDATE` so running migrations or re-seeding never creates duplicate rows.

### 6.2 Atomic Upsert & Row-Locking Rules
1. **Webhook Repo Sync Upsert:** When GitHub fires `push` or `repository` webhooks concurrently, `github_sync.py` MUST use PostgreSQL's atomic upsert on `github_repo_id` (or `slug` for flagship repos):

    INSERT INTO projects (slug, github_repo_id, title, tagline, summary, architecture_md, ai_explainer, tech_stack, github_url, primary_language, stars_count, forks_count, readme_sha, latest_commit_sha, is_auto_synced, last_pushed_at, updated_at)
    VALUES (:slug, :github_repo_id, :title, :tagline, :summary, :architecture_md, :ai_explainer, :tech_stack, :github_url, :primary_language, :stars_count, :forks_count, :readme_sha, :latest_commit_sha, TRUE, :last_pushed_at, NOW())
    ON CONFLICT (slug) DO UPDATE SET
        stars_count = EXCLUDED.stars_count,
        forks_count = EXCLUDED.forks_count,
        primary_language = EXCLUDED.primary_language,
        ai_explainer = CASE
            WHEN projects.readme_sha IS DISTINCT FROM EXCLUDED.readme_sha THEN EXCLUDED.ai_explainer
            ELSE projects.ai_explainer
        END,
        readme_sha = EXCLUDED.readme_sha,
        latest_commit_sha = EXCLUDED.latest_commit_sha,
        last_pushed_at = EXCLUDED.last_pushed_at,
        updated_at = NOW();

2. **Cost-Zero Embedding Deduplication:** Before calling Gemini or Ollama to compute a 768-dim vector for `portfolio_embeddings`, compute `sha256(chunk_text)`. If `content_hash` in `portfolio_embeddings` matches the new hash, **skip** the embedding API call completely.

---

## 7. Ground-Truth Seed Specification (`/content/portfolio_data.json`)

Migration `0002_seed_shreyas_ground_truth.py` MUST populate these exact verified records so the portfolio boots with 100% real data:

### 7.1 Flagship Projects (`projects` where `is_flagship = TRUE`)
1. **`securerag`** — **SecureRAG: 5-Layer Zero-Trust Multi-Agent RAG Pipeline**
   - *Category:* `Cybersecurity & Zero-Trust` | *3D Archetype:* `zero_trust_shield`
   - *Tech Stack:* `["Python", "FastAPI", "Qdrant", "Hybrid Vector + Sparse Retrieval", "128-Bit Hex Nonce Delimiters", "Multi-Agent Auditing"]`
   - *Highlights:* 5 concentric security layers defending RAG systems against indirect prompt injection, retrieval poisoning, and sensitive output leakage.
2. **`datamind`** — **DataMind: Autonomous AI Data Intelligence Platform**
   - *Category:* `Agentic AI & RAG` | *3D Archetype:* `neural_data_core`
   - *Tech Stack:* `["Next.js 15", "FastAPI", "PostgreSQL", "pgvector", "Tailwind CSS", "Ollama", "Pytest", "Playwright"]`
   - *Highlights:* End-to-end conversational data intelligence workbench combining local Ollama SLMs with `pgvector` semantic indexing and automated E2E Playwright verification.
3. **`constructpulse`** — **ConstructPulse: Autonomous Construction Intelligence & CRM Sync Engine**
   - *Category:* `Enterprise AI & Automation` | *3D Archetype:* `construction_wireframe_isometric`
   - *Tech Stack:* `["FastAPI", "PostgreSQL", "RAVE Build API", "HubSpot", "Pytest", "Docker"]`
   - *Highlights:* Real-time construction project intelligence platform synchronizing CRM deal pipelines, spec sheets, and subcontractor scheduling.
4. **`crisispulse`** — **CrisisPulse: Geospatial Multi-Modal Disaster Intelligence Platform**
   - *Category:* `Geospatial AI & Crisis Ops` | *3D Archetype:* `geospatial_disaster_globe`
   - *Tech Stack:* `["FastAPI", "GeoJSON", "Mapbox GL", "Ollama", "Redis", "WebSockets"]`
   - *Highlights:* Real-time multi-modal crisis intelligence aggregating emergency feeds, satellite overlays, and automated resource dispatch recommendations.
5. **`telarc`** — **Telugu Digital Archive Portal (`telarc`)**
   - *Category:* `Full-Stack & Open Source` | *3D Archetype:* `cultural_archive_cube`
   - *Tech Stack:* `["Python", "Streamlit", "Hugging Face Spaces", "Multimedia Archiving", "MIT License"]`
   - *Highlights:* Open-source regional digital preservation platform archiving Telugu audio, video, image, and text datasets with accessible metadata indexing.

### 7.2 Google Colab & Research Repositories (`projects` where `is_flagship = FALSE`)
1. **`computer-vision`** — **Computer Vision & Denoising Topography Lab**
2. **`machine-learning`** — **Machine Learning Algorithms & ROC Diagnostics Lab**
3. **`data-wrangling-visualization`** — **Data Wrangling & Statistical EDA Workbench**

### 7.3 Career & Academic Timeline (`experiences`)
1. **`limelite-fde-nz`** — **Forward Deployed Engineer | Limelite Constructions (New Zealand)** (`2026-06-01` to Present)
2. **`viswam-ai-tech-lead`** — **Tech Lead (AI & Software Development Intern) | Viswam.ai** (`2025-06-01` to `2025-08-31`)
3. **`icfai-tech-btech`** — **B.Tech Computer Science & Engineering (AI) | ICFAI Tech School** (`2023-08-01` to `2027-05-31`)
   - *Highlights:* Directed technical strategy, architecture standardization, code reviews, and AI development workflows across a cohort of 200+ engineering interns.
2. **`team-codex-lead`** — **Core Technical Lead | Team CODEX** (`2025-07-01` to `Present`)
   - *Highlights:* Spearheaded system architecture, backend integration, and AI security engineering across national hackathons alongside UX, AI/Prompt, Data Science, and Deployment specialists.
3. **`icfai-tech-btech`** — **B.Tech in Computer Science & Engineering (AI) | ICFAI Tech** (`2023-08-01` to `2027-05-31`)
   - *Highlights:* Specializing in Artificial Intelligence, Autonomous Agents, Deep Learning, Computer Vision, and Production Software Engineering in Hyderabad, India.

### 7.3 Hackathon Arena (`hackathons`)
1. **`sih-2025`** — **Smart India Hackathon (SIH) 2025** | *Role:* Technical Lead (AI & Full-Stack Architecture)
2. **`cybersecurity-hackathon-2025`** — **Cybersecurity Hackathon 2025 (`Project Sentinel`)** | *Role:* Lead Security & UEBA Architect
3. **`soai-hackathon-2025`** — **SOAI Hackathon 2025 (`Folkbattle` on Code Swecha)** | *Role:* Lead Application Developer

### 7.4 Verified Credentials Vault (`certificates`)
1. **`azure-ai-901`** — **Microsoft Certified: Azure AI Fundamentals (AI-901)** | *Issuer:* Microsoft | *Category:* `Cloud Architecture`
2. **`gcp-gen-ai-academy`** — **Google Cloud Gen AI Academy (APAC Edition)** | *Issuer:* Google Cloud | *Category:* `AI & Agents`
3. **`nvidia-dli-robotics-prompt`** — **NVIDIA DLI: Autonomous Robotics & Prompt Engineering** | *Issuer:* NVIDIA Deep Learning Institute | *Category:* `AI & Agents`
4. **`kaggle-ai-agents-intensive`** — **AI Agents Intensive Course & Capstone** | *Issuer:* Kaggle & Google | *Category:* `AI & Agents`
5. **`nasscom-futureskills-data`** — **Data Processing and Visualisation Credential** | *Issuer:* FutureSkills Prime (NASSCOM) | *Category:* `Data Science & Big Data`
6. **`ibm-cybersecurity-fundamentals`** — **Cybersecurity Fundamentals & Infosys Big Data / Hadoop 3** | *Issuer:* IBM SkillsBuild & Infosys Springboard | *Category:* `Cybersecurity`

---

## 8. Senior Database Engineering "Why" & Verification Commands

### Senior Engineering Trade-Offs
1. **Why an HNSW Index (`vector_cosine_ops`) Instead of IVFFlat on `portfolio_embeddings`?**
   - `IVFFlat` requires pre-training cluster centroids on a large dataset and degrades badly when rows are inserted dynamically via GitHub webhooks. **HNSW (Hierarchical Navigable Small World)** requires zero training step, maintains high recall on small-to-medium tables, and dynamically indexes new repo embeddings on the fly in `<2ms`.
2. **Why Hybrid Relational Columns + Validated `JSONB` Instead of 15 Join Tables?**
   - Normalizing `tech_stack`, `metrics`, and `highlights` into separate many-to-many join tables forces a 6-table `JOIN` on every portfolio page load. Storing filterable attributes (`slug`, `category`, `is_flagship`, `display_order`) as indexed relational columns and nested display arrays as Pydantic-validated `JSONB` allows FastAPI to fetch the entire portfolio payload in a single sequential read without N+1 queries.

### PowerShell & DBeaver Verification Commands
Run these commands in your Antigravity IDE PowerShell terminal (`PS C:\Users\shrey\Documents\Shreyas\Projects\shreyas-portfolio>`) to verify `docs/SCHEMA.md` is saved and ready for Phase 1 migration generation:

    # 1. Verify docs/SCHEMA.md is saved and non-empty:
    Get-Item .\docs\SCHEMA.md | Select-Object Name, Length, LastWriteTime

    # 2. Once Docker Postgres is up in Phase 1, verify pgvector & all 8 tables via psql:
    # docker exec -it shreyas_portfolio_postgres psql -U postgres -d postgres -c "\dx"
    # docker exec -it shreyas_portfolio_postgres psql -U postgres -d postgres -c "\dt"