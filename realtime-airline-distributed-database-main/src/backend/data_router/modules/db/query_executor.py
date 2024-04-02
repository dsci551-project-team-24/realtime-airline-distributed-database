from kazoo.client import KazooClient
from src.backend.data_router.modules.host_management.host_manager import HostManager
from src.backend.data_router.modules.db.db_node_manager import DatabaseNodeManager
from src.backend.data_router.clients.mysql_client import MySqlClient
from src.backend.data_router.modules.hashing.consistent_hashing import ConsistentHashing


class QueryExecutor:
    def __init__(self, host_manager: HostManager, db_manager: DatabaseNodeManager):
        self.host_manager = host_manager
        self.db_manager = db_manager
        self.hasher = ConsistentHashing(self.host_manager.get_hosts())

    def execute_query(self, query: str):
        query_parts = query.strip().split()

        if query_parts[0].lower() == 'create':
            if query_parts[1].lower() == 'database':
                database_name = query_parts[2]
                self.create_database(database_name)
            elif query_parts[1].lower() == 'table':
                table_name = query_parts[2]
                self.create_table(table_name, query)
        else:
            print("Unsupported query type.")

    def create_database(self, database_name: str):
        host = self.hasher.get_server(database_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            query = f"CREATE DATABASE IF NOT EXISTS {database_name};"
            client.execute_ddl_query(query)
            print(f"Database '{database_name}' created successfully on host {host}.")
        else:
            print("No available hosts.")

    def create_table(self, table_name: str, query: str):
        host = self.hasher.get_server(table_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            client.execute_ddl_query(query)
            print(f"Table '{table_name}' created successfully on host {host}.")
        else:
            print("No available hosts.")

    def insert_data(self, table_name: str, query: str):
        host = self.hasher.get_server(table_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            client.execute_dml_query(query)
            print(f"Data inserted successfully into table '{table_name}' on host {host}.")
        else:
            print("No available hosts.")

    def select_data(self, table_name: str, query: str):
        host = self.hasher.get_server(table_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            data = client.execute_select_query(query)
            print(f"Data selected successfully from table '{table_name}' on host {host}.")
            return data
        else:
            print("No available hosts.")
            return []

    def delete_data(self, table_name: str, query: str):
        host = self.hasher.get_server(table_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            client.execute_dml_query(query)
            print(f"Data deleted successfully from table '{table_name}' on host {host}.")
        else:
            print("No available hosts.")

    def update_data(self, table_name: str, query: str):
        host = self.hasher.get_server(table_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            client.execute_dml_query(query)
            print(f"Data updated successfully in table '{table_name}' on host {host}.")
        else:
            print("No available hosts.")

    def drop_table(self, table_name: str):
        host = self.hasher.get_server(table_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            query = f"DROP TABLE {table_name};"
            client.execute_ddl_query(query)
            print(f"Table '{table_name}' dropped successfully on host {host}.")
        else:
            print("No available hosts.")

    def drop_database(self, database_name: str):
        host = self.hasher.get_server(database_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            query = f"DROP DATABASE {database_name};"
            client.execute_ddl_query(query)
            print(f"Database '{database_name}' dropped successfully on host {host}.")
        else:
            print("No available hosts.")
