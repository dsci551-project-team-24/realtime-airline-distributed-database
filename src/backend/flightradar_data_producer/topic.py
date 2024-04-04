import json
import os

from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic
from loguru import logger

if __name__ == '__main__':
    kafka_config = os.environ.get('KAFKA_CONFIG', '{"bootstrap.servers": "localhost:9092"}')
    kafka_config = json.loads(kafka_config)

    logger.info(f"Connecting to Kafka: {kafka_config}")
    admin_client = AdminClient(kafka_config)
    # check if connection to kafka is successful
    topics = admin_client.list_topics().topics
    if topics is None:
        logger.error("Failed to connect to Kafka")
        exit(1)
    logger.info("Connected to Kafka")
    # check if the topic realtime-flightradar24-data exists
    if "realtime-flightradar24-data" in topics.keys():
        logger.warning("Topic realtime-flightradar24-data already exists, exiting")
        exit(0)
    logger.info("Creating topic realtime-flightradar24-data since it does not exist")
    # create a topic with the name realtime-flightradar24-data and wait for it to be created
    response = admin_client.create_topics(
        [NewTopic("realtime-flightradar24-data", num_partitions=3, replication_factor=1)])
    for topic, future in response.items():
        try:
            future.result()
            logger.info(f"Topic {topic} created")
        except Exception as e:
            logger.error(f"Failed to create topic {topic}: {e}")
