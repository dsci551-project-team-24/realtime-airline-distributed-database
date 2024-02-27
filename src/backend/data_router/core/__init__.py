from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from .dependencies import init_clients, init_modules, shutdown_clients, setup_watchers, destroy_modules
from ..routes import main_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_clients()
    init_modules()
    logger.info("App started.")
    yield
    logger.info("App shutting down.")
    destroy_modules()
    shutdown_clients()


def create_app():
    app = FastAPI(
        title="Data Router",
        description="A simple data router",
        version="0.1",
        lifespan=lifespan
    )
    app.include_router(main_router)
    return app
