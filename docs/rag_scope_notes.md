# RAG Path — Scope Notes (Person B)

## What's implemented

`/analyze-rag` accepts `retrieved_chunks` (already present on `AnalyzeRequest`)
and runs the same per-item pipeline `/analyze` uses — `sanitize()` →
`pattern_scanner.scan_prompt()` → `semantic_classifier.classify_prompt()` →
`risk_engine.compute_risk_score()` — once per chunk, instead of building new
detection logic. Returns a per-chunk `risk_score`/`category`/`action`, plus an
`overall_action`/`overall_risk_score` for the whole request.

## Explicitly deferred (future work)

- **Chunk scanner as a distinct module (6.4)** — currently each chunk just
  reuses the same prompt-level scanner/classifier; no chunk-specific
  detection logic (e.g. cross-chunk context) exists yet.
- **Embedding-based anomaly detection (6.5)** — Isolation Forest / cosine
  similarity outlier detection is not implemented. No anomaly score
  contributes to chunk risk today.
- **Reliability filter (6.6)** — no contradiction detection or
  majority-consensus selection across chunks. The "overall" verdict is
  currently a placeholder: **the riskiest single chunk's action wins.**
  This does not model source trust or agreement between chunks at all.
- **Evaluator LLM (6.7)** — no secondary verification model reviews chunks
  or the final response.
- **Isolated context engine (6.8)** — chunks are not yet routed through a
  separate evidence channel; this only scores them, it doesn't change how
  they reach the LLM.

## Known tradeoff: latency

`semantic_classifier.classify_prompt()` is a zero-shot HF pipeline
(~0.5–1.5s per call on CPU). `/analyze-rag` calls it once per chunk, so
latency scales linearly with chunk count — roughly 5–15s for a 10-chunk
request. This is a direct consequence of reusing the existing classifier
as-is rather than building a chunk-batching or lighter-weight path.

## Suggested next steps (not in this pass)

- Batch classifier calls instead of one-per-chunk, if latency becomes a
  blocker for a live demo.
- Replace "riskiest chunk wins" with an actual reliability/consensus rule
  once the reliability filter exists.