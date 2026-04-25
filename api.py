import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="AI Research Assistant")
BASE_DIR = Path(__file__).resolve().parent

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    topic: str


@app.get("/")
def serve_ui():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/research")
async def research(query: Query):
    topic = query.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Please enter a research topic.")

    try:
        from pipeline import run_research_pipeline

        result = await run_in_threadpool(run_research_pipeline, topic)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Research pipeline failed: {exc}",
        ) from exc

    return {
        "report": result.get("report", ""),
        "feedback": result.get("feedback", ""),
        "sources": result.get("sources", []),
    }
