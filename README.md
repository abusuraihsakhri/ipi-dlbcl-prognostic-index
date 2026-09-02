# Ipi Dlbcl Prognostic Index

> **Domain:** Medical Oncology & Cancer Staging Systems  
> **Reference Guidelines & Standards:** `AJCC Cancer Staging Manual & NCCN Clinical Practice Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

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

Zero-dependency Python implementation.
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

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
- **`main()`** — calculates and validates main parameters.

---

## 📐 Mathematical Formulation & Logic

```text
  Calculates the IPI score (0-5) and risk group for DLBCL prognosis.
  Also calculates R-IPI (Revised IPI) groups:
  Calculate IPI and R-IPI scores for DLBCL.
  score = 0
  elif score == 2:
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --input data.csv
```

### Parameter Reference
- `--interactive`: Launch guided terminal interactive wizard.
- `--input <path>`: Evaluate input from JSON or CSV specification.
- `--json`: Output deterministic structured results in JSON format.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Parameter / observation metric | Required |
| `v1` | Parameter / observation metric | Required |
| `v2` | Parameter / observation metric | Required |
| `v3` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t ipi-dlbcl-prognostic-index .
docker run -p 8000:8000 ipi-dlbcl-prognostic-index
```
