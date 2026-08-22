"""
Route stubs. Start with /analyze — it's the core of the firewall.

Suggested implementation order:
1. Wire /analyze to sanitizer -> pattern_scanner -> semantic_classifier only.
2. Add risk_engine + action_engine to turn signals into PASS/REWRITE/BLOCK.
3. Add /analyze-rag once chunk_scanner + reliability_filter + evaluator_llm exist.
4. Add /admin/logs to back the dashboard.
"""

from fastapi import APIRouter
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.modules.pattern_scanner import scan_prompt
from app.modules.semantic_classifier import classify_prompt
from app.core.risk_engine import compute_risk_score

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_prompt(payload: AnalyzeRequest):
    """
    Direct prompt injection check (Chapters 6.2, 6.3, 6.9, 6.10).
    Sanitizer (6.1) and full RAG-side modules still TODO — see README build order.
    """
    pattern_result = scan_prompt(payload.prompt)
    classification = classify_prompt(payload.prompt)
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
    return {"status": "not_implemented", "logs": []}
