import uuid
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.database import Job, Keyword
from ..schemas.jobs import AnalyzeRequest
from .crawler import Crawler
from .analyzer import KeywordAnalyzer

logger = logging.getLogger(__name__)

async def start_analysis_job(db: AsyncSession, request: AnalyzeRequest):
    job_id = str(uuid.uuid4())
    
    new_job = Job(
        id=job_id,
        url=request.url,
        status="pending",
        options=request.model_dump()
    )
    db.add(new_job)
    await db.commit()
    
    # Стартираме фонова задача
    asyncio.create_task(run_analysis_task(job_id, request, db.bind))
    
    return job_id

async def run_analysis_task(job_id: str, request: AnalyzeRequest, engine):
    from ..models.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Обновяваме статус: crawling
            job = await db.get(Job, job_id)
            job.status = "crawling"
            await db.commit()
            
            # 2. Crawler
            crawler = Crawler(
                start_url=request.url,
                max_pages=request.max_pages,
                max_depth=request.max_depth,
                mode=request.mode,
                include_subdomains=request.include_subdomains
            )
            pages = await crawler.run()
            
            if not pages:
                job.status = "failed"
                job.error = "No pages found or blocked by robots.txt"
                await db.commit()
                return

            # 3. Analyzer
            job.status = "analyzing"
            await db.commit()
            
            analyzer = KeywordAnalyzer(pages, target_lang=request.language)
            keywords_data = analyzer.analyze()
            
            # 4. Save keywords
            for kw in keywords_data:
                keyword_obj = Keyword(
                    job_id=job_id,
                    phrase=kw['phrase'],
                    score=kw['score'],
                    occurrences=kw['occurrences'],
                    pages_count=kw['pages_count'],
                    top_page=kw['top_page'],
                    source_mix=kw['source_mix'],
                    intent=kw['intent'],
                    language=kw['language']
                )
                db.add(keyword_obj)
            
            job.status = "completed"
            await db.commit()
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            job = await db.get(Job, job_id)
            if job:
                job.status = "failed"
                job.error = str(e)
                await db.commit()
