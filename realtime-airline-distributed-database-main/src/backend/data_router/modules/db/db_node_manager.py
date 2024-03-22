# This script essentially acts as a manager for dynamically handling MySQL database nodes, adding or removing them based
# on changes detected by the host manager. It ensures proper credential handling and logging throughout the process.

import os
import signal
from typing import Dict, Union

from loguru import logger

from src.backend.data_router.clients.mysql_client import MySqlClient
from src.backend.data_router.modules.host_management.host_manager import HostManager


class DatabaseNodeManager:
    host_manager: HostManager
    mysql_user: str
    mysql_password: str
    clients: Dict[str, MySqlClient]

    def __init__(self, host_manager: HostManager):
        self.host_manager = host_manager
        self.clients = {}
        self.__creds_check_and_set()
        self.watcher = host_manager.get_client().ChildrenWatch("/hosts", self.__watcher_callback)

    def __watcher_callback(self, children):
        logger.info(f"Children of /hosts updated to: {children}")
        current_nodes = set(self.clients.keys())
        new_nodes = set(children)
        nodes_to_add = new_nodes - current_nodes
        nodes_to_remove = current_nodes - new_nodes
        is_operation_needed = len(nodes_to_add) > 0 or len(nodes_to_remove) > 0
        if not is_operation_needed:
            logger.info("No operation needed.")
            return
        if len(nodes_to_add) > 0:
            logger.info(f"Need to add nodes: {nodes_to_add}")
        if len(nodes_to_remove) > 0:
            logger.info(f"Need to remove nodes: {nodes_to_remove}")
        for node in nodes_to_add:
            logger.info(f"Adding node {node}")
            self.add_node(node, self.mysql_user, self.mysql_password)
        for node in nodes_to_remove:
            logger.info(f"Removing node {node}")
            self.remove_node(node)

    def __creds_check_and_set(self):
        if os.environ.get("MYSQL_USER") is None:
            logger.error("MYSQL_USER environment variable not set.")
            os.kill(os.getpid(), signal.SIGTERM)
        if os.environ.get("MYSQL_PASSWORD") is None:
            logger.error("MYSQL_PASSWORD environment variable not set.")
            os.kill(os.getpid(), signal.SIGTERM)
        self.mysql_user = os.environ.get("MYSQL_USER")
        self.mysql_password = os.environ.get("MYSQL_PASSWORD")

    def get_client_for_host(self, host: str) -> Union[MySqlClient, None]:
        if host not in self.clients:
            logger.error(f"Node {host} does not exist")
            return None
        return self.clients[host]

    def add_node(self, host: str, username: str, password: str) -> bool:
        if host in self.clients:
            logger.error(f"Node {host} already exists")
            return False
        client = MySqlClient(host, username, password)
        self.clients[host] = client
        return True

    def remove_node(self, host: str) -> bool:
        if host not in self.clients:
            logger.error(f"Node {host} does not exist")
            return False
        client = self.clients[host]
        client.close_connection()
        del self.clients[host]
        return True

    def close_connections(self) -> None:
        for client in self.clients.values():
            client.close_connection()
        self.clients = {}
