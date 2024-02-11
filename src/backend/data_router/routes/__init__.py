from fastapi import APIRouter

from .hello_world import hello_world_router

main_router = APIRouter()
main_router.include_router(hello_world_router)
