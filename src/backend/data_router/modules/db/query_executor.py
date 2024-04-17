from typing import Dict, Any, List

from loguru import logger
from pyspark.sql import SparkSession
from uhashring import HashRing

from data_router.modules.db.db_node_manager import DatabaseNodeManager
from data_router.modules.host_management.host_manager import HostManager


class QueryExecutor:
    def __init__(self, host_manager: HostManager, db_manager: DatabaseNodeManager, spark_session: SparkSession,
                 hash_ring: HashRing):
        self.host_manager = host_manager
        self.db_manager = db_manager
        self.zk = self.host_manager.get_client()
        self.spark_session = spark_session
        self.hash_ring = hash_ring

    def create_table(self, table_name: str, query: str, partition_key: str):
        hosts = list(self.hash_ring.get_nodes())
        print(f"Hosts: {hosts}")
        # First create the database in each host
        for host in hosts:
            client = self.db_manager.get_client_for_host(host)
            if client:
                try:
                    client.create_database(table_name)
                    logger.info(f"Database '{table_name}' created successfully on host {host}.")
                except Exception:
                    logger.error(f"Database creation failed on host {host}.")
                    return
        # Save the partition key as a znode
        partition_key_path = f"/tables/{table_name}/partition_key"
        self.zk.ensure_path(partition_key_path)
        self.zk.set(partition_key_path, partition_key.encode('utf-8'))
        logger.info(f"Partition key '{partition_key}' saved successfully for table '{table_name}'.")
        num_hosts = len(hosts)
        # now number of partitions is equal to number of hosts
        # assign each partition to a host
        # and create the table in each host, if the creation of the table fails in any host, rollback the creation
        for i in range(num_hosts):
            host = hosts[i]
            client = self.db_manager.get_client_for_host(host)
            if client:
                partition_path = f"/tables/{table_name}/partition{i}/host"
                self.zk.ensure_path(partition_path)
                self.zk.set(partition_path, host.encode('utf-8'))
                print(f"Partition {i} created successfully for table '{table_name}'.")
                try:
                    client.execute_ddl_query(query, table_name)
                    print(f"Table '{table_name}' created successfully on host {host}.")
                except Exception:
                    print(f"Table creation failed on host {host}. Rolling back.")
                    for j in range(i):
                        partition_path = f"/tables/{table_name}/partition{j}/host"
                        self.zk.delete(partition_path)
                    break
            else:
                print("No available hosts.")

    def insert_data(self, table_name: str, data: Dict[str, Any]):
        # Pre step: Check if the table exists
        if not self.zk.exists(f"/tables/{table_name}"):
            logger.error(f"Table '{table_name}' does not exist.")
            return
        # 1. Get the partition key for the table
        partition_key_path = f"/tables/{table_name}/partition_key"
        # 2. Find the total number of partitions for the table
        partitions = self.zk.get_children(f"/tables/{table_name}")
        num_partitions = len(partitions) - 1
        # 3. Assign the partition based on the partition key
        partition_key = self.zk.get(partition_key_path)[0].decode('utf-8')
        partition = hash(data[partition_key]) % num_partitions
        logger.info(f"Partition key: {partition_key}, Partition Data: {data[partition_key]}, Partition: {partition}")
        # 4. INSERT query is formulated
        # TODO: Store this somewhere
        add_data_template = "INSERT INTO flight_data (heading, altitude, ground_speed, aircraft_code, callsign, latitude, longitude, registration, origin_airport_iata, destination_airport_iata, origin_airport_name, destination_airport_name, airline_short_name, destination_airport_country_name, destination_airport_gate, vertical_speed) VALUES ({heading}, {altitude}, {ground_speed}, '{aircraft_code}', '{callsign}', {latitude}, {longitude}, '{registration}', '{origin_airport_iata}', '{destination_airport_iata}', '{origin_airport_name}', '{destination_airport_name}', '{airline_short_name}', '{destination_airport_country_name}', '{destination_airport_gate}', {vertical_speed});"
        query = add_data_template.format(**data)
        # 5. Get the host for the partition
        partition_path = f"/tables/{table_name}/partition{partition}/host"
        host = self.zk.get(partition_path)[0].decode('utf-8')
        # 6. Execute the insert query on the host
        client = self.db_manager.get_client_for_host(host)
        if client:
            try:
                client.execute_dml_query(query, table_name)
                logger.info(f"Data inserted successfully into table '{table_name}' on host {host}.")
            except Exception:
                logger.error(f"Data insertion failed on host {host}.")
        else:
            logger.error("No available hosts.")

    def select_data(self, table_name: str, query: str) -> List[dict]:
        # 1. Get all hosts for the table
        hosts = self.host_manager.get_hosts()
        # 2. Get all the dataframes for the table from each host
        dfs = [self.db_manager.get_dataframe_for_host_and_table(host, table_name) for host in hosts]
        # 4. Union all the dataframes and create a temporary view so that we can run the query
        final_df = dfs[0]
        for i in range(1, len(dfs)):
            final_df = final_df.union(dfs[i])
        final_df.createOrReplaceTempView(table_name)
        # 5. Run the query on the unioned dataframe
        result = self.spark_session.sql(query)
        # 6. Convert the result to a list of dictionaries where each dictionary represents a row, it should have key
        # as the column name and value as the column value
        return result.toPandas().to_dict(orient='records')

    def query_data(self, table_name: str, partition_key_value: str, query: str) -> List[dict]:
        # 1. Get the partition key for the table
        partition_key_path = f"/tables/{table_name}/partition_key"
        # 2. Find the total number of partitions for the table
        partitions = self.zk.get_children(f"/tables/{table_name}")
        num_partitions = len(partitions) - 1
        # 3. Assign the partition based on the partition key
        partition_key = self.zk.get(partition_key_path)[0].decode('utf-8')
        partition = hash(partition_key_value) % num_partitions
        logger.info(f"Partition key: {partition_key}, Partition Data: {partition_key_value}, Partition: {partition}")
        # 4. Get the host for the partition
        partition_path = f"/tables/{table_name}/partition{partition}/host"
        host = self.zk.get(partition_path)[0].decode('utf-8')
        # 5. Execute the select query on the host
        client = self.db_manager.get_client_for_host(host)
        if client:
            try:
                result = client.execute_select_query(query, table_name)
                logger.info(f"Data selected successfully from table '{table_name}' on host {host}.")
                return result
            except Exception:
                logger.error(f"Data selection failed on host {host}.")
        else:
            logger.error("No available hosts.")
