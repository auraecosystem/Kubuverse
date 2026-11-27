import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from services.analyzer import analyze_repo

router = APIRouter()
logger = logging.getLogger(__name__)


class RepoInput(BaseModel):
    url: HttpUrl


@router.post("/analyze")
async def analyze(input: RepoInput):
    try:
        result = await analyze_repo(str(input.url))
        return {"output": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Repository analysis failed")
        raise HTTPException(
            status_code=502,
            detail="Repository analysis failed. Check server logs for details.",
        ) from None
