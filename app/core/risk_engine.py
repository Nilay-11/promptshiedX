"""
Risk Scoring Engine (Chapter 6.9) — simplified version for the zero-shot path.

Full version (per config.yaml risk_scoring.weights) combines pattern_severity,
classifier_confidence, chunk_risk, reliability_score, and anomaly_score. Until
the RAG-side modules (chunk scanner, anomaly detector, reliability filter)
are built, this uses just the two signals that exist today: the pattern
scanner's severity and the semantic classifier's confidence.
"""

CATEGORY_BASE_SEVERITY = {
    "safe": 0,
    "prompt_injection": 70,
    "jailbreak": 80,
    "prompt_extraction": 75,
    "agent_manipulation": 65,
}


def compute_risk_score(pattern_severity: int, classification: dict) -> dict:
    """
    pattern_severity: 0-100, max severity hit from the regex/keyword scanner
                       (0 if no rule matched)
    classification: output of semantic_classifier.classify_prompt()

    Returns: {"risk_score": int, "category": str, "action": "PASS"|"REWRITE"|"BLOCK"}
    """
    category = classification["category"]
    confidence = classification["confidence"]

    base = CATEGORY_BASE_SEVERITY.get(category, 50)
    classifier_signal = base * confidence

    # Weighted average of the two available signals (pattern scanner, classifier).
    # Once chunk_risk / reliability_score / anomaly_score exist, replace this
    # with the full formula in config.yaml.
    risk_score = round(0.4 * pattern_severity + 0.6 * classifier_signal)
    risk_score = max(0, min(100, risk_score))

    if risk_score <= 30:
        action = "PASS"
    elif risk_score <= 65:
        action = "REWRITE"
    else:
        action = "BLOCK"

    return {"risk_score": risk_score, "category": category, "action": action}
