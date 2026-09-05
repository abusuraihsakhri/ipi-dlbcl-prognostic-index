#!/usr/bin/env python3
"""Tests for IPI (International Prognostic Index) for DLBCL - 20 real clinical tests."""

import json
import pytest
from ipi_dlbcl import (
    calculate_ipi,
    process_batch,
    _ipi_risk_group,
    _ripi_group,
    _validate_csv_path,
    REQUIRED_CSV_FIELDS,
    IPI_SURVIVAL,
    RIPI_SURVIVAL,
)


# ---------------------------------------------------------------------------
# Individual risk factor scoring
# ---------------------------------------------------------------------------

class TestRiskFactors:
    def test_age_over_60(self):
        """Age >60 contributes 1 point."""
        res = calculate_ipi(age=65, ldh_ratio=0.8, ecog_ps=0, stage=1, extranodal_sites=0)
        assert res["risk_factors"]["age_over_60"]["point"] == 1
        assert res["ipi_score"] == 1

    def test_age_exactly_60(self):
        """Age exactly 60 does NOT contribute (must be >60)."""
        res = calculate_ipi(age=60, ldh_ratio=0.8, ecog_ps=0, stage=1, extranodal_sites=0)
        assert res["risk_factors"]["age_over_60"]["point"] == 0
        assert res["ipi_score"] == 0

    def test_ldh_elevated(self):
        """LDH >1.0 contributes 1 point."""
        res = calculate_ipi(age=50, ldh_ratio=1.5, ecog_ps=0, stage=1, extranodal_sites=0)
        assert res["risk_factors"]["ldh_elevated"]["point"] == 1
        assert res["ipi_score"] == 1

    def test_ldh_normal(self):
        """LDH exactly 1.0 does NOT contribute (must be >1.0)."""
        res = calculate_ipi(age=50, ldh_ratio=1.0, ecog_ps=0, stage=1, extranodal_sites=0)
        assert res["risk_factors"]["ldh_elevated"]["point"] == 0

    def test_ecog_ge_2(self):
        """ECOG ≥2 contributes 1 point."""
        res = calculate_ipi(age=50, ldh_ratio=0.8, ecog_ps=2, stage=1, extranodal_sites=0)
        assert res["risk_factors"]["ecog_ge_2"]["point"] == 1
        assert res["ipi_score"] == 1

    def test_ecog_below_2(self):
        """ECOG 1 does NOT contribute."""
        res = calculate_ipi(age=50, ldh_ratio=0.8, ecog_ps=1, stage=1, extranodal_sites=0)
        assert res["risk_factors"]["ecog_ge_2"]["point"] == 0

    def test_stage_iii(self):
        """Stage III contributes 1 point."""
        res = calculate_ipi(age=50, ldh_ratio=0.8, ecog_ps=0, stage=3, extranodal_sites=0)
        assert res["risk_factors"]["stage_iii_iv"]["point"] == 1
        assert res["ipi_score"] == 1

    def test_stage_ii(self):
        """Stage II does NOT contribute."""
        res = calculate_ipi(age=50, ldh_ratio=0.8, ecog_ps=0, stage=2, extranodal_sites=0)
        assert res["risk_factors"]["stage_iii_iv"]["point"] == 0

    def test_extranodal_gt_1(self):
        """Extranodal sites >1 contributes 1 point."""
        res = calculate_ipi(age=50, ldh_ratio=0.8, ecog_ps=0, stage=1, extranodal_sites=2)
        assert res["risk_factors"]["extranodal_gt_1"]["point"] == 1
        assert res["ipi_score"] == 1

    def test_extranodal_exactly_1(self):
        """Exactly 1 extranodal site does NOT contribute."""
        res = calculate_ipi(age=50, ldh_ratio=0.8, ecog_ps=0, stage=1, extranodal_sites=1)
        assert res["risk_factors"]["extranodal_gt_1"]["point"] == 0


# ---------------------------------------------------------------------------
# IPI risk groups
# ---------------------------------------------------------------------------

class TestIPIRiskGroups:
    def test_score_0_low(self):
        assert _ipi_risk_group(0) == "Low"

    def test_score_1_low(self):
        assert _ipi_risk_group(1) == "Low"

    def test_score_2_low_int(self):
        assert _ipi_risk_group(2) == "Low-Intermediate"

    def test_score_3_high_int(self):
        assert _ipi_risk_group(3) == "High-Intermediate"

    def test_score_4_high(self):
        assert _ipi_risk_group(4) == "High"

    def test_score_5_high(self):
        assert _ipi_risk_group(5) == "High"


# ---------------------------------------------------------------------------
# Full IPI calculations
# ---------------------------------------------------------------------------

class TestFullIPI:
    def test_score_0(self):
        """Young patient, normal values → IPI 0, Low risk."""
        res = calculate_ipi(age=45, ldh_ratio=0.9, ecog_ps=0, stage=1, extranodal_sites=0)
        assert res["ipi_score"] == 0
        assert res["ipi_risk_group"] == "Low"
        assert res["five_year_survival_pct"] == 73.0

    def test_score_5(self):
        """All risk factors present → IPI 5, High risk."""
        res = calculate_ipi(age=70, ldh_ratio=2.0, ecog_ps=3, stage=4, extranodal_sites=3)
        assert res["ipi_score"] == 5
        assert res["ipi_risk_group"] == "High"
        assert res["five_year_survival_pct"] == 26.0

    def test_score_3_high_intermediate(self):
        """3 risk factors → High-Intermediate."""
        res = calculate_ipi(age=65, ldh_ratio=1.5, ecog_ps=0, stage=4, extranodal_sites=0)
        assert res["ipi_score"] == 3
        assert res["ipi_risk_group"] == "High-Intermediate"

    def test_classification_string(self):
        res = calculate_ipi(age=45, ldh_ratio=0.9, ecog_ps=0, stage=1, extranodal_sites=0)
        assert "IPI" in res["classification"]
        assert "Low" in res["classification"]

    def test_has_recommendation(self):
        res = calculate_ipi(age=45, ldh_ratio=0.9, ecog_ps=0, stage=1, extranodal_sites=0)
        assert len(res["clinical_recommendation"]) > 10


# ---------------------------------------------------------------------------
# R-IPI groups
# ---------------------------------------------------------------------------

class TestRIPI:
    def test_ripi_very_good(self):
        assert _ripi_group(0) == "Very Good"

    def test_ripi_good(self):
        assert _ripi_group(1) == "Good"
        assert _ripi_group(2) == "Good"

    def test_ripi_poor(self):
        assert _ripi_group(3) == "Poor"
        assert _ripi_group(5) == "Poor"

    def test_ripi_in_result(self):
        res = calculate_ipi(age=45, ldh_ratio=0.9, ecog_ps=0, stage=1, extranodal_sites=0)
        assert res["ripi_group"] == "Very Good"
        assert res["ripi_four_year_survival_pct"] == 94.0


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestValidation:
    def test_negative_age(self):
        with pytest.raises(ValueError):
            calculate_ipi(age=-1, ldh_ratio=1.0, ecog_ps=0, stage=1, extranodal_sites=0)

    def test_invalid_ecog(self):
        with pytest.raises(ValueError):
            calculate_ipi(age=50, ldh_ratio=1.0, ecog_ps=5, stage=1, extranodal_sites=0)

    def test_invalid_stage(self):
        with pytest.raises(ValueError):
            calculate_ipi(age=50, ldh_ratio=1.0, ecog_ps=0, stage=5, extranodal_sites=0)


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

class TestBatch:
    def test_batch_basic(self, tmp_path):
        csv_in = tmp_path / "in.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "age,ldh_ratio,ecog_ps,stage,extranodal_sites\n"
            "45,0.9,0,1,0\n"
            "70,2.0,3,4,3\n",
            encoding="utf-8",
        )
        count = process_batch(str(csv_in), str(csv_out))
        assert count == 2
        assert csv_out.exists()
        content = csv_out.read_text(encoding="utf-8")
        assert "ipi_score" in content
        assert "ipi_risk_group" in content

    def test_batch_missing_fields(self, tmp_path):
        """Batch processing rejects CSV missing required fields."""
        csv_in = tmp_path / "bad.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "age,ecog_ps,stage\n"
            "45,0,1\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="missing required fields"):
            process_batch(str(csv_in), str(csv_out))

    def test_batch_empty_csv(self, tmp_path):
        """Batch processing rejects CSV with no data rows."""
        csv_in = tmp_path / "empty.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "age,ldh_ratio,ecog_ps,stage,extranodal_sites\n",
            encoding="utf-8",
        )
        count = process_batch(str(csv_in), str(csv_out))
        assert count == 0


# ---------------------------------------------------------------------------
# CSV path validation
# ---------------------------------------------------------------------------

class TestCsvPathValidation:
    def test_valid_path(self):
        result = _validate_csv_path("data.csv")
        assert result.endswith("data.csv")

    def test_rejects_path_traversal(self):
        """Path traversal attempts are rejected."""
        with pytest.raises(ValueError, match="traversal"):
            _validate_csv_path("../../../etc/passwd")

    def test_rejects_null_bytes(self):
        """Null bytes in path are rejected."""
        with pytest.raises(ValueError, match="null bytes"):
            _validate_csv_path("data\x00.csv")

    def test_required_fields_constant(self):
        """Required fields set contains all expected fields."""
        assert REQUIRED_CSV_FIELDS == {"age", "ldh_ratio", "ecog_ps", "stage", "extranodal_sites"}


# ---------------------------------------------------------------------------
# CLI command tests
# ---------------------------------------------------------------------------

class TestCliCommands:
    def test_cli_single(self):
        from ipi_dlbcl import main
        result = main(["single", "--age", "45", "--ldh-ratio", "0.9",
                       "--ecog-ps", "0", "--stage", "1", "--extranodal-sites", "0"])
        assert result == 0

    def test_cli_batch(self, tmp_path):
        from ipi_dlbcl import main
        csv_in = tmp_path / "in.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "age,ldh_ratio,ecog_ps,stage,extranodal_sites\n"
            "45,0.9,0,1,0\n",
            encoding="utf-8",
        )
        result = main(["batch", "-i", str(csv_in), "-o", str(csv_out)])
        assert result == 0

    def test_cli_audit(self):
        from ipi_dlbcl import main
        result = main(["audit", "--task-id", "TEST-001", "--primary-metric", "10.0"])
        assert result == 0

    def test_cli_chat(self):
        from ipi_dlbcl import main
        result = main(["chat", "test", "query"])
        assert result == 0

    def test_cli_verify_audit(self):
        from ipi_dlbcl import main
        result = main(["verify-audit"])
        assert result == 0
