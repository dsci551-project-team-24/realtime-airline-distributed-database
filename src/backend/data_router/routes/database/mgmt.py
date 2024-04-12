from fastapi import APIRouter

from data_router.core.dependencies import Modules
from data_router.models.management import CreateTableRequest, SelectDataRequest, QueryDataRequest

database_router = APIRouter()


# get the number of hosts using the host manager
@database_router.post("/tables", tags=["database_router"])
async def create_table(create_table_request: CreateTableRequest):
    query_executor = Modules.query_executor
    query_executor.create_table(
        create_table_request.tableName,
        create_table_request.createTableQuery,
        create_table_request.partitionKey
    )


@database_router.post("/scan", tags=["database_router"])
async def create_table(select_data_request: SelectDataRequest):
    query_executor = Modules.query_executor
    return query_executor.select_data(select_data_request.tableName, select_data_request.selectQuery)


@database_router.post("/query", tags=["database_router"])
async def create_table(query_data_request: QueryDataRequest):
    query_executor = Modules.query_executor
    return query_executor.query_data(table_name=query_data_request.tableName, query=query_data_request.query,
                                     partition_key_value=query_data_request.partitionKey)
