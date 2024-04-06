from typing import List

from kazoo.client import KazooClient
from src.backend.data_router.modules.host_management.host_manager import HostManager
from src.backend.data_router.modules.db.db_node_manager import DatabaseNodeManager
from src.backend.data_router.clients.mysql_client import MySqlClient
from src.backend.data_router.modules.hashing.consistent_hashing import ConsistentHashing


class QueryExecutor:
    def __init__(self, zk_hosts: str, db_manager: DatabaseNodeManager):
        self.host_manager = HostManager(KazooClient(hosts=zk_hosts))
        self.db_manager = db_manager
        self.hasher = ConsistentHashing(self.host_manager.get_hosts())
        self.zk = self.host_manager.get_client()

    def execute_query(self, query: str):
        query_parts = query.strip().split()

        if query_parts[0].lower() == 'create':
            if query_parts[1].lower() == 'database':
                database_name = query_parts[2]
                self.create_database(database_name)
            elif query_parts[1].lower() == 'table':
                table_name = query_parts[2]
                self.create_table(table_name, query)
        elif query_parts[0].lower() == 'insert':
            table_name = query_parts[2]
            self.insert_data(table_name, query)
        elif query_parts[0].lower() == 'select':
            table_name = query_parts[3]
            self.select_data(table_name, query)
        elif query_parts[0].lower() == 'delete':
            table_name = query_parts[2]
            self.delete_data(table_name, query)
        elif query_parts[0].lower() == 'update':
            table_name = query_parts[1]
            self.update_data(table_name, query)
        elif query_parts[0].lower() == 'drop':
            if query_parts[1].lower() == 'table':
                table_name = query_parts[2]
                self.drop_table(table_name)
            elif query_parts[1].lower() == 'database':
                database_name = query_parts[2]
                self.drop_database(database_name)
        else:
            print("Unsupported query type.")

    def create_database(self, database_name: str):
        host = self.hasher.get_server(database_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            query = f"CREATE DATABASE IF NOT EXISTS {database_name};"
            client.execute_ddl_query(query)
            print(f"Database '{database_name}' created successfully on host {host}.")
            # Create znode for the partition
            self.zk.ensure_path(f"/tables/{database_name}")
        else:
            print("No available hosts.")

    def create_table(self, table_name: str, query: str):
        host = self.hasher.get_server(table_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            client.execute_ddl_query(query)
            print(f"Table '{table_name}' created successfully on host {host}.")

            # Get the number of partitions from the query or set a default value
            partition_number = self.extract_partition_number(query)
            if partition_number:
                for i in range(partition_number):
                    partition_path = f"/tables/{table_name}/partition{i}/host"
                    self.zk.ensure_path(partition_path)
                    self.zk.set(partition_path, host.encode('utf-8'))
                    print(f"Partition {i} created successfully for table '{table_name}'.")
            else:
                print(f"No partition specified for table '{table_name}'.")

        else:
            print("No available hosts.")

    def extract_partition_number(self, query: str) -> int:
        """
        Extracts the partition number from the CREATE TABLE query.
        Example query: "CREATE TABLE table_name (...) PARTITIONS = 5;"
        """
        partition_keyword_index = query.lower().find("partitions")
        if partition_keyword_index != -1:
            try:
                partition_number = int(query[partition_keyword_index:].split()[2])
                return partition_number
            except ValueError:
                print("Invalid partition number specified.")
        return 0

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
            # Delete znode for the partition
            self.zk.delete(f"/tables/{table_name}")
        else:
            print("No available hosts.")

    def drop_database(self, database_name: str):
        host = self.hasher.get_server(database_name)
        client = self.db_manager.get_client_for_host(host)
        if client:
            query = f"DROP DATABASE {database_name};"
            client.execute_ddl_query(query)
            print(f"Database '{database_name}' dropped successfully on host {host}.")
            self.zk.delete(f"/tables/{database_name}")
        else:
            print("No available hosts.")