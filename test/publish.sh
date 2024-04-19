#!/bin/bash
MQTT_BROKER="localhost"
MQTT_PORT=1883
MQTT_TOPIC="train-image"
# Function to generate random numbers
# Function to generate random numbers and encode to Base64
IMG=$(base64 test.jpg)
json_payload="{\"image\": \"$IMG\", \"id\": \"test\"}"
echo $json_payload > payload.json
mosquitto_pub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "$MQTT_TOPIC" -f payload.json