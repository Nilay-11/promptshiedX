from typing import Literal, Optional
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None
    retrieved_chunks: Optional[list[str]] = None  # populated for /analyze-rag


class AnalyzeResponse(BaseModel):
    action: Literal["PASS", "REWRITE", "BLOCK"]
    risk_score: int  # 0-100, see config.yaml risk_scoring.thresholds
    category: Literal[
        "safe",
        "prompt_injection",
        "jailbreak",
        "prompt_extraction",
        "agent_manipulation",
    ]
    details: str
    rewritten_prompt: Optional[str] = None
