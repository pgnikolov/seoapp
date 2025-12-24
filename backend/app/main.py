from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import io
import pandas as pd

from .models.session import init_db, get_db
from .models.database import Job, Keyword
from .schemas.jobs import AnalyzeRequest, JobStatusResponse, KeywordSchema
from .services.jobs import start_analysis_job

app = FastAPI(title="SEO Keyword Extractor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    job_id = await start_analysis_job(db, request)
    return {"job_id": job_id}

@app.get("/results/{job_id}", response_model=JobStatusResponse)
async def get_results(job_id: str, db: AsyncSession = Depends(get_db)):
    # Вземаме работата (job)
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Вземаме ключовите думи ако е завършено
    keywords = []
    if job.status == "completed":
        result = await db.execute(select(Keyword).where(Keyword.job_id == job_id).order_by(Keyword.score.desc()))
        keywords = result.scalars().all()
    
    return JobStatusResponse(
        id=job.id,
        url=job.url,
        status=job.status,
        created_at=job.created_at,
        error=job.error,
        keywords=[KeywordSchema.model_validate(k, from_attributes=True) for k in keywords]
    )

@app.get("/results/{job_id}/export.csv")
async def export_csv(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Keyword).where(Keyword.job_id == job_id).order_by(Keyword.score.desc()))
    keywords = result.scalars().all()
    
    if not keywords:
        raise HTTPException(status_code=404, detail="No keywords found for this job")
    
    df = pd.DataFrame([{
        "Keyword": k.phrase,
        "Score": k.score,
        "Occurrences": k.occurrences,
        "Pages Count": k.pages_count,
        "Top Page": k.top_page,
        "Intent": k.intent,
        "Language": k.language
    } for k in keywords])
    
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = f"attachment; filename=keywords_{job_id}.csv"
    return response
