from fastapi import APIRouter

from data_router.core.dependencies import Modules
from data_router.clients.mysql_client import MySqlClient

flights_router = APIRouter()
client = MySqlClient()

@flights_router.get("/flights", tags=["flights"])
async def get_flights():
    query = "SELECT * FROM flights"
    return client.execute_query(query)

@flights_router.get("/flights/{flight_id}", tags=["flights"])
async def get_flight(flight_id: int):
    query = f"SELECT * FROM flights WHERE flight_id = {flight_id}"
    return client.execute_query(query)


