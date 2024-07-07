from typing import Optional

import sentry_sdk
from fastapi import FastAPI

from container import settings
from src.api.app.initialize.lifspan import lifespan
from src.api.routers.assistant.router import assistant_router
from src.api.routers.dev_routers.router import dev_router
from src.api.routers.main_process.router import processes_router
from src.api.routers.results.router import results_router

from src.database.repositories.storage_container import Repositories

sentry_sdk.init(
    dsn=settings.sentry.sentry_dns_fast_api,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    enable_tracing=True,
    debug=True
)


def create_server(repositories: Optional[Repositories] = None):
    server = FastAPI(lifespan=lifespan,
                     title="INSIGHTER APPLICATION",
                     )
    server.include_router(processes_router)
    server.include_router(assistant_router)
    server.include_router(results_router)
    server.include_router(dev_router)
    server.repositories = repositories

    return server
