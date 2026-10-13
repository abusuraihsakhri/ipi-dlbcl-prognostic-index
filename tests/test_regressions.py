"""Regression tests for clinical boundaries, CSV hygiene, and audit integrity."""
import csv
import math
import pytest

from ipi_dlbcl import calculate_ipi, process_batch
from agents.base import AuditTrail
from agents.api import IPIPatient, api_ipi, app

BASE = dict(age=60, ldh_ratio=1.0, ecog_ps=1, stage=2, extranodal_sites=1)


@pytest.mark.parametrize("key,value", [
    ("age", 61), ("ldh_ratio", 1.0001), ("ecog_ps", 2),
    ("stage", 3), ("extranodal_sites", 2),
])
def test_boundary_contributes_exactly_one_point(key, value):
    assert calculate_ipi(**BASE)["ipi_score"] == 0
    assert calculate_ipi(**{**BASE, key: value})["ipi_score"] == 1


@pytest.mark.parametrize("key,value", [
    ("age", True), ("age", 60.5), ("ecog_ps", 2.5),
    ("stage", 3.4), ("extranodal_sites", True),
    ("ldh_ratio", float("nan")), ("ldh_ratio", float("inf")),
    ("ldh_ratio", True), ("ldh_ratio", -1.0),
])
def test_invalid_input_is_rejected(key, value):
    with pytest.raises(ValueError):
        calculate_ipi(**{**BASE, key: value})


def test_no_automatic_chemotherapy_advice():
    for age in (50, 65):
        r = calculate_ipi(**{**BASE, "age": age})
        assert "not a treatment recommendation" in r["clinical_recommendation"]
        assert "R-CHOP" not in r["clinical_recommendation"]


def test_csv_spreadsheet_formula_and_invalid_row(tmp_path):
    inp, out = tmp_path / "in.csv", tmp_path / "out.csv"
    inp.write_text("age,ldh_ratio,ecog_ps,stage,extranodal_sites,note\n"
                   "60,1,1,2,1,=HYPERLINK(\"evil\")\n"
                   "61,NaN,1,2,1,@SUM(1)\n", encoding="utf-8")
    assert process_batch(str(inp), str(out)) == 2
    with out.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["note"].startswith("'=")
    assert rows[1]["note"].startswith("'@")
    assert rows[1]["ipi_score"].startswith("ERROR")


def test_csv_rejects_reserved_and_duplicate_columns(tmp_path):
    for header in ["age,ldh_ratio,ecog_ps,stage,extranodal_sites,ipi_score",
                   "age,ldh_ratio,ecog_ps,stage,extranodal_sites,age"]:
        inp, out = tmp_path / "in.csv", tmp_path / "out.csv"
        inp.write_text(header + "\n", encoding="utf-8")
        with pytest.raises(ValueError):
            process_batch(str(inp), str(out))


def test_audit_checks_signatures_not_only_prev_hash():
    audit = AuditTrail(secret_key="unit-test-only")
    audit.log("worker", "system", "INIT", {"task": "T1"})
    audit.log("worker", "system", "NEXT", {"task": "T2"})
    assert audit.verify_integrity()
    # Returned snapshot cannot modify audit state.
    audit.get_trail()[0]["actor"] = "bad"
    assert audit.verify_integrity()
    # Mutation of a signed field with correct chain links must be detected.
    audit.logs[0]["actor"] = "bad"
    assert not audit.verify_integrity()


def test_api_serves_calculator_and_endpoint():
    r = api_ipi(IPIPatient(**BASE))
    assert r["ipi_score"] == 0
    paths = [route.path for route in app.routes]
    assert "/api/ipi" in paths
    assert "/" in paths


def test_supervisor_api_requires_configured_token(monkeypatch):
    from fastapi import HTTPException
    from agents.api import require_supervisor_token
    monkeypatch.delenv("SUPERVISOR_API_TOKEN", raising=False)
    with pytest.raises(HTTPException) as exc:
        require_supervisor_token(None)
    assert exc.value.status_code == 503
    monkeypatch.setenv("SUPERVISOR_API_TOKEN", "test-secret-only")
    with pytest.raises(HTTPException) as exc:
        require_supervisor_token("wrong-secret")
    assert exc.value.status_code == 401
    assert require_supervisor_token("test-secret-only") is None


def test_js_python_parity_when_node_available():
    import shutil
    import subprocess
    import json
    from pathlib import Path
    if not shutil.which("node"):
        pytest.skip("Node.js is not installed")
    cases = [
        {**BASE, "age": 59, "ldh_ratio": 0.9, "ecog_ps": 0, "stage": 1, "extranodal_sites": 0},
        {**BASE, "age": 61},
        {**BASE, "age": 61, "ldh_ratio": 1.2},
        {**BASE, "age": 61, "ldh_ratio": 1.2, "ecog_ps": 2},
        {**BASE, "age": 61, "ldh_ratio": 1.2, "ecog_ps": 2, "stage": 3},
        {**BASE, "age": 61, "ldh_ratio": 1.2, "ecog_ps": 2, "stage": 3, "extranodal_sites": 2},
    ]
    script = "const calc=require('./web/ipi.js').calculateIPI; let cases=JSON.parse(process.argv[1]);console.log(JSON.stringify(cases.map(calc)));" 
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(["node", "-e", script, json.dumps(cases)],cwd=root,check=True,capture_output=True,text=True)
    js_results = json.loads(result.stdout)
    for inp, javascript in zip(cases, js_results):
        assert javascript == calculate_ipi(**inp)
