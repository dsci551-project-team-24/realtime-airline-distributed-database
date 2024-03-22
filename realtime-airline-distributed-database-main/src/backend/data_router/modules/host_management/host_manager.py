from typing import List

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
from loguru import logger
from src.backend.data_router.modules.hashing import consistent_hashing


class HostManager:
    def __init__(self, zookeeper_client: KazooClient):
        self.zk = zookeeper_client
        logger.info("Initializing HostManager and ensuring /hosts path exists.")
        self.zk.ensure_path("/hosts")
        logger.info("HostManager initialized.")

    def get_client(self) -> KazooClient:
        return self.zk

    def get_hosts(self) -> List[str]:
        """
        Returns all hosts in the /hosts znode.
        Example: ['host1', 'host2', ...]
        :return: List of strings containing all hosts.
        """
        logger.info("Getting all hosts.")
        host_children_znodes = self.zk.get_children("/hosts")
        return host_children_znodes

    def add_host(self, host_name: str, host_url: str):
        logger.info(f"Adding host {host_name} with URL {host_url}.")
        host_path = f"/hosts/{host_name}"
        self.zk.ensure_path(host_path)
        self.zk.set(host_path, host_url.encode())
        logger.info(f"Host {host_name} added with URL {host_url}.")

    def get_partition_host(self, table_name: str, partition_number: int) -> str:
        logger.info(f"Getting host for partition {partition_number} of table {table_name}.")
        partition_path = f"/tables/{table_name}/partition{partition_number}/host"
        try:
            data, _ = self.zk.get(partition_path)
            return data.decode()
        except NoNodeError:
            logger.error(f"Partition {partition_number} of table {table_name} not found.")
            return ""

    def get_host_url(self, host_name: str) -> str:
        logger.info(f"Getting URL for host {host_name}.")
        host_path = f"/hosts/{host_name}"
        try:
            data, _ = self.zk.get(host_path)
            return data.decode()
        except NoNodeError:
            logger.error(f"Host {host_name} not found.")
            return ""

    def map_partition_to_host(self, table_name: str, partition_number: int, host_name: str):
        logger.info(f"Mapping partition {partition_number} of table {table_name} to host {host_name}.")
        partition_path = f"/tables/{table_name}/partition{partition_number}/host"
        self.zk.ensure_path(partition_path)
        self.zk.set(partition_path, host_name.encode())
        logger.info(f"Partition {partition_number} of table {table_name} mapped to host {host_name}.")

    def map_partition_to_host_with_hash(self, table_name: str, partition_number: int):
        logger.info(f"Mapping partition {partition_number} of table {table_name} with hash.")
        host_name = self.hasher.get_server(f"{table_name}-{partition_number}")
        self.map_partition_to_host(table_name, partition_number, host_name)
        logger.info(f"Partition {partition_number} of table {table_name} mapped to host {host_name} using hash.")

