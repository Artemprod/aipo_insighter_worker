from dataclasses import asdict

from fastapi import HTTPException
from fastapi import APIRouter
from starlette.requests import Request
from src.consumption.models.buisnes_models import TranscribedText, SummaryText

database_router = APIRouter()


@database_router.get("/api/results/get_transcribed_text")
async def get_transcribed_text_from_database(id_text: int,
                                             request: Request):
    try:
        text: TranscribedText = await request.app.repositories.transcribed_text_repository.get(text_id=id_text)
        if text is not None:
            return {"data": asdict(text)}
        else:
            raise HTTPException(status_code=404, detail="Text not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@database_router.get("/api/results/get_summary_text")
async def get_summary_text_from_database(id_text: int,
                                         request: Request):
    try:
        text: SummaryText = await request.app.repositories.summary_text_repository.get(text_id=id_text)
        if text is not None:
            return {"text": text.summary_text}
        else:
            raise HTTPException(status_code=404, detail="Text not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
