from loguru import logger
from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from src.api.routers.exceptions import NotFoundError, ErrorMessage
from src.api.routers.history.schemas import UserHistoryScheme
from src.consumption.models.consumption.history import HistoryResultDTO


history_router = APIRouter(
    prefix='/history',
    tags=["History"]
)


@history_router.get(
    "/get_history",
    responses={
        404: {"model": ErrorMessage},
        500: {"model": ErrorMessage}
    }
)
async def get_user_history(
        user_id: int,
        request: Request
) -> list[HistoryResultDTO]:
    try:
        return await request.app.repositories.history_repository.get_history_by_user_id(user_id=user_id)
    except NotFoundError:
        raise
    except Exception as e:
        logger.exception(f"An error occurred when getting history with user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@history_router.get(
    "/get_history_by_date",
    responses={
        404: {"model": ErrorMessage},
        500: {"model": ErrorMessage}
    }
)
async def get_user_history_by_date(
        user_id: int,
        date: str,
        request: Request
) -> list[HistoryResultDTO]:
    try:
        return await request.app.repositories.history_repository.get_history_by_date(user_id=user_id, date=date)
    except NotFoundError:
        raise
    except Exception as e:
        logger.exception(f"An error occurred when getting history by date {date} with user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@history_router.get(
    "/check_history",
    responses={
        500: {"model": ErrorMessage}
    }
)
async def check_user_history(
        user_id: int,
        request: Request
) -> UserHistoryScheme:
    try:
        return UserHistoryScheme(
            is_history=await request.app.repositories.history_repository.check_history(user_id=user_id)
        )
    except Exception as e:
        logger.exception(f"An error occurred when check user history with user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
