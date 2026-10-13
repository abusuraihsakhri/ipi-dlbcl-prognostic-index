"""
FastAPI REST API Server for Ipi Dlbcl Prognostic Index.
"""
from pathlib import Path
import os
import hmac
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from ipi_dlbcl import calculate_ipi
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Ipi Dlbcl Prognostic Index API",
    description="Enterprise Distributed Component Platform (Clinical & Biomedical AI)",
    version="3.0.0-ENTERPRISE",
)


def require_supervisor_token(x_api_token: str | None = Header(default=None)):
    """Fail closed unless a server-side authorization token is configured."""
    expected = os.environ.get("SUPERVISOR_API_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="Supervisor API is disabled")
    if not x_api_token or not hmac.compare_digest(x_api_token, expected):
        raise HTTPException(status_code=401, detail="Invalid supervisor token")


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "ipi-dlbcl-prognostic-index", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload, _auth: None = Depends(require_supervisor_token)):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest, _auth: None = Depends(require_supervisor_token)):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs(_auth: None = Depends(require_supervisor_token)):
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


class IPIPatient(BaseModel):
    age: int
    ldh_ratio: float
    ecog_ps: int
    stage: int
    extranodal_sites: int


@app.post("/api/ipi")
def api_ipi(payload: IPIPatient):
    try:
        return calculate_ipi(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# Serve the same dependency-free calculator as GitHub Pages.
app.mount("/", StaticFiles(directory=str(Path(__file__).resolve().parent.parent / "web"), html=True), name="calculator")
