import asyncio
import json
import os

from aiokafka import AIOKafkaConsumer
from loguru import logger

from data_router.modules.db.query_executor import QueryExecutor


class IngestionConsumer:
    query_executor: QueryExecutor = None
    kafka_bootstrap_servers: str = None
    ingestion_topic: str = None
    consumer: AIOKafkaConsumer = None

    def __init__(self, query_executor: QueryExecutor):
        self.query_executor = query_executor
        self.kafka_bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
        self.ingestion_topic = os.environ.get("INGESTION_TOPIC")

    async def consume(self):
        consumer = AIOKafkaConsumer("realtime-flightradar24-data", bootstrap_servers="kafka")
        # keep trying to connect to kafka until it is successful
        while True:
            try:
                await consumer.start()
                logger.info("Consumer started")
                break
            except Exception as e:
                logger.error(f"Failed to connect to Kafka: {e}")
                await asyncio.sleep(5)
        try:
            async for message in consumer:
                # log message id and timestamp
                logger.info(f"Consumed message: {message.timestamp}")
                json_data = message.value.decode("utf-8")
                json_data = json.loads(json_data)
                self.query_executor.insert_data("flight_data", json_data)
        finally:
            await consumer.stop()

    async def shutdown(self):
        await self.consumer.stop()
