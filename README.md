# IPI DLBCL Prognostic Index

A reproducible calculator for the original International Prognostic Index (IPI) and Revised IPI (R-IPI) used for prognostic stratification in diffuse large B-cell lymphoma. A static browser interface, Python CLI, batch CSV processor and optional FastAPI service are provided.

## Calculation

Each of the following contributes one point: age >60 years; serum LDH above the laboratory upper limit of normal (ratio >1); ECOG performance status ≥2; Ann Arbor stage III–IV; and more than one extranodal disease site.

| Score | Original IPI | Historical 5-year OS¹ | R-IPI group | Historical 4-year OS² |
| --- | --- | --- | --- | --- |
| 0 | Low | 73% | Very Good | 94% |
| 1 | Low | 73% | Good | 79% |
| 2 | Low-Intermediate | 51% | Good | 79% |
| 3 | High-Intermediate | 43% | Poor | 55% |
| 4–5 | High | 26% | Poor | 55% |

¹ Original IPI outcomes (1980s pre-rituximab cohort). ² R-IPI outcomes from an R-CHOP-treated cohort. The endpoints, populations and treatment eras differ; these percentages must not be combined or interpreted as individualized probabilities.

This is a **prognostic tool, not a treatment decision algorithm**. Treatment selection requires contemporary clinical assessment, tumor biology, patient factors and applicable guidelines. Educational/research use only.

## Browser calculator

Open `web/index.html` in a browser, enter the five factors, and select **Calculate IPI**. The result includes the score, IPI/R-IPI classification, factor breakdown and historical group outcomes.

Optional CSV upload uses headers `age,ldh_ratio,ecog_ps,stage,extranodal_sites` (other columns are ignored in the downloaded output). The browser processes up to 10,000 data rows / 2 MB and downloads only row numbers and calculated results. Files remain on the device; the static app makes no network API calls and uses no cookies, analytics or browser storage. **Do not submit patient identifiers/PHI.** All source code is public.

## Python CLI

The core calculation has no third-party dependencies. From the repository root:

```sh
python cli.py single --age 65 --ldh-ratio 1.5 --ecog-ps 1 --stage 3 --extranodal-sites 2
python cli.py batch -i sample.csv -o results.csv
```

The batch CLI preserves input columns, which may contain sensitive data. Avoid using identifiable clinical records. CSV output escapes spreadsheet formula prefixes. Invalid data rows are marked with an error; missing or duplicate headers are rejected.

The repository retains additional supervisory CLI commands: `audit`, `chat` and `verify-audit`. They use deterministic mock worker logic and must not be interpreted as real clinical surveillance, medical triage or LLM-powered analysis. Audit entries live only in the running process and are signed with HMAC-SHA256. A production deployment must set `AUDIT_SECRET_KEY`; the built-in PHI pattern filter is **not** a de-identification guarantee.

## Local API / Docker

```sh
python -m pip install -r requirements.txt
uvicorn agents.api:app --reload
# Open http://127.0.0.1:8000/
```

Or start a container with a strong secret:

```sh
docker build -t ipi-dlbcl-prognostic-index .
docker run --rm -p 8000:8000 -e AUDIT_SECRET_KEY='replace-with-a-long-random-secret' ipi-dlbcl-prognostic-index
```

`POST /api/ipi` evaluates an IPI input object; `GET /health` checks the service. Existing audit/chat endpoints remain available but are not supported on GitHub Pages (which is static). The supervisory endpoints require the server-side `SUPERVISOR_API_TOKEN` value and the matching `X-API-Token` request header. Without the environment variable these routes fail closed with HTTP 503. Use TLS and rate limiting for any internet-facing service.

## Tests

```sh
python -m pip install -r requirements-dev.txt
pytest -q
node --check web/ipi.js
node --test tests/test_web.cjs
```

GitHub Actions tests Python 3.10–3.12 and the browser calculation logic with Node.js.

## Evidence

- International Non-Hodgkin's Lymphoma Prognostic Factors Project. *N Engl J Med.* 1993;329:987–994. [DOI: 10.1056/NEJM199309303291402](https://doi.org/10.1056/NEJM199309303291402).
- Sehn LH, et al. *Blood.* 2007;109:1857–1861. [DOI: 10.1182/blood-2006-08-038257](https://doi.org/10.1182/blood-2006-08-038257).

Requires a modern browser with JavaScript, the File API and Blob URLs (e.g., current Chrome, Firefox, Safari or Edge). No Python-in-browser runtime is needed because the standalone JavaScript calculator implements the same five-factor algorithm.

## License

MIT; see [LICENSE](LICENSE).
