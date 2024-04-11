import asyncio
import os
import sys

from kazoo.client import KazooClient
from loguru import logger
from pyspark.sql import SparkSession

from data_router.consumers.ingestion_consumer import IngestionConsumer
from data_router.modules.db.db_node_manager import DatabaseNodeManager
from data_router.modules.db.query_executor import QueryExecutor
from data_router.modules.host_management.host_manager import HostManager



class Modules:
    host_manager: HostManager = None
    db_node_orchestrator: DatabaseNodeManager = None
    query_executor: QueryExecutor = None


class Clients:
    zookeeper_client: KazooClient = None
    spark_session: SparkSession = None


class Consumers:
    ingestion_consumer: IngestionConsumer = None


def init_clients():
    def create_spark_session():
        mysql_connector_jar_path = os.environ.get("MYSQL_CONNECTOR_JAR_PATH", None)
        if mysql_connector_jar_path is None:
            logger.error("MYSQL_CONNECTOR_JAR_PATH environment variable not set.")
            sys.exit(1)
        return SparkSession \
            .builder \
            .config("spark.jars", mysql_connector_jar_path) \
            .master("spark://spark-master:7077") \
            .getOrCreate()

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
    Clients.spark_session = create_spark_session()


async def setup_watchers():
    # setup up a watch on the children of /hosts on a separate thread
    await Modules.host_manager.watch_children()


def shutdown_clients():
    def shutdown_zookeeper_client():
        logger.info("Shutting down Zookeeper client.")
        Clients.zookeeper_client.stop()

    def shutdown_spark_session():
        logger.info("Shutting down Spark session.")
        Clients.spark_session.stop()

    shutdown_zookeeper_client()
    shutdown_spark_session()


def init_modules():
    Modules.host_manager = HostManager(Clients.zookeeper_client)
    Modules.db_node_orchestrator = DatabaseNodeManager(Modules.host_manager, Clients.spark_session)
    Modules.query_executor = QueryExecutor(host_manager=Modules.host_manager, db_manager=Modules.db_node_orchestrator,
                                           spark_session=Clients.spark_session)


def init_consumers():
    Consumers.ingestion_consumer = IngestionConsumer(Modules.query_executor)


async def start_consumers():
    loop = asyncio.get_event_loop()
    loop.create_task(Consumers.ingestion_consumer.consume())


async def shutdown_consumers():
    await Consumers.ingestion_consumer.shutdown()


def destroy_modules():
    Modules.db_node_orchestrator.close_connections()
