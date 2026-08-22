# PromptShield X — Architecture

## Pipeline (Chapter 5)

```
User Query
   |
   v
Pre-Retrieval Sanitization      (app/modules/sanitizer.py)
   |
   v
Chunk Scanner                    (app/modules/chunk_scanner.py)
   |
   v
Embedding Anomaly Detection      (app/modules/anomaly_detector.py)
   |
   v
Reliability Filter               (app/modules/reliability_filter.py)
   |
   v
Evaluator LLM                    (app/modules/evaluator_llm.py)
   |
   v
Risk Scoring Engine               (app/core/risk_engine.py)
   |
   v
Action Engine (PASS/REWRITE/BLOCK) (app/core/action_engine.py)
   |
   v
Target LLM
   |
   v
Response (re-verified by Evaluator LLM)
   |
   v
Audit Dashboard / Logger          (app/core/init_db.py, dashboard/)
```

Direct prompt path (no RAG) skips the RAG-specific stages (chunk scanner,
anomaly detection, reliability filter) and goes: sanitizer -> pattern
scanner -> semantic classifier -> risk engine -> action engine.

## Module -> file map

| Module (thesis section) | File |
|---|---|
| 6.1 Pre-Retrieval Sanitization | `app/modules/sanitizer.py` |
| 6.2 User Prompt Scanner | `app/modules/pattern_scanner.py` |
| 6.3 Semantic Classification Engine | `app/modules/semantic_classifier.py` |
| 6.4 Chunk Scanner | `app/modules/chunk_scanner.py` |
| 6.5 Embedding-Based Anomaly Detection | `app/modules/anomaly_detector.py` |
| 6.6 Reliability Filter | `app/modules/reliability_filter.py` |
| 6.7 Evaluator LLM | `app/modules/evaluator_llm.py` |
| 6.8 Isolated Context Engine | `app/modules/isolated_context.py` |
| 6.9 Risk Scoring Engine | `app/core/risk_engine.py` |
| 6.10 Action Engine | `app/core/action_engine.py` |
| 6.11 Adaptive Learning Module | `app/modules/adaptive_learning.py` |
| 6.12 Audit Logger | `app/core/init_db.py` + logging calls in `app/core/` |

## Risk scoring formula (starting point, tune against Ch. 10 datasets)

```
risk = 0.20 * pattern_severity
     + 0.25 * classifier_confidence
     + 0.20 * chunk_risk
     + 0.15 * reliability_score
     + 0.20 * anomaly_score

0-30   -> PASS
31-65  -> REWRITE
66-100 -> BLOCK
```

Weights live in `config.yaml` under `risk_scoring.weights` — treat the
starting numbers as a hypothesis to validate/tune during evaluation, not a
fixed answer.
