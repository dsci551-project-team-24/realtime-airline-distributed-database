import os
import sys

from kazoo.client import KazooClient
from loguru import logger

from src.backend.data_router.modules.db.db_node_manager import DatabaseNodeManager
from src.backend.data_router.modules.host_management.host_manager import HostManager
from src.backend.data_router.modules.hashing.consistent_hashing import ConsistentHashing


class Modules:
    host_manager: HostManager = None
    db_node_orchestrator: DatabaseNodeManager = None
    hasher: ConsistentHashing = None


class Clients:
    zookeeper_client: KazooClient = None


def init_clients():
    def init_zookeeper_client():
        logger.info("Initializing Zookeeper client.")
        if os.environ.get("ZOOKEEPER_SERVERS") is None:
            logger.error("ZOOKEEPER_SERVERS environment variable not set.")
            sys.exit(1)
        zookeeper_servers = os.environ.get("ZOOKEEPER_SERVERS")
        client = KazooClient(hosts=zookeeper_servers)
        client.start()
        return client

    Clients.zookeeper_client = init_zookeeper_client()


async def setup_watchers():
    # setup up a watch on the children of /hosts on a separate thread
    await Modules.host_manager.watch_children()


def shutdown_clients():
    def shutdown_zookeeper_client():
        logger.info("Shutting down Zookeeper client.")
        Clients.zookeeper_client.stop()

    shutdown_zookeeper_client()


def init_modules():
    Modules.host_manager = HostManager(Clients.zookeeper_client)
    Modules.db_node_orchestrator = DatabaseNodeManager(Modules.host_manager)


def destroy_modules():
    Modules.db_node_orchestrator.close_connections()
