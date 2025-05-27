#!/bin/bash

set -Eeuo pipefail

MQTT_BROKER="${MQTT_BROKER:-localhost}"
MQTT_PORT="${MQTT_PORT:-1883}"
MQTT_TOPIC="${MQTT_TOPIC:-train-image}"
IMAGE_FILE="${IMAGE_FILE:-test.jpg}"

mosquitto_pub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "$MQTT_TOPIC" -s <<EOF
{"image": "$(base64 -w0 $IMAGE_FILE)", "id": "$(date -Iseconds)"}
EOF
