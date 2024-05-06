
import uvicorn

if __name__ == "__main__":
    uvicorn.run("infrastructure.web.api_app:app",  host="127.0.0.1", port=9192, lifespan="on")