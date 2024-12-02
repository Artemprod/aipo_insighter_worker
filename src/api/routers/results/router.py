from fastapi import HTTPException
from fastapi import APIRouter
from loguru import logger
from starlette.requests import Request

from src.api.routers.exceptions import NotFoundError, ErrorMessage
from src.consumption.models.consumption.summarization import SummaryText
from src.consumption.models.consumption.transcribition import TranscribedText
from src.database.repositories.base_repository import BaseRepository


results_router = APIRouter(
    prefix='/results',
    tags=["Results"]
)


async def get_text_from_repository(
        repository: BaseRepository,
        text_id: int,
        text_type: str
):
    logger.info(f"Getting {text_type} with id {text_id}")
    try:
        return await repository.get(text_id=text_id)
    except NotFoundError:
        raise
    except Exception as e:
        logger.exception(f"An error occurred when getting {text_type} with id {text_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@results_router.get(
    "/get_transcribed_text",
    responses={
        404: {"model": ErrorMessage},
        500: {"model": ErrorMessage}
    }
)
async def get_transcribed_text_from_database(
        id_text: int,
        request: Request
) -> TranscribedText:
    return await get_text_from_repository(
        repository=request.app.repositories.transcribed_text_repository,
        text_id=id_text,
        text_type="transcribed text"
    )


@results_router.get(
    "/get_summary_text",
    responses={
        404: {"model": ErrorMessage},
        500: {"model": ErrorMessage}
    }
)
async def get_summary_text_from_database(
        id_text: int,
        request: Request
) -> SummaryText:
    return await get_text_from_repository(
        repository=request.app.repositories.summary_text_repository,
        text_id=id_text,
        text_type="summary text"
    )
