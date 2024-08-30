from fastapi import HTTPException, APIRouter, Request

dev_router = APIRouter(
    prefix="/development",
    tags=["Endpoints for development"],
)


@dev_router.get("/assistant/get_all")
async def get_all_assistants(request: Request):
    try:
        # Фиктивные данные
        assistants = [
            {"id": 1, "name": "Assistant One", "role": "Helper"},
            {"id": 2, "name": "Assistant Two", "role": "Guide"}
        ]
        return assistants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@dev_router.get("/assistant/get_one")
async def get_one_assistant(request: Request):
    try:
        # Фиктивные данные
        assistant = {"id": 1, "name": "Assistant One", "role": "Helper"}
        return assistant
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@dev_router.get("/result/get_transcribed_text")
async def get_transcribed_text(request: Request):
    try:
        # Фиктивные данные
        transcribed_text = {"id": 1, "text": "This is a transcribed text."}

        return transcribed_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@dev_router.get("/result/get_summary_text")
async def get_summary_text(request: Request):
    try:
        # Фиктивные данные
        summary_text = {"id": 1, "summary": "This is a summary of the text."}
        return summary_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@dev_router.post("/start/youtube")
async def start_youtube(request: Request):
    try:
        # Фиктивные данные
        response = {"status": "YouTube processing started", "id": 1}

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@dev_router.post("/start/storage")
async def start_storage(request: Request):
    division_by_zero = 1 / 0
    try:
        # Фиктивные данные
        response = {"status": "Storage processing started", "id": 2}

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
