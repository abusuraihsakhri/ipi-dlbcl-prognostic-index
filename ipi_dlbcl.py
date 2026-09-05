#!/usr/bin/env python3
"""
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
"""

import argparse
import csv
import json
import sys
from typing import Dict, Any, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# 5-year overall survival by IPI risk group (%)
IPI_SURVIVAL = {
    "Low": 73.0,
    "Low-Intermediate": 51.0,
    "High-Intermediate": 43.0,
    "High": 26.0,
}

# R-IPI 4-year overall survival (%)
RIPI_SURVIVAL = {
    "Very Good": 94.0,
    "Good": 79.0,
    "Poor": 55.0,
}


# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------

def calculate_ipi(
    age: int,
    ldh_ratio: float,
    ecog_ps: int,
    stage: int,
    extranodal_sites: int,
) -> Dict[str, Any]:
    """
    Calculate IPI and R-IPI scores for DLBCL.

    Parameters:
        age: Patient age in years
        ldh_ratio: LDH / upper limit of normal (e.g., 1.5 means 1.5x ULN).
                   Use 1.0 for normal, >1.0 for elevated.
        ecog_ps: ECOG performance status (0-4)
        stage: Ann Arbor stage (1-4)
        extranodal_sites: Number of extranodal disease sites

    Returns:
        Dict with IPI score, risk group, R-IPI group, survival estimates.
    """
    # Validate
    if age < 0:
        raise ValueError("Age must be non-negative")
    if ldh_ratio < 0:
        raise ValueError("LDH ratio must be non-negative")
    if ecog_ps < 0 or ecog_ps > 4:
        raise ValueError(f"ECOG PS must be 0-4, got {ecog_ps}")
    if stage < 1 or stage > 4:
        raise ValueError(f"Ann Arbor stage must be 1-4, got {stage}")
    if extranodal_sites < 0:
        raise ValueError("Extranodal sites must be non-negative")

    # Score each factor
    factors = {}
    score = 0

    # Age > 60
    age_point = 1 if age > 60 else 0
    factors["age_over_60"] = {"value": age, "point": age_point}
    score += age_point

    # LDH > normal (>1.0)
    ldh_point = 1 if ldh_ratio > 1.0 else 0
    factors["ldh_elevated"] = {"ratio": ldh_ratio, "point": ldh_point}
    score += ldh_point

    # ECOG ≥ 2
    ecog_point = 1 if ecog_ps >= 2 else 0
    factors["ecog_ge_2"] = {"value": ecog_ps, "point": ecog_point}
    score += ecog_point

    # Stage III-IV (Ann Arbor 3 or 4)
    stage_point = 1 if stage >= 3 else 0
    factors["stage_iii_iv"] = {"value": stage, "point": stage_point}
    score += stage_point

    # Extranodal sites > 1
    extranodal_point = 1 if extranodal_sites > 1 else 0
    factors["extranodal_gt_1"] = {"count": extranodal_sites, "point": extranodal_point}
    score += extranodal_point

    # IPI risk group
    ipi_group = _ipi_risk_group(score)

    # R-IPI group
    ripi_group = _ripi_group(score)

    return {
        "tool": "ipi-dlbcl-prognostic-index",
        "ipi_score": score,
        "ipi_risk_group": ipi_group,
        "five_year_survival_pct": IPI_SURVIVAL[ipi_group],
        "ripi_group": ripi_group,
        "ripi_four_year_survival_pct": RIPI_SURVIVAL[ripi_group],
        "risk_factors": factors,
        "classification": f"IPI {score}/5 - {ipi_group} Risk",
        "clinical_recommendation": _recommendation(ipi_group, score),
    }


def _ipi_risk_group(score: int) -> str:
    """Map IPI score to risk group."""
    if score <= 1:
        return "Low"
    elif score == 2:
        return "Low-Intermediate"
    elif score == 3:
        return "High-Intermediate"
    else:
        return "High"


def _ripi_group(score: int) -> str:
    """Map IPI score to R-IPI group."""
    if score == 0:
        return "Very Good"
    elif score <= 2:
        return "Good"
    else:
        return "Poor"


def _recommendation(group: str, score: int) -> str:
    """Generate treatment recommendation based on IPI risk group."""
    if group == "Low":
        return (
            "Low-risk DLBCL. Excellent prognosis with standard R-CHOP "
            "(rituximab, cyclophosphamide, doxorubicin, vincristine, prednisone) "
            "× 6 cycles. 5-year overall survival ~73%. "
            "Consider abbreviated therapy (4-6 cycles) in select patients."
        )
    elif group == "Low-Intermediate":
        return (
            "Low-intermediate risk DLBCL. Good prognosis with R-CHOP × 6 cycles. "
            "5-year overall survival ~51%. Consider interim PET-adapted approach. "
            "Consolidation radiation for residual disease."
        )
    elif group == "High-Intermediate":
        return (
            "High-intermediate risk DLBCL. Standard R-CHOP × 6-8 cycles. "
            "5-year overall survival ~43%. Consider dose-adjusted EPOCH-R. "
            "Evaluate for CNS prophylaxis. Clinical trial enrollment encouraged."
        )
    else:
        return (
            "High-risk DLBCL. Poor prognosis with standard therapy. "
            "5-year overall survival ~26%. Consider intensified regimens "
            "(DA-EPOCH-R, R-ACVBP). CNS prophylaxis recommended. "
            "Early evaluation for CAR-T or stem cell transplant. "
            "Clinical trial enrollment strongly encouraged."
        )


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

REQUIRED_CSV_FIELDS = {"age", "ldh_ratio", "ecog_ps", "stage", "extranodal_sites"}


def _validate_csv_path(path: str) -> str:
    """Validate CSV file path to prevent path traversal."""
    import os
    # Ensure the path does not contain null bytes or traversal sequences
    if "\x00" in path:
        raise ValueError("Path contains null bytes")
    # Check for ".." in path components (handles both / and \\ separators)
    normalized = path.replace("\\", "/")
    if ".." in normalized.split("/"):
        raise ValueError("Path traversal detected")
    resolved = os.path.realpath(path)
    return resolved


def process_batch(input_csv: str, output_csv: str) -> int:
    """Process a CSV of patients and write IPI results."""
    input_csv = _validate_csv_path(input_csv)
    output_csv = _validate_csv_path(output_csv)

    with open(input_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    # Validate required fields present
    missing_fields = REQUIRED_CSV_FIELDS - set(fieldnames)
    if missing_fields:
        raise ValueError(f"Input CSV missing required fields: {missing_fields}")

    out_fields = fieldnames + [
        "ipi_score", "ipi_risk_group", "five_year_survival_pct",
        "ripi_group", "clinical_recommendation",
    ]
    out_rows = []
    for r in rows:
        try:
            res = calculate_ipi(
                age=int(r["age"]),
                ldh_ratio=float(r["ldh_ratio"]),
                ecog_ps=int(r["ecog_ps"]),
                stage=int(r["stage"]),
                extranodal_sites=int(r["extranodal_sites"]),
            )
            row_dict = dict(r)
            row_dict["ipi_score"] = res["ipi_score"]
            row_dict["ipi_risk_group"] = res["ipi_risk_group"]
            row_dict["five_year_survival_pct"] = res["five_year_survival_pct"]
            row_dict["ripi_group"] = res["ripi_group"]
            row_dict["clinical_recommendation"] = res["clinical_recommendation"]
        except (ValueError, KeyError) as e:
            row_dict = dict(r)
            row_dict["ipi_score"] = f"ERROR: {e}"
            row_dict["ipi_risk_group"] = ""
            row_dict["five_year_survival_pct"] = ""
            row_dict["ripi_group"] = ""
            row_dict["clinical_recommendation"] = ""
        out_rows.append(row_dict)

    with open(output_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Processed {len(out_rows)} records -> {output_csv}")
    return len(out_rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="IPI (International Prognostic Index) for DLBCL"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single evaluation
    sp = subparsers.add_parser("single", help="Evaluate a single DLBCL patient")
    sp.add_argument("--age", type=int, required=True,
                    help="Patient age in years")
    sp.add_argument("--ldh-ratio", type=float, required=True,
                    help="LDH / upper limit of normal (e.g., 1.5 for 1.5x ULN)")
    sp.add_argument("--ecog-ps", type=int, required=True,
                    help="ECOG performance status (0-4)")
    sp.add_argument("--stage", type=int, required=True,
                    help="Ann Arbor stage (1-4)")
    sp.add_argument("--extranodal-sites", type=int, required=True,
                    help="Number of extranodal disease sites")

    # Batch processing
    bp = subparsers.add_parser("batch", help="Batch process CSV file")
    bp.add_argument("-i", "--input", required=True, help="Input CSV file")
    bp.add_argument("-o", "--output", default="results.csv", help="Output CSV file")

    # Audit command (enterprise supervisor)
    ap = subparsers.add_parser("audit", help="Run supervisor audit task")
    ap.add_argument("--task-id", default="CLI-AUDIT-01", help="Task identifier")
    ap.add_argument("--target", default="CLI-TARGET-01", help="Target identifier")
    ap.add_argument("--primary-metric", type=float, default=10.0, help="Primary metric")
    ap.add_argument("--secondary-metric", type=float, default=3.0, help="Secondary metric")
    ap.add_argument("--status", default="NOMINAL", help="Status descriptor")
    ap.add_argument("--critical", action="store_true", help="Critical flag")

    # Chat command (enterprise supervisor)
    cp = subparsers.add_parser("chat", help="Supervisory chat query")
    cp.add_argument("query", nargs="+", help="Query text")

    # Verify audit command
    vp = subparsers.add_parser("verify-audit", help="Verify HMAC audit trail integrity")

    args = parser.parse_args(argv)

    if args.command == "single":
        result = calculate_ipi(
            age=args.age,
            ldh_ratio=args.ldh_ratio,
            ecog_ps=args.ecog_ps,
            stage=args.stage,
            extranodal_sites=args.extranodal_sites,
        )
        print(json.dumps(result, indent=2))
        return 0
    elif args.command == "batch":
        process_batch(args.input, args.output)
        return 0
    elif args.command == "audit":
        from agents.supervisor import SystemSupervisor
        from agents.models import SystemTaskPayload
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id=args.task_id,
            target_identifier=args.target,
            primary_metric=args.primary_metric,
            secondary_metric=args.secondary_metric,
            status_descriptor=args.status,
            is_critical_flag=args.critical,
        )
        dossier = supervisor.process_task(payload)
        print(json.dumps(dossier.to_dict(), indent=2, default=str))
        return 0
    elif args.command == "chat":
        from agents.supervisor import SystemSupervisor
        supervisor = SystemSupervisor(model_provider="mock")
        query = " ".join(args.query)
        response = supervisor.query_supervisory_chat(query)
        print(json.dumps({"response": response}, indent=2))
        return 0
    elif args.command == "verify-audit":
        from agents.base import AuditLogger
        valid = AuditLogger.verify_integrity()
        trail_len = len(AuditLogger.get_trail())
        print(json.dumps({"audit_valid": valid, "trail_length": trail_len}, indent=2))
        return 0 if valid else 1


if __name__ == "__main__":
    main()
