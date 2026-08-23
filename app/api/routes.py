"""
API routes for PromptShield X.

Pipeline: sanitizer (6.1) -> pattern scanner (6.2) -> semantic classifier
(6.3) -> risk engine (6.9) -> action engine (6.10).

/analyze-rag (Person B — minimal RAG path): runs the SAME per-item pipeline
(sanitizer -> pattern scanner -> semantic classifier -> risk engine) once per
retrieved chunk, instead of the prompt as a whole. No new detection model —
chunk_scanner / anomaly_detector / reliability_filter / evaluator_llm
(6.4-6.8) are explicitly out of scope for this pass; overall verdict is
currently just "riskiest chunk wins," which is a simplification standing in
for the reliability/consensus filter documented as future work.

NOTE: semantic_classifier is a zero-shot HF pipeline (~0.5-1.5s/call on CPU).
/analyze-rag latency scales linearly with chunk count as a result.
"""

from fastapi import APIRouter
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalyzeRagResponse,
    ChunkRiskResult,
)
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


@router.post("/analyze-rag", response_model=AnalyzeRagResponse)
def analyze_rag_context(payload: AnalyzeRequest):
    """
    Indirect (RAG) prompt injection check — minimal path.
    Reuses sanitizer + pattern_scanner + semantic_classifier + risk_engine
    per chunk. Full version (6.4-6.8: chunk scanner, anomaly detector,
    reliability filter, evaluator LLM) is documented as future work.
    """
    chunks = payload.retrieved_chunks or []

    chunk_results: list[ChunkRiskResult] = []
    for i, chunk in enumerate(chunks):
        clean_chunk = sanitize(chunk)

        pattern_result = scan_prompt(clean_chunk)
        classification = classify_prompt(clean_chunk)
        scored = compute_risk_score(pattern_result["severity"], classification)

        chunk_results.append(
            ChunkRiskResult(
                index=i,
                chunk_preview=(clean_chunk[:120] + "...") if len(clean_chunk) > 120 else clean_chunk,
                risk_score=scored["risk_score"],
                category=scored["category"],
                action=scored["action"],
                pattern_matches=[m["id"] for m in pattern_result["matches"]],
                classifier_confidence=classification["confidence"],
            )
        )

    if chunk_results:
        riskiest = max(chunk_results, key=lambda c: c.risk_score)
        overall_risk_score = riskiest.risk_score
        overall_action = riskiest.action
    else:
        overall_risk_score = 0
        overall_action = "PASS"

    return AnalyzeRagResponse(
        total_chunks=len(chunk_results),
        overall_risk_score=overall_risk_score,
        overall_action=overall_action,
        chunks=chunk_results,
    )


@router.get("/admin/logs")
def get_audit_logs(limit: int = 50):
    """Backs the audit dashboard (Chapter 6.12)."""
    return {"status": "not_implemented", "logs": []}