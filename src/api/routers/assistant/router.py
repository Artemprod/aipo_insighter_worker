from fastapi import HTTPException
from fastapi import APIRouter
from loguru import logger
from starlette.requests import Request

from fastapi_cache.decorator import cache

from src.api.routers.exceptions import NotFoundError, ErrorMessage
from src.consumption.models.consumption.asssistant import AIAssistantScheme

assistant_router = APIRouter(
    prefix="/assistants",
    tags=["Assistants"],
)


@assistant_router.get(
    "/get_all",
    responses={
        404: {"model": ErrorMessage},
        500: {"model": ErrorMessage}
    }
)
@cache(expire=60)
async def get_all_assistants(request: Request) -> list[AIAssistantScheme]:
    try:
        return await request.app.repositories.assistant_repository.get_all()
    except NotFoundError:
        raise
    except Exception as e:
        logger.exception(f"An error occurred when getting assistants: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@assistant_router.get(
    "/get_one",
    responses={
        404: {"model": ErrorMessage},
        500: {"model": ErrorMessage}
    }
)
@cache(expire=60)
async def get_one_assistant(
        request: Request,
        assistant_id: int
) -> AIAssistantScheme:
    try:
        return await request.app.repositories.assistant_repository.get(assistant_id=assistant_id)
    except NotFoundError:
        raise
    except Exception as e:
        logger.exception(f"An error occurred when getting assistant with id {assistant_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
