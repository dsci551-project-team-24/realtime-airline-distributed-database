from typing import List

from kazoo.client import KazooClient
from loguru import logger


class HostManager:
    def __init__(self, zookeeper_client: KazooClient):
        self.zk = zookeeper_client
        logger.info("Initializing HostManager and ensuring /hosts path exists.")
        self.zk.ensure_path("/hosts")
        logger.info("HostManager initialized.")

    def get_hosts(self) -> List[str]:
        """
        Returns all hosts in the /hosts znode.
        Example: ['host1', 'host2', ...]
        :return: List of strings containing all hosts.
        """
        logger.info("Getting all hosts.")
        host_children_znodes = self.zk.get_children("/hosts")
        return host_children_znodes
