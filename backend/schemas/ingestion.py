from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Concept(BaseModel):
    name: str
    description: str
    confidence: float
    source: Optional[str] = None

class IngestionStatus(BaseModel):
    job_id: str
    status: str
    current_step: Optional[str] = None
    progress: float
    error: Optional[str] = None

class ReviewPayload(BaseModel):
    concepts: List[Concept]
    # Future: methods, assumptions, etc.

class ApprovalRequest(BaseModel):
    approved_concepts: List[Concept]
