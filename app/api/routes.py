"""
API routes for PromptShield X.

Pipeline: sanitizer (6.1) -> pattern scanner (6.2) -> semantic classifier
(6.3) -> risk engine (6.9) -> action engine (6.10).
"""

from fastapi import APIRouter
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.modules.sanitizer import sanitize
from app.modules.pattern_scanner import scan_prompt
from app.modules.semantic_classifier import classify_prompt
from app.core.risk_engine import compute_risk_score
from app.core.action_engine import apply_action

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_prompt(payload: AnalyzeRequest):
    clean_prompt = sanitize(payload.prompt)

    pattern_result = scan_prompt(clean_prompt)
    classification = classify_prompt(clean_prompt)
    scored = compute_risk_score(pattern_result["severity"], classification)

    outcome = apply_action(scored["action"], clean_prompt, pattern_result["matches"])

    details = (
        f"pattern_matches={[m['id'] for m in pattern_result['matches']]}, "
        f"classifier_confidence={classification['confidence']}, "
        f"removed_fragments={outcome['removed_fragments']}"
    )

    return AnalyzeResponse(
        action=scored["action"],
        risk_score=scored["risk_score"],
        category=scored["category"],
        details=details,
        rewritten_prompt=outcome["prompt"] if scored["action"] == "REWRITE" else None,
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
    return {"status": "not_implemented", "logs": []}
