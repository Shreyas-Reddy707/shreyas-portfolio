import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
MANIFEST_PATH = BASE_DIR / "content" / "portfolio_data.json"

def upgrade_manifest():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # 1. Update Flagship Projects
    project_upgrades = {
        "securerag": {
            "github_url": "https://github.com/Shreyas-Reddy707/Secure_RAG",
            "tagline": "5-LAYER ZERO-TRUST MULTI-AGENT DEFENSE FOR ENTERPRISE RAG",
            "summary": "Mathematically grounded 5-Layer Zero-Trust Multi-Agent Defense Pipeline halting Indirect Prompt Injection, PoisonedRAG, and Namespace Traversal.",
            "metrics": [
                {"label": "ATTACK SUCCESS", "value": "0.0%"},
                {"label": "INJECTION INTERCEPTION", "value": "100%"},
                {"label": "FACTUAL FAITHFULNESS", "value": "99.8%"},
            ],
            "model_3d_config": {
                "archetype": "zero_trust_shield",
                "primary_hex": "#00F0FF",
                "secondary_hex": "#10B981",
                "wireframe": True,
                "layers_count": 5,
                "rotation_speed": 0.35,
                "camera_position": [0.0, 0.4, 4.2],
                "eyebrow": "SECURERAG",
                "subtitle": "5-LAYER ZERO-TRUST MULTI-AGENT DEFENSE FOR ENTERPRISE RAG",
                "core_concept": "Mathematically grounded 5-Layer Zero-Trust Multi-Agent Defense Pipeline halting Indirect Prompt Injection, PoisonedRAG, and Namespace Traversal.",
                "metric_pills": [
                    "0.0% ATTACK SUCCESS RATE",
                    "100% INJECTION INTERCEPTION",
                    "99.8% FACTUAL FAITHFULNESS",
                ],
                "pipeline_layers": [
                    {
                        "id": "L1",
                        "name": "Pre-Retrieval Input Firewall",
                        "badge": "~5ms",
                        "accent": "cyan",
                        "detail": "Regex + semantic intent classifier blocking jailbreaks, token smuggling, and cross-namespace query probing before vector search.",
                    },
                    {
                        "id": "L2",
                        "name": "Hybrid Retriever — BGE-Small + BM25 + RBAC Gate",
                        "badge": "~6ms",
                        "accent": "violet",
                        "detail": "Qdrant dense (BAAI/bge-small-en-v1.5) + sparse BM25 retrieval strictly filtered by cryptographic role-based access control metadata.",
                    },
                    {
                        "id": "L3",
                        "name": "Context Sanitizer & Cross-Chunk Consensus",
                        "badge": "~76ms",
                        "accent": "emerald",
                        "detail": "Strips adversarial instruction patterns from retrieved chunks and scores cross-chunk semantic agreement to quarantine PoisonedRAG chunks.",
                    },
                    {
                        "id": "L4",
                        "name": "Cryptographic Nonce-Spotlighted Synthesizer",
                        "badge": "~38ms",
                        "accent": "cyan",
                        "detail": "Wraps untrusted context in per-turn 128-bit hex nonce delimiters (<context_nonce>) so embedded instructions cannot escape data boundaries.",
                    },
                    {
                        "id": "L5",
                        "name": "Post-Generation Output & Citation Auditor",
                        "badge": "pipeline",
                        "accent": "violet",
                        "detail": "Verifies every generated sentence against source chunk embeddings and halts response emission on hallucination or policy violation.",
                    },
                ],
            },
        },
        "datamind": {
            "github_url": "https://github.com/Shreyas-Reddy707/Datamind",
            "tagline": "LOCAL-FIRST NO-CODE AI DATA ANALYTICS & AUTOML WORKSPACE",
            "summary": "End-to-end conversational analytics and AutoML engine transforming raw CSV, Excel, JSON, and Parquet datasets into leakage-free predictive models and 2D/3D Plotly telemetry.",
            "metrics": [
                {"label": "AUTOML", "value": "Leakage-Free"},
                {"label": "ENGINE", "value": "DuckDB + pgvector"},
                {"label": "SECURITY", "value": "Argon2id + JWT"},
            ],
            "model_3d_config": {
                "archetype": "neural_data_core",
                "primary_hex": "#10B981",
                "secondary_hex": "#00F0FF",
                "wireframe": True,
                "layers_count": 5,
                "rotation_speed": 0.4,
                "camera_position": [0.0, 0.2, 4.0],
                "eyebrow": "DATAMIND V2",
                "subtitle": "LOCAL-FIRST NO-CODE AI DATA ANALYTICS & AUTOML WORKSPACE",
                "core_concept": "End-to-end conversational analytics and AutoML engine transforming raw CSV, Excel, JSON, and Parquet datasets into leakage-free predictive models and 2D/3D Plotly telemetry.",
                "metric_pills": [
                    "ZERO DATA LEAKAGE AUTOML",
                    "DUCKDB + PGVECTOR HYBRID",
                    "ARGON2ID + JWT SECURITY",
                ],
                "pipeline_layers": [
                    {
                        "id": "L1",
                        "name": "Multi-Format Ingestion & Upload Security Guard",
                        "badge": "~12ms",
                        "accent": "cyan",
                        "detail": "Validates magic bytes and schema integrity across CSV, Excel, JSON, and Parquet files before loading into zero-copy DuckDB tables.",
                    },
                    {
                        "id": "L2",
                        "name": "Automated Data-Quality & Statistical Profiler",
                        "badge": "~28ms",
                        "accent": "violet",
                        "detail": "Computes missingness, outlier distributions, multicollinearity matrices, and automated data-health scores using Pandas, SciPy, and Statsmodels.",
                    },
                    {
                        "id": "L3",
                        "name": "Natural-Language Pivot & 2D/3D Plotly Engine",
                        "badge": "~45ms",
                        "accent": "emerald",
                        "detail": "Translates plain-English analytical queries into parameterized DuckDB SQL and interactive 2D/3D Plotly surface and scatter visualizations.",
                    },
                    {
                        "id": "L4",
                        "name": "Leakage-Guarded Scikit-Learn AutoML & What-If Simulator",
                        "badge": "~180ms",
                        "accent": "cyan",
                        "detail": "Trains and benchmarks classification/regression models with strict train-test isolation, target-leakage detection, and real-time feature perturbation sliders.",
                    },
                    {
                        "id": "L5",
                        "name": "Local Ollama Copilot with Offline DuckDB Fallback",
                        "badge": "local-first",
                        "accent": "violet",
                        "detail": "Synthesizes executive insights via local Ollama LLMs and pgvector semantic memory while guaranteeing 100% offline query execution.",
                    },
                ],
            },
        },
        "constructpulse": {
            "github_url": "https://github.com/Shreyas-Reddy707/Construct_Pulse",
            "tagline": "REAL-TIME CONSTRUCTION WORKFORCE & SITE SAFETY PLATFORM",
            "summary": "Full-stack Flutter and FastAPI operational command system uniting QR-based site telemetry, Firebase OTP verification, role-based access, and live emergency mustering.",
            "metrics": [
                {"label": "SITE OCCUPANCY", "value": "Real-Time"},
                {"label": "VERIFICATION", "value": "QR + Firebase OTP"},
                {"label": "SAFETY", "value": "Live Mustering"},
            ],
            "model_3d_config": {
                "archetype": "topography_surface",
                "primary_hex": "#F59E0B",
                "secondary_hex": "#00F0FF",
                "wireframe": True,
                "layers_count": 5,
                "rotation_speed": 0.3,
                "camera_position": [0.0, 0.3, 4.5],
                "eyebrow": "CONSTRUCTPULSE",
                "subtitle": "REAL-TIME CONSTRUCTION WORKFORCE & SITE SAFETY PLATFORM",
                "core_concept": "Full-stack Flutter and FastAPI operational command system uniting QR-based site telemetry, Firebase OTP verification, role-based access, and live emergency mustering.",
                "metric_pills": [
                    "REAL-TIME SITE OCCUPANCY",
                    "QR + FIREBASE OTP AUTH",
                    "LIVE EMERGENCY MUSTERING",
                ],
                "pipeline_layers": [
                    {
                        "id": "L1",
                        "name": "Firebase OTP & Admin-Approved Worker Onboarding",
                        "badge": "auth",
                        "accent": "cyan",
                        "detail": "Verifies worker identity via mobile OTP and holds new profiles in a pending queue until approved by site supervisors.",
                    },
                    {
                        "id": "L2",
                        "name": "Cryptographic QR Check-In / Check-Out Scanner",
                        "badge": "~15ms",
                        "accent": "violet",
                        "detail": "Flutter mobile scanner validates rotating site QR checkpoints to log exact entry/exit timestamps and zone assignments.",
                    },
                    {
                        "id": "L3",
                        "name": "FastAPI + SQLAlchemy Async RBAC Engine",
                        "badge": "~8ms",
                        "accent": "emerald",
                        "detail": "Enforces strict role hierarchy (Admin, Site Manager, Worker) backed by JWT rotation and Alembic-migrated PostgreSQL tables.",
                    },
                    {
                        "id": "L4",
                        "name": "Live Site-Occupancy & Trade Analytics Dashboard",
                        "badge": "real-time",
                        "accent": "cyan",
                        "detail": "Streams active headcount by trade, shift duration, and zone capacity to management dashboards.",
                    },
                    {
                        "id": "L5",
                        "name": "Emergency Mustering & Roll-Call Protocol",
                        "badge": "safety-critical",
                        "accent": "violet",
                        "detail": "Triggers instant site-wide muster alerts and tracks accounted vs. unaccounted personnel in real time during site emergencies.",
                    },
                ],
            },
        },
        "crisispulse": {
            "github_url": "https://github.com/Shreyas-Reddy707/team-31",
            "tagline": "REAL-TIME CRISIS INTELLIGENCE & GEOSPATIAL MAPPING ENGINE",
            "summary": "Built during the WikiVerse Hackathon at IIIT Hyderabad to ingest live Wikimedia, Wikinews, and Wikipedia edit streams into an interactive global crisis radar.",
            "metrics": [
                {"label": "HACKATHON", "value": "WikiVerse IIIT-H"},
                {"label": "STREAMING", "value": "Wikimedia Real-Time"},
                {"label": "RADAR", "value": "Geospatial 60fps"},
            ],
            "model_3d_config": {
                "archetype": "neural_data_core",
                "primary_hex": "#00F0FF",
                "secondary_hex": "#EC4899",
                "wireframe": True,
                "layers_count": 5,
                "rotation_speed": 0.45,
                "camera_position": [0.0, 0.2, 4.0],
                "eyebrow": "CRISISPULSE",
                "subtitle": "REAL-TIME CRISIS INTELLIGENCE & GEOSPATIAL MAPPING ENGINE",
                "core_concept": "Built during the WikiVerse Hackathon at IIIT Hyderabad to ingest live Wikimedia, Wikinews, and Wikipedia edit streams into an interactive global crisis radar.",
                "metric_pills": [
                    "WIKIVERSE HACKATHON (IIIT-H)",
                    "LIVE WIKIMEDIA STREAMING",
                    "GEOSPATIAL INCIDENT RADAR",
                ],
                "pipeline_layers": [
                    {
                        "id": "L1",
                        "name": "Wikimedia & Wikinews Live Event Ingestion",
                        "badge": "stream",
                        "accent": "cyan",
                        "detail": "Polls and filters real-time revision and breaking-news feeds across Wikimedia, Wikipedia, and Wikinews APIs.",
                    },
                    {
                        "id": "L2",
                        "name": "NLP Incident Classification & Severity Scoring",
                        "badge": "~22ms",
                        "accent": "violet",
                        "detail": "Categorizes events into natural disasters, infrastructure outages, and humanitarian alerts while filtering non-crisis noise.",
                    },
                    {
                        "id": "L3",
                        "name": "Entity & Coordinate Geoparsing Pipeline",
                        "badge": "~30ms",
                        "accent": "emerald",
                        "detail": "Extracts affected regions and resolves latitude/longitude coordinates for map projection.",
                    },
                    {
                        "id": "L4",
                        "name": "Interactive Geospatial Cluster & Heatmap Canvas",
                        "badge": "60fps",
                        "accent": "cyan",
                        "detail": "Renders severity-coded incident pins, regional clusters, and timeline playback controls.",
                    },
                    {
                        "id": "L5",
                        "name": "Verified Source Attribution & Cross-Wiki Audit",
                        "badge": "verified",
                        "accent": "violet",
                        "detail": "Links every map alert directly to primary revision diffs and citations for rapid responder triage.",
                    },
                ],
            },
        },
        "telarc": {
            "github_url": "https://github.com/Shreyas-Reddy707?tab=repositories",
            "tagline": "OPEN-SOURCE MULTIMEDIA NLP CORPUS & ARCHIVING PLATFORM",
            "summary": "Engineered at VISWAM.AI (Swecha & IIIT Hyderabad) to collect, validate, and export multimodal Telugu audio, video, image, and text datasets for regional LLM fine-tuning.",
            "metrics": [
                {"label": "COHORT", "value": "200+ Interns"},
                {"label": "DATASET", "value": "Multimodal NLP"},
                {"label": "EXPORT", "value": "CSV & Hugging Face"},
            ],
            "model_3d_config": {
                "archetype": "topography_surface",
                "primary_hex": "#38BDF8",
                "secondary_hex": "#00F0FF",
                "wireframe": True,
                "layers_count": 5,
                "rotation_speed": 0.35,
                "camera_position": [0.0, 0.3, 4.2],
                "eyebrow": "TELARC",
                "subtitle": "OPEN-SOURCE MULTIMEDIA NLP CORPUS & ARCHIVING PLATFORM",
                "core_concept": "Engineered at VISWAM.AI (Swecha & IIIT Hyderabad) to collect, validate, and export multimodal Telugu audio, video, image, and text datasets for regional LLM fine-tuning.",
                "metric_pills": [
                    "200+ INTERN COHORT PIPELINE",
                    "MULTIMODAL NLP CORPUS",
                    "AUTOMATED CSV / METADATA EXPORT",
                ],
                "pipeline_layers": [
                    {
                        "id": "L1",
                        "name": "Multimodal Asset Ingestion (Audio, Video, Image, Text)",
                        "badge": "upload",
                        "accent": "cyan",
                        "detail": "Handles regional field recordings, folk literature scans, and vernacular text contributions across 10 intern teams.",
                    },
                    {
                        "id": "L2",
                        "name": "Dialect, Domain & Speaker Metadata Tagging",
                        "badge": "schema",
                        "accent": "violet",
                        "detail": "Enforces structured linguistic metadata capture required for supervised LLM and ASR model training.",
                    },
                    {
                        "id": "L3",
                        "name": "Data-Quality Validation & Deduplication Gate",
                        "badge": "~18ms",
                        "accent": "emerald",
                        "detail": "Detects corrupted media, missing transcriptions, and duplicate corpus entries before storage.",
                    },
                    {
                        "id": "L4",
                        "name": "Structured Corpus Storage & Indexing",
                        "badge": "indexed",
                        "accent": "cyan",
                        "detail": "Organizes validated records by dialect, media modality, and contributor cohort.",
                    },
                    {
                        "id": "L5",
                        "name": "One-Click CSV & Hugging Face Dataset Export",
                        "badge": "pipeline",
                        "accent": "violet",
                        "detail": "Exports clean training manifests ready for downstream Telugu NLP fine-tuning via GitLab CI/CD.",
                    },
                ],
            },
        },
        "denoising-edge-detection": {
            "github_url": "https://github.com/Shreyas-Reddy707?tab=repositories",
            "tagline": "SPATIAL DENOISING, CANNY EDGE FIDELITY & 3D INTENSITY TOPOGRAPHY",
            "summary": "Interactive computer vision laboratory quantifying how Gaussian, Median, and Bilateral denoising priors recover Canny edge topology and SSIM fidelity under severe sensor noise.",
            "metrics": [
                {"label": "WORKBENCH", "value": "3D Topography"},
                {"label": "FIDELITY", "value": "SSIM & PSNR"},
                {"label": "BENCHMARK", "value": "Gaussian + Salt&Pepper"},
            ],
            "model_3d_config": {
                "archetype": "topography_surface",
                "primary_hex": "#10B981",
                "secondary_hex": "#00F0FF",
                "wireframe": True,
                "layers_count": 5,
                "rotation_speed": 0.35,
                "camera_position": [0.0, 0.4, 4.2],
                "eyebrow": "COMPUTER VISION WORKBENCH",
                "subtitle": "SPATIAL DENOISING, CANNY EDGE FIDELITY & 3D INTENSITY TOPOGRAPHY",
                "core_concept": "Interactive computer vision laboratory quantifying how Gaussian, Median, and Bilateral denoising priors recover Canny edge topology and SSIM fidelity under severe sensor noise.",
                "metric_pills": [
                    "3D INTENSITY TOPOGRAPHY",
                    "REAL-TIME SSIM & PSNR METRICS",
                    "GAUSSIAN & SALT-PEPPER BENCHMARK",
                ],
                "pipeline_layers": [
                    {
                        "id": "L1",
                        "name": "Synthetic Sensor Noise Injection (Gaussian & Salt-and-Pepper)",
                        "badge": "~4ms",
                        "accent": "cyan",
                        "detail": "Applies parameterized variance and impulse corruption to benchmark filter resilience.",
                    },
                    {
                        "id": "L2",
                        "name": "Spatial Prior Filtering (Gaussian, Median, Bilateral)",
                        "badge": "~9ms",
                        "accent": "violet",
                        "detail": "Executes convolution and edge-preserving bilateral smoothing prior to gradient computation.",
                    },
                    {
                        "id": "L3",
                        "name": "Sobel Gradient & Non-Maximum Suppression",
                        "badge": "~6ms",
                        "accent": "emerald",
                        "detail": "Computes gradient magnitude/orientation and thins wide ridges into 1-pixel edge candidates.",
                    },
                    {
                        "id": "L4",
                        "name": "Hysteresis Thresholding & SSIM Fidelity Audit",
                        "badge": "~11ms",
                        "accent": "cyan",
                        "detail": "Measures Structural Similarity Index (SSIM) and Peak Signal-to-Noise Ratio (PSNR) against ground-truth edges.",
                    },
                    {
                        "id": "L5",
                        "name": "Interactive 3D Pixel Intensity Topography Surface",
                        "badge": "3D WebGL",
                        "accent": "violet",
                        "detail": "Projects 2D grayscale luminance into an interactive 3D heightfield showing noise spikes vs. smoothed edge cliffs.",
                    },
                ],
            },
        },
    }

    for proj in data["projects"]:
        slug = proj["slug"]
        if slug in project_upgrades:
            u = project_upgrades[slug]
            proj["github_url"] = u["github_url"]
            proj["tagline"] = u["tagline"]
            proj["summary"] = u["summary"]
            proj["metrics"] = u["metrics"]
            # Merge model_3d_config
            cfg = proj.get("model_3d_config", {})
            cfg.update(u["model_3d_config"])
            proj["model_3d_config"] = cfg

    # 2. Update Work Experiences
    experience_upgrades = {
        "limelite-fde-nz": {
            "role": "Forward Deployed Engineer",
            "organization": "Limelite Constructions · New Zealand (Remote)",
            "is_current": True,
            "summary": "Deploying directly into the sales org: architecting technical workflow solutions and end-to-end automation on top of the existing software stack.",
            "highlights": [
                "Partner directly with construction sales teams to architect technical workflow solutions and end-to-end automation.",
                "Built an automated PDF document generation engine triggered by client building-feature selections using existing software subscriptions.",
                "Spearheaded full-scale CRM data migration from HubSpot to RAVE Build (NZ construction CRM) — cleaning records, establishing step-by-step SOPs, and deploying daily CRM workflow automations.",
            ],
            "tech_stack": [
                "HubSpot CRM",
                "RAVE Build CRM",
                "PDF Automation",
                "Workflow Engineering",
                "SOP Design",
            ],
            "spline_node_config": {
                "accent_hex": "#00F0FF",
                "node_scale": 1.2,
                "status_label": "ACTIVE NODE",
                "z_position": 0.0,
            },
        },
        "viswam-ai-tech-lead": {
            "role": "AI & Software Development Intern (Tech Lead)",
            "organization": "VISWAM.AI · Swecha & IIIT Hyderabad",
            "is_current": False,
            "summary": "Selected as 1 of 10 Tech Leads (from ~200 interns) to direct a 20-intern engineering pod and coordinate across 10 teams building a production Telugu NLP corpus and multilingual AI applications.",
            "highlights": [
                "Led 20 interns directly and coordinated across 10 engineering teams to collect, validate, and standardize Telugu-language datasets for open-source LLM fine-tuning.",
                "Architected and shipped the Telugu Archive Portal (telarc) — a multimodal upload platform with structured metadata logging and automated CSV export.",
                "Built CrisisPulse during the WikiVerse Hackathon at IIIT Hyderabad, integrating live Wikinews, Wikipedia, and Wikimedia APIs with interactive geospatial mapping.",
                "Deployed multilingual AI applications using Python, Ollama, Hugging Face, and Dify via automated GitLab CI/CD pipelines.",
            ],
            "tech_stack": [
                "Python",
                "Ollama",
                "Hugging Face",
                "Dify",
                "GitLab CI/CD",
                "Telugu NLP Corpus",
                "Streamlit",
            ],
            "spline_node_config": {
                "accent_hex": "#A855F7",
                "node_scale": 1.0,
                "status_label": "TECH LEAD POD",
                "z_position": -2.0,
            },
        },
        "icfai-tech-btech": {
            "role": "B.Tech in Computer Science & Engineering (Artificial Intelligence)",
            "organization": "ICFAI Tech University · Hyderabad, India",
            "is_current": True,
            "summary": "Specializing in Generative AI Systems, Zero-Trust RAG Architectures, Autonomous Multi-Agent Pipelines, and Statistical Machine Learning (CGPA: 7.24 / 10).",
            "highlights": [
                "Architected flagship academic and production systems including SecureRAG (5-Layer Zero-Trust RAG defense) and DataMind v2 (Local-First AI Analytics & AutoML Workspace).",
                "Active technical lead in Smart India Hackathon (SIH) 2025 and Devnovate Hack With Hyderabad 3.0.",
                "Completed 22+ industry certifications across Microsoft Azure AI, AWS Cloud Practitioner, NVIDIA DLI Prompt Engineering, Google Cloud Gen AI, EY, Deloitte, and Tata.",
            ],
            "tech_stack": [
                "CGPA: 7.24 / 10",
                "Generative AI & LLMs",
                "LangGraph & RAG",
                "Data Science & AutoML",
                "AWS & Docker",
            ],
            "spline_node_config": {
                "accent_hex": "#10B981",
                "node_scale": 1.0,
                "status_label": "ACADEMIC EXCELLENCE",
                "z_position": -4.0,
            },
        },
    }

    for exp in data["experiences"]:
        slug = exp["slug"]
        if slug in experience_upgrades:
            u = experience_upgrades[slug]
            exp["role"] = u["role"]
            exp["organization"] = u["organization"]
            exp["is_current"] = u["is_current"]
            exp["summary"] = u["summary"]
            exp["highlights"] = u["highlights"]
            exp["tech_stack"] = u["tech_stack"]
            exp["spline_node_config"] = u["spline_node_config"]

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    frontend_manifest_path = BASE_DIR / "frontend" / "public" / "content" / "portfolio_data.json"
    if frontend_manifest_path.parent.exists():
        import copy

        frontend_data = copy.deepcopy(data)
        if "candidate_profile" in frontend_data:
            frontend_data["candidate_profile"].pop("email_cleartext", None)
            frontend_data["candidate_profile"].pop("phone_cleartext", None)
        with open(frontend_manifest_path, "w", encoding="utf-8") as f:
            json.dump(frontend_data, f, indent=2, ensure_ascii=False)
        print("Synchronized sanitized manifest to frontend/public/content/portfolio_data.json.")

    print("Successfully upgraded content/portfolio_data.json with L1-L5 layers and recruiter-grade copy!")

if __name__ == "__main__":
    upgrade_manifest()

