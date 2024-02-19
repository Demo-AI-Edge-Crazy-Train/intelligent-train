# Intelligent train

Embeded model using ONNXRuntime, that is suited for CPU. Listen to a mqtt topic and publish to another.
Look for env var in ```app.py``` for customization.

## Run

1. Run ```mosquitto```
2. Run ```python app.py```
3. Publish image in base64 format to the input mqtt topic. You can run ```./publish``` as an exemple.

## Docker

```
podman pod create intelligent-train
podman run -d --pod intelligent-train eclipse-mosquitto
podman run -d --pod intelligent-train quay.io/demo-ai-edge-crazy-train/intelligent-train:v1.0
# TODO: script to run ./publish in pod network
```