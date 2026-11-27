from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from services.analyzer import analyze_repo

router = APIRouter()


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
        # Avoid returning provider errors, clone output, or server details.
        raise HTTPException(
            status_code=502,
            detail="Repository analysis failed. Check server logs for details.",
        ) from None
