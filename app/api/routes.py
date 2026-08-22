"""
API routes for PromptShield X.

PLACE THIS FILE AT: app/api/routes.py (replaces the existing one)

Updated to call sanitizer.sanitize() first in /analyze, before the pattern
scanner and semantic classifier run.
"""

from fastapi import APIRouter
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.modules.sanitizer import sanitize
from app.modules.pattern_scanner import scan_prompt
from app.modules.semantic_classifier import classify_prompt
from app.core.risk_engine import compute_risk_score

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_prompt(payload: AnalyzeRequest):
    """
    Direct prompt injection check.
    Pipeline: sanitizer (6.1) -> pattern scanner (6.2) -> semantic
    classifier (6.3) -> risk engine (6.9) -> action (6.10).
    """
    clean_prompt = sanitize(payload.prompt)

    pattern_result = scan_prompt(clean_prompt)
    classification = classify_prompt(clean_prompt)
    scored = compute_risk_score(pattern_result["severity"], classification)

    details = (
        f"pattern_matches={[m['id'] for m in pattern_result['matches']]}, "
        f"classifier_confidence={classification['confidence']}"
    )

    return AnalyzeResponse(
        action=scored["action"],
        risk_score=scored["risk_score"],
        category=scored["category"],
        details=details,
    )


@router.post("/analyze-rag")
def analyze_rag_context(payload: AnalyzeRequest):
    """
    Indirect (RAG) prompt injection check (Chapters 6.4-6.8).
    TODO: call chunk_scanner -> anomaly_detector -> reliability_filter -> evaluator_llm
    """
    return {"status": "not_implemented"}


@router.get("/admin/logs")
def get_audit_logs(limit: int = 50):
    """Backs the audit dashboard (Chapter 6.12)."""
    return {"status": "not_implemented", "logs": []}git add app/modules/sanitizer.py app/api/routes.py
git commit -m "Add sanitizer module (Ch 6.1), wire into /analyze"
git push origin feature/sanitizer-action-engine