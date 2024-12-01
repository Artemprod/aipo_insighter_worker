from typing import Optional

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.routers.history import schemas
from src.api.schemas import ServiceSources
from src.consumption.models.consumption.history import HistoryResultDTO

history_router = APIRouter(
    prefix='/history',
    tags=["History"]
)


@history_router.get(
    "/get_history", response_model=schemas.GetHistoryResponseList,
    status_code=status.HTTP_200_OK
)
async def get_user_history(
        user_id: int,
        source: ServiceSources,
        request: Request,
        unique_id: Optional[str] = None
):
    """Получить всю историю запросов у пользователя, если указать параметр unique_id то вернет определенную историю"""
    logger.info("user_id", user_id)
    try:
        history: list[HistoryResultDTO] = await request.app.repositories.history_repository.get_history_by_user_id(
            user_id=user_id,
            source=source.value,
            unique_id=unique_id
        )
        if history is not None:
            result = [i.to_dict() for i in history]
            return JSONResponse(content={"result": result})
        else:
            raise HTTPException(status_code=404, detail="History not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@history_router.get(
    "/get_history_by_date", response_model=schemas.GetHistoryResponseList,
    status_code=status.HTTP_200_OK
)
async def get_user_history_by_date(user_id: int, source: ServiceSources, date, request: Request):
    """Получение истории пользователя за определённую дату"""
    logger.info("user_id", user_id)
    try:
        history: list[HistoryResultDTO] = await request.app.repositories.history_repository.get_history_by_date(
            user_id=user_id, source=source.value, date=date
        )
        logger.info(f"Проверка истории в API {history}")
        if history is not None:
            result = [i.to_dict() for i in history]
            return JSONResponse(content={"result": result})
        else:
            raise HTTPException(status_code=404, detail=f"History with this date: {date} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@history_router.get(
    "/check_history", response_model=schemas.HistoryCheckDTO,
    status_code=status.HTTP_200_OK
)
async def get_user_history_by_date(user_id: int, source: ServiceSources, request: Request):
    """Проверка истории у пользователя"""
    logger.info("user_id", user_id)
    try:
        is_history = await request.app.repositories.history_repository.check_history(
            user_id=user_id,
            source=source.value
        )
        logger.info(f"Проверка ответа истории в API {is_history}")
        return {"is_history": is_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
