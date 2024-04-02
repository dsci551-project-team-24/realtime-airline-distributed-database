#!/bin/bash

echo "Checking if the kafka topic exists and creating it if it doesn't"
python /app/flightradar_data_producer/topic.py

echo "Starting the flight radar 24 data collector and producer..."
python /app/flightradar_data_producer/producer.py