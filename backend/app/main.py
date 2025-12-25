from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any
from app.services.analyzer import WebsiteAnalyzer
import os

app = FastAPI(title="Website Intelligence / SEO Snapshot API")


class AnalyzeRequest(BaseModel):
    url: HttpUrl


@app.post("/analyze")
async def analyze_website(request: AnalyzeRequest) -> Dict[str, Any]:
    """
    Анализира URL и връща snapshot с данни за домейна, технологии, SEO и WHOIS.
    """
    try:
        analyzer = WebsiteAnalyzer()
        result = await analyzer.analyze(str(request.url))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Грешка при анализ: {str(e)}")


# Serve static files (must be after route definitions)
static_dir = os.path.join(os.path.dirname(__file__), '..', 'public')
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

