from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime

class AnalyzeRequest(BaseModel):
    url: str
    max_pages: Optional[int] = 30
    max_depth: Optional[int] = 2
    mode: Optional[str] = "domain" # "single" or "domain"
    include_subdomains: Optional[bool] = False
    language: Optional[str] = None # auto-detect if None

class KeywordSchema(BaseModel):
    phrase: str
    score: float
    occurrences: int
    pages_count: int
    top_page: str
    source_mix: Dict[str, int]
    intent: str
    language: str

class JobStatusResponse(BaseModel):
    id: str
    url: str
    status: str
    created_at: datetime
    error: Optional[str] = None
    keywords: Optional[List[KeywordSchema]] = None
