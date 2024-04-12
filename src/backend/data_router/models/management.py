from pydantic import BaseModel


class CreateTableRequest(BaseModel):
    createTableQuery: str
    partitionKey: str
    tableName: str


class SelectDataRequest(BaseModel):
    selectQuery: str
    tableName: str


class QueryDataRequest(BaseModel):
    query: str
    tableName: str
    partitionKey: str
