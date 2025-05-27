#!/bin/bash

set -Eeuo pipefail

# Replace these variables with your MQTT broker details
MQTT_BROKER="${MQTT_BROKER:-localhost}"
MQTT_PORT="${MQTT_PORT:-1883}"
MQTT_TOPIC="${MQTT_TOPIC:-train-image}"
MQTT_RESPONSE_TOPIC="${MQTT_RESPONSE_TOPIC:-train-model-result}"

# Path to the image file
IMAGE_FILE="${IMAGE_FILE:-test.jpg}"

declare -a float_list=()

for ((i = 1; i <= 100; i++)); do
    echo "Iteration $i"
    start=$(date +%s.%N)
    . publish.sh
    stop=$(mosquitto_sub -v -t "$MQTT_RESPONSE_TOPIC" -C 1 | xargs -d$'\n' -L1 bash -c 'date +%s.%N')
    duration=$(echo "$stop - $start" | bc -q /dev/stdin )
    float_list+=("$duration")
    echo $duration
    sleep 0.1
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
echo "Mean: $mean s"
