from fastapi import FastAPI

from ..routes import main_router


def create_app():
    app = FastAPI(
        title="Data Router",
        description="A simple data router",
        version="0.1",
    )
    app.include_router(main_router)
    return app
