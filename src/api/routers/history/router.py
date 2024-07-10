from loguru import logger
from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from src.consumption.models.consumption.history import HistoryResultDTO
from fastapi_cache.decorator import cache

history_router = APIRouter(
    prefix='/history',
    tags=["History"]
)


@history_router.get("/get_history")
@cache(expire=60 * 10)
async def get_user_history(user_id: int, request: Request):
    logger.info("user_id", user_id)
    try:
        history: list[HistoryResultDTO] = await request.app.repositories.history_repository.get_history_by_user_id(
            user_id=user_id)
        if history is not None:
            result = [i.to_dict() for i in history]
            return result
        else:
            raise HTTPException(status_code=404, detail="History not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@history_router.get("/get_history_by_date")
@cache(expire=60 * 10)
async def get_user_history_by_date(user_id: int, date, request: Request):
    logger.info("user_id", user_id)
    try:
        history: list[HistoryResultDTO] = await request.app.repositories.history_repository.get_history_by_date(
            user_id=user_id, date=date)
        logger.info(f"Проверка истории в API {history}")
        if history is not None:
            result = [i.to_dict() for i in history]
            return result
        else:
            raise HTTPException(status_code=404, detail=f"History with this date: {date} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@history_router.get("/check_history")
@cache(expire=60 * 10)
async def get_user_history_by_date(user_id: int, request: Request):
    logger.info("user_id", user_id)
    try:
        is_history = await request.app.repositories.history_repository.check_history(user_id=user_id)
        logger.info(f"Проверка ответа истории в API {is_history}")
        return {"is_history": is_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
