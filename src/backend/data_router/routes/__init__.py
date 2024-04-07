from fastapi import APIRouter

from .host_management.hosts import host_management_router

main_router = APIRouter()
main_router.include_router(host_management_router, prefix="/host_management")

flight_router = APIRouter()
flight_router.include_router(flight_router, prefix="/flights")
