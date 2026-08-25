# IPI (International Prognostic Index) for DLBCL

Real implementation of the IPI scoring system for Diffuse Large B-Cell Lymphoma prognosis.

## What It Does

Calculates the **IPI score (0-5)** and **risk group** based on five clinical risk factors:

| Risk Factor | Criterion | Points |
|-------------|-----------|--------|
| Age | >60 years | 1 |
| LDH | >upper limit of normal | 1 |
| ECOG PS | ≥2 | 1 |
| Ann Arbor Stage | III or IV | 1 |
| Extranodal sites | >1 | 1 |

**Risk Groups and 5-Year Overall Survival:**
| Group | Score | 5-Year OS |
|-------|-------|-----------|
| Low | 0-1 | ~73% |
| Low-Intermediate | 2 | ~51% |
| High-Intermediate | 3 | ~43% |
| High | 4-5 | ~26% |

Also calculates **R-IPI (Revised IPI)** groups:
- Very Good (0 points): ~94% 4-year OS
- Good (1-2 points): ~79% 4-year OS
- Poor (3-5 points): ~55% 4-year OS

## Installation

Zero dependencies — Python 3.7+ stdlib only.

## Usage

### Single Patient

```bash
python ipi_dlbcl.py single \
  --age 65 --ldh-ratio 1.5 --ecog-ps 2 \
  --stage 4 --extranodal-sites 2
```

### Batch Processing

```bash
python ipi_dlbcl.py batch -i patients.csv -o results.csv
```

CSV columns: `age`, `ldh_ratio`, `ecog_ps`, `stage`, `extranodal_sites`

### Python API

```python
from ipi_dlbcl import calculate_ipi

result = calculate_ipi(
    age=65, ldh_ratio=1.5, ecog_ps=2, stage=4, extranodal_sites=2,
)
print(result["ipi_score"])       # 5
print(result["ipi_risk_group"])  # "High"
print(result["ripi_group"])      # "Poor"
```

## Running Tests

```bash
python -m pytest test_ipi_dlbcl.py -v
```

## Clinical Reference

The International Non-Hodgkin's Lymphoma Prognostic Factors Project. A predictive model for aggressive non-Hodgkin's lymphoma. N Engl J Med. 1993;329(14):987-994.

Sehn LH et al. The revised International Prognostic Index (R-IPI) is a better predictor of outcome than the standard IPI for patients with diffuse large B-cell lymphoma treated with R-CHOP. Blood. 2007;109(5):1857-1861.

## License

MIT
