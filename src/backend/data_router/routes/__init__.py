from fastapi import APIRouter

from .database.mgmt import database_router
from .host_management.hosts import host_management_router

main_router = APIRouter()
main_router.include_router(host_management_router, prefix="/host_management")
main_router.include_router(database_router, prefix="/database")
