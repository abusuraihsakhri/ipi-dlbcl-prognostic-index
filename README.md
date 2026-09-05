# IPI DLBCL Prognostic Index

> **Domain:** Medical Oncology & Cancer Staging Systems
> **Reference Guidelines & Standards:** AJCC Cancer Staging Manual & NCCN Clinical Practice Guidelines

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

International Prognostic Index (IPI) for Diffuse Large B-Cell Lymphoma

Calculates the IPI score (0-5) and risk group for DLBCL prognosis.

Risk factors (1 point each):
  - Age > 60
  - LDH > upper limit of normal
  - ECOG performance status ≥ 2
  - Ann Arbor Stage III or IV
  - Extranodal sites > 1

Risk groups:
  Low:             0-1 points  → 5-year OS ~73%
  Low-Intermediate: 2 points   → 5-year OS ~51%
  High-Intermediate: 3 points  → 5-year OS ~43%
  High:            4-5 points  → 5-year OS ~26%

Also calculates R-IPI (Revised IPI) groups:
  Very Good: 0 points  → 4-year OS ~94%
  Good:      1-2 points → 4-year OS ~79%
  Poor:      3-5 points → 4-year OS ~55%

License: MIT

---

## Installation

```bash
pip install fastapi uvicorn pydantic pytest
```

---

## Key Capabilities & Algorithmic Modules

### Analytical Functions

- **`calculate_ipi()`**: Calculate IPI and R-IPI scores for DLBCL.

Parameters:
    age: Patient age in years
    ldh_ratio: LDH / upper limit of normal (e.g., 1.5 means 1.5x ULN).
               Use 1.0 for normal, >1.0 for elevated.
    ecog_ps: ECOG performance status (0-4)
    stage: Ann Arbor stage (1-4)
    extranodal_sites: Number of extranodal disease sites

Returns:
    Dict with IPI score, risk group, R-IPI group, survival estimates.

- **`process_batch()`**: Process a CSV of patients and write IPI results.
- **`main()`** — CLI entry point for all commands.

---

## CLI Quickstart & Usage

### 1. Single Patient Evaluation
```bash
python cli.py single --age 65 --ldh-ratio 1.5 --ecog-ps 1 --stage 3 --extranodal-sites 2
```

### 2. Batch CSV Processing
```bash
python cli.py batch -i patients.csv -o results.csv
```

### 3. Enterprise Supervisor Audit
```bash
python cli.py audit --task-id TASK-001 --primary-metric 15.0 --status NOMINAL
```

### 4. Supervisory Chat
```bash
python cli.py chat "Explain IPI scoring"
```

### 5. Verify Audit Trail
```bash
python cli.py verify-audit
```

### Parameter Reference
- `single`: Evaluate a single patient (requires --age, --ldh-ratio, --ecog-ps, --stage, --extranodal-sites)
- `batch`: Batch process CSV file (requires -i/--input, optional -o/--output)
- `audit`: Run supervisor audit task
- `chat`: Supervisory chat query
- `verify-audit`: Verify HMAC audit trail integrity

### Input CSV Schema (for batch processing)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `age` | Patient age in years | Required |
| `ldh_ratio` | LDH / upper limit of normal | Required |
| `ecog_ps` | ECOG performance status (0-4) | Required |
| `stage` | Ann Arbor stage (1-4) | Required |
| `extranodal_sites` | Number of extranodal disease sites | Required |

---

## Mathematical Formulation

```
IPI Score = Σ risk factors (0-5)

Risk factors (1 point each):
  - Age > 60
  - LDH ratio > 1.0 (elevated)
  - ECOG PS ≥ 2
  - Ann Arbor Stage III or IV (≥ 3)
  - Extranodal sites > 1

IPI Risk Groups:
  Score 0-1  → Low
  Score 2    → Low-Intermediate
  Score 3    → High-Intermediate
  Score 4-5  → High

R-IPI Groups:
  Score 0    → Very Good
  Score 1-2  → Good
  Score 3-5  → Poor
```

---

## Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances, Claude, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable in production:

```bash
# Linux/macOS
export AUDIT_SECRET_KEY="your-secure-random-key"

# Windows
set AUDIT_SECRET_KEY=your-secure-random-key
```

---

## Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## Container Deployment

```bash
docker build -t ipi-dlbcl-prognostic-index .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key ipi-dlbcl-prognostic-index
```

Or using docker-compose:

```bash
AUDIT_SECRET_KEY=your-secure-key docker-compose up
```
