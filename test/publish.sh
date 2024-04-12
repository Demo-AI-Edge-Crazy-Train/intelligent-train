#!/bin/bash
MQTT_BROKER="localhost"
MQTT_PORT=1883
MQTT_TOPIC="train-image"
# Function to generate random numbers
# Function to generate random numbers and encode to Base64
mosquitto_pub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "$MQTT_TOPIC" -f kafka_messages.json