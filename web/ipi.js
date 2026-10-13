"use strict";
(function (root) {
  const ipiSurvival = {"Low": 73, "Low-Intermediate": 51, "High-Intermediate": 43, "High": 26};
  const ripiSurvival = {"Very Good": 94, "Good": 79, "Poor": 55};
  const keys = ["age", "ldh_ratio", "ecog_ps", "stage", "extranodal_sites"];

  function calculateIPI(data) {
    const values = {};
    for (const key of keys) {
      const raw = data[key];
      if (raw === "" || raw === null || raw === undefined || typeof raw === "boolean") {
        throw new Error(key + " is required and must be numeric");
      }
      if (typeof raw === "string") {
        const clean = raw.trim();
        const format = key === "ldh_ratio" ? /^[+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][+-]?\\d+)?$/ : /^[+-]?\\d+$/;
        if (!format.test(clean)) throw new Error(key + " must have valid numeric format");
      }
      const val = Number(raw);
      if (!Number.isFinite(val)) throw new Error(key + " must be finite");
      values[key] = val;
    }
    const {age, ldh_ratio, ecog_ps, stage, extranodal_sites} = values;
    for (const key of ["age", "ecog_ps", "stage", "extranodal_sites"]) {
      if (!Number.isSafeInteger(values[key])) throw new Error(key + " must be an integer");
    }
    if (age < 0) throw new Error("Age must be non-negative");
    if (ldh_ratio < 0) throw new Error("LDH ratio must be non-negative");
    if (ecog_ps < 0 || ecog_ps > 4) throw new Error("ECOG PS must be 0-4");
    if (stage < 1 || stage > 4) throw new Error("Ann Arbor stage must be 1-4");
    if (extranodal_sites < 0) throw new Error("Extranodal sites must be non-negative");

    const factors = {
      age_over_60: {value: age, point: Number(age > 60)},
      ldh_elevated: {ratio: ldh_ratio, point: Number(ldh_ratio > 1)},
      ecog_ge_2: {value: ecog_ps, point: Number(ecog_ps >= 2)},
      stage_iii_iv: {value: stage, point: Number(stage >= 3)},
      extranodal_gt_1: {count: extranodal_sites, point: Number(extranodal_sites > 1)}
    };
    const score = Object.values(factors).reduce((total, factor) => total + factor.point, 0);
    const group = score <= 1 ? "Low" : score === 2 ? "Low-Intermediate" : score === 3 ? "High-Intermediate" : "High";
    const ripi = score === 0 ? "Very Good" : score <= 2 ? "Good" : "Poor";
    return {
      tool: "ipi-dlbcl-prognostic-index",
      ipi_score: score,
      ipi_risk_group: group,
      five_year_survival_pct: ipiSurvival[group],
      ripi_group: ripi,
      ripi_four_year_survival_pct: ripiSurvival[ripi],
      risk_factors: factors,
      classification: "IPI " + score + "/5 - " + group + " Risk",
      clinical_recommendation: "IPI " + score + "/5 (" + group + " risk). This is a prognostic grouping, not a treatment recommendation. Historical cohort survival estimates are not individualized predictions; treatment requires current disease and patient-specific assessment."
    };
  }

  // Supports RFC 4180 quoted cells, commas and line breaks; rejects unclosed quotes.
  function parseCSV(source) {
    const text = source.replace(/^\uFEFF/, "");
    const rows = [], row = [];
    let field = "", quote = false;
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      if (quote) {
        if (ch === '"' && text[i + 1] === '"') { field += '"'; i++; }
        else if (ch === '"') quote = false;
        else field += ch;
      } else if (ch === '"' && field === "") {
        quote = true;
      } else if (ch === ",") {
        row.push(field); field = "";
      } else if (ch === "\n" || ch === "\r") {
        if (ch === "\r" && text[i + 1] === "\n") i++;
        row.push(field); field = "";
        if (row.some(cell => cell.trim() !== "")) rows.push(row.slice());
        row.length = 0;
      } else {
        if (ch === '"') throw new Error("Unexpected quote in CSV");
        field += ch;
      }
    }
    if (quote) throw new Error("Unclosed quoted CSV field");
    row.push(field);
    if (row.some(cell => cell.trim() !== "")) rows.push(row);
    return rows;
  }

  const api = { calculateIPI, parseCSV };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.IPICalculator = api;

  if (typeof document === "undefined") return;

  const $ = id => document.getElementById(id);
  const form = $("ipi-form"), result = $("result"), error = $("form-error");
  const factors = [
    ["Age >60 years", "age_over_60"],
    ["LDH above laboratory ULN", "ldh_elevated"],
    ["ECOG performance status 2–4", "ecog_ge_2"],
    ["Ann Arbor stage III–IV", "stage_iii_iv"],
    [">1 extranodal disease site", "extranodal_gt_1"]
  ];
  function showResult(data) {
    $("score").textContent = data.ipi_score + " / 5";
    $("ipi-group").textContent = data.ipi_risk_group;
    $("ripi-group").textContent = data.ripi_group;
    $("ipi-os").textContent = data.five_year_survival_pct + "%";
    $("ripi-os").textContent = data.ripi_four_year_survival_pct + "%";
    const breakdown = $("breakdown");
    breakdown.replaceChildren();
    for (const [label, key] of factors) {
      const li = document.createElement("li");
      const mark = document.createElement("strong");
      mark.textContent = String(data.risk_factors[key].point);
      li.append(document.createTextNode(label), mark);
      breakdown.append(li);
    }
    result.hidden = false;
    $("placeholder").hidden = true;
  }
  form.addEventListener("submit", event => {
    event.preventDefault();
    error.textContent = "";
    try {
      const input = Object.fromEntries(keys.map(key => [key, $(key).value]));
      showResult(calculateIPI(input));
    } catch (err) {
      result.hidden = true;
      $("placeholder").hidden = false;
      error.textContent = err.message;
    }
  });
  $("reset").addEventListener("click", () => {
    form.reset();
    result.hidden = true;
    $("placeholder").hidden = false;
    error.textContent = "";
  });
  $("batch-file").addEventListener("change", async event => {
    const file = event.target.files[0];
    $("batch-status").textContent = "";
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      $("batch-status").textContent = "CSV exceeds 2 MB limit.";
      event.target.value = "";
      return;
    }
    try {
      const rows = parseCSV(await file.text());
      if (!rows.length) throw new Error("CSV is empty");
      const header = rows.shift().map(value => value.trim());
      if (new Set(header).size !== header.length || keys.some(key => !header.includes(key))) {
        throw new Error("CSV must contain unique columns: " + keys.join(", "));
      }
      if (rows.length > 10000) throw new Error("Maximum 10,000 data rows");
      const lines = ["row,ipi_score,ipi_risk_group,ripi_group,error"];
      let failed = 0;
      rows.forEach((cells, index) => {
        try {
          if (cells.length !== header.length) throw new Error("Column count mismatch");
          const input = Object.fromEntries(header.map((name, i) => [name, cells[i]]));
          const data = calculateIPI(input);
          lines.push([index + 2, data.ipi_score, data.ipi_risk_group, data.ripi_group, ""].join(","));
        } catch {
          failed++;
          lines.push([index + 2, "", "", "", "Invalid input"].join(","));
        }
      });
      const blob = new Blob([lines.join("\r\n") + "\r\n"], {type: "text/csv;charset=utf-8"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "ipi-results.csv";
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      $("batch-status").textContent = rows.length + " rows processed; " + failed + " invalid. Only row numbers and results are exported.";
    } catch (err) {
      $("batch-status").textContent = "CSV error: " + err.message;
    } finally {
      event.target.value = "";
    }
  });
})(typeof window !== "undefined" ? window : undefined);
