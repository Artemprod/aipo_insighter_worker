from fastapi import HTTPException
from fastapi import APIRouter
from starlette.requests import Request
assistant_router = APIRouter()


@assistant_router.get("/api/assistants/get_all")
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
async def get_one_assistant(request: Request,
                            assistant_id: int):
    try:
        assistants = await request.app.repositories.assistant_repository.get(assistant_id=assistant_id)
        if assistants is not None:
            return assistants
        else:
            raise HTTPException(status_code=404, detail="assistant not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
