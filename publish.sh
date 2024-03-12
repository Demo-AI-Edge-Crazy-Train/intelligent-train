#!/bin/bash

# Replace these variables with your MQTT broker details
MQTT_BROKER="localhost"
MQTT_PORT=1883
MQTT_TOPIC="images"

# Path to the image file
IMAGE_FILE="test.jpg"

# Encode the image file as base64
IMAGE_BASE64=$(base64 -w 0 "$IMAGE_FILE")

# Publish the base64-encoded image to the MQTT broker
mosquitto_pub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "$MQTT_TOPIC" -m '{"image": "'"$IMAGE_BASE64"'", "id": "test"}'
