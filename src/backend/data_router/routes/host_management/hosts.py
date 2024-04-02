from fastapi import APIRouter

from data_router.core.dependencies import Modules

host_management_router = APIRouter()


# get the number of hosts using the host manager
@host_management_router.get("/hosts", tags=["host_management"])
async def get_hosts():
    return {"hosts": Modules.host_manager.get_hosts()}
