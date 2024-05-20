from fastapi import HTTPException
from fastapi import APIRouter
from starlette.requests import Request

from fastapi_cache.decorator import cache

assistant_router = APIRouter(
    prefix="/assistants",
    tags=["Assistants"],
)


@assistant_router.get("/get_all")
@cache(expire=60)
async def get_all_assistants(request: Request):
    try:
        assistants = await request.app.repositories.assistant_repository.get_all()
        if assistants is not None:
            return assistants
        else:
            raise HTTPException(status_code=404, detail="assistants not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@assistant_router.get("/api/assistants/get_one")
@cache(expire=60)
async def get_one_assistant(request: Request,
                            assistant_id: int):
    try:
        assistants = await request.app.repositories.assistant_repository.get(assistant_id=assistant_id)
        if assistants is not None:
            return assistants
        else:
            raise HTTPException(status_code=404,
                                detail={

                                    'details': f"No assistant with this id: {assistant_id}, in database"}
                                )
    except Exception as e:
        raise HTTPException(status_code=500, detail={

            'details': f"An error occurred: {str(e)}"}

                            )
