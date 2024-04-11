import json
import os
import time

from FlightRadar24 import Flight
from confluent_kafka import Producer
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By

time_to_sleep = int(os.environ.get('TIME_TO_SLEEP', 30))


def get_detailed_flight_information(driver, flight_id):
    try:
        driver.get(f"https://data-live.flightradar24.com/clickhandler/?flight={flight_id}")
    except Exception as e:
        producer.flush()
        logger.error(f"Failed to get detailed flight information for flight_id={flight_id}: {e}")
        # wait for some time as the server might be throttling us
        logger.info(f"Sleeping for {time_to_sleep} seconds, then retrying to get data from flightradar24")
        time.sleep(time_to_sleep)
        return None
    try:
        data = driver.find_element(By.XPATH, "/html/body/pre").text
    except Exception as e:
        producer.flush()
        logger.error(f"Failed to get detailed flight information for flight_id={flight_id}: {e}")
        # wait for some time as the server might be throttling us
        logger.info(f"Sleeping for {time_to_sleep} seconds, then retrying to get data from flightradar24")
        time.sleep(time_to_sleep)
        return None
    return json.loads(data)


def convert_to_json(flight):
    if (flight.origin_airport_name is None
            or flight.destination_airport_name is None
            or flight.origin_airport_iata is None
            or len(flight.origin_airport_iata) < 3
            or len(flight.destination_airport_iata) < 3
            or flight.destination_airport_iata is None
            or flight.registration is None
            or flight.callsign is None
            or flight.aircraft_code is None
            or flight.latitude is None
            or flight.longitude is None
            or flight.heading is None
            or flight.altitude is None
            or flight.ground_speed is None
            or flight.airline_short_name is None
            or flight.destination_airport_country_name is None
            or flight.destination_airport_gate is None
            or flight.vertical_speed is None
    ):
        return None
    return {
        "heading": flight.heading,
        "altitude": flight.altitude,
        "ground_speed": flight.ground_speed,
        "aircraft_code": flight.aircraft_code,
        "callsign": flight.callsign,
        "latitude": flight.latitude,
        "longitude": flight.longitude,
        "registration": flight.registration,
        "origin_airport_iata": flight.origin_airport_iata,
        "destination_airport_iata": flight.destination_airport_iata,
        "origin_airport_name": flight.origin_airport_name,
        "destination_airport_name": flight.destination_airport_name,
        "airline_short_name": flight.airline_short_name,
        "destination_airport_country_name": flight.destination_airport_country_name,
        "destination_airport_gate": flight.destination_airport_gate,
        "vertical_speed": flight.vertical_speed,
    }


if __name__ == '__main__':
    logger.info("Starting the producer")
    kafka_config = os.environ.get('KAFKA_CONFIG', '{"bootstrap.servers": "localhost:9092"}')
    kafka_config = json.loads(kafka_config)
    logger.info(f"Connecting to Kafka: {kafka_config}")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    logger.info("Setting up selenium webdriver")
    if "SELENIUM_DRIVER_URL" in os.environ:
        server = os.environ.get('SELENIUM_DRIVER_URL')
        driver = webdriver.Remote(command_executor=server, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    logger.info("Selenium webdriver setup complete, connecting to Kafka")
    producer = Producer(kafka_config)
    while True:
        logger.info("Fetching data from flightradar24")
        # get the data from the api
        try:
            driver.get("https://data-cloud.flightradar24.com/zones/fcgi/feed.js?airline=DAL")
        except Exception as e:
            logger.error(f"Failed to get data from flightradar24: {e}")
            # wait for some time as the server might be throttling us
            logger.info(f"Sleeping for {time_to_sleep} seconds, then retrying to get data from flightradar24")
            time.sleep(time_to_sleep)
            continue
        # use xpath to get the data
        try:
            data = driver.find_element(By.XPATH, "/html/body/pre").text
        except Exception as e:
            logger.error(f"Failed to get data from flightradar24: {e}")
            # wait for some time as the server might be throttling us
            producer.flush()
            logger.info(f"Sleeping for {time_to_sleep} seconds, then retrying to get data from flightradar24")
            time.sleep(time_to_sleep)
            continue
        parsed_data = json.loads(data)
        print(f"Found {len(parsed_data)} flights")
        for flight_id, flight_info in parsed_data.items():
            # Get flights only.
            if not flight_id[0].isnumeric():
                continue
            flight = Flight(flight_id, flight_info)
            flight_details = get_detailed_flight_information(driver, flight_id)
            if flight_details is None:
                continue
            flight.set_flight_details(flight_details)
            jsonified_flight = convert_to_json(flight)
            if jsonified_flight is None:
                continue
            producer.produce('realtime-flightradar24-data', json.dumps(jsonified_flight))
            logger.info(f"Produced message for flight_id={flight.id}")
        # sleep for 30 seconds
        time.sleep(time_to_sleep)
        producer.flush()
