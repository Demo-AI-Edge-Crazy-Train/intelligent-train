#!/bin/bash

# Replace these variables with your MQTT broker details
MQTT_BROKER="localhost"
MQTT_PORT=1883
MQTT_TOPIC="images"
MQTT_RESPONSE_TOPIC="results"

# Path to the image file
IMAGE_FILE="../traffic-signs.jpg"

# Encode the image file as base64
IMAGE_BASE64=$(base64 -w 0 "$IMAGE_FILE")

float_list=()

for ((i = 1; i <= 3; i++)); do
    echo "Iteration $i"
    mosquitto_pub -h "$MQTT_BROKER" -p "$MQTT_PORT" -t "$MQTT_TOPIC" -m "$IMAGE_BASE64"
    start=$(date +%s%N)
    stop=$(mosquitto_sub -v -t results -C 1 | xargs -d$'\n' -L1 bash -c 'date +%s%N')
    duration_ns=$((stop - start))
    duration_ms=$((duration_ns / 1000000))
    float_list+=("$duration_ms")
    echo $duration_ms
    sleep 1
done

calculate_mean() {
    local sum=0
    for number in "$@"; do
        sum=$(awk "BEGIN{print $sum + $number}")
    done
    local mean=$(awk "BEGIN{print $sum / $#}")
    echo "$mean"
}

mean=$(calculate_mean "${float_list[@]}")
echo "Mean: $mean"