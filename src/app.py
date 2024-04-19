import paho.mqtt.client as mqtt
import base64
import numpy as np
import time
import onnxruntime as ort
import json
import os
import logging
import ast

from prometheus_client import start_http_server, Summary, Histogram
from utils import *


# Define the MQTT settings
MQTT_BROKER = os.environ.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "train-image")
MQTT_PUB_TOPIC = os.environ.get("MQTT_PUB_TOPIC", "train-model-result")
# Other variables
MODEL_PATH = os.environ.get("MODEL_PATH", "models/model.onnx")
IMG_IN_RESPONSE = bool(os.environ.get("IMG_IN_RESPONSE", True))
# Onnxruntime providers
PROVIDERS = ast.literal_eval(os.environ.get("ONNXRUNTIME_PROVIDERS", '["CUDAExecutionProvider"]'))
# Prometheus
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


# Define the MQTT event handler
@REQUEST_TIME.time()
def on_message(client, userdata, msg):
    start_fun = time.time()
    # Process the received image
    payload = json.loads(msg.payload)
    image_id = payload["id"]
    image = payload["image"]
    nparr = np.frombuffer(base64.b64decode(payload["image"]), np.uint8)
    nparr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    start_pre = time.time()
    preprocessed, scale, original_image = preprocess(nparr)
    time_pre = time.time() - start_pre
    start_inf = time.time()
    outputs = ort_sess.run(None, {'images': preprocessed})
    time_inf = time.time() - start_inf
    start_post = time.time()
    detections = postprocess(outputs[0])
    img_b64 = str(image) if IMG_IN_RESPONSE else ""
    time_post = time.time() - start_post
    time_fun = time.time() - start_fun
    total_inference_time = time_pre + time_inf + time_post
    h.observe(time_pre + time_inf + time_post)
    #cv2.imwrite("last.png", nparr)
    payload = {
        "id": image_id, "image": img_b64, "detections": detections, "pre-process": f'{time_pre:.2f}s', 
        "inference": f'{time_inf:.2f}s', "post-process": f'{time_post:.2f}s', 
        "total": f'{time_fun:.2f}s', "scale": scale
    }
   
    payload = json.dumps(payload)
    #logger.info(f"Processed payload: {payload}")
    start_pub = time.time()
    client.publish(MQTT_PUB_TOPIC, payload)
    stop_pub = time.time() - start_pub
    logger.info(f"Processed image {image_id} in {total_inference_time:.5f}s")

def on_connect(client, userdata, flags, rc, properties):
    logger.info(f"Connected with result code {rc}")
    # Subscribe to the MQTT topic when connected
    client.subscribe(MQTT_TOPIC)
    logger.info(f"Subscribed to topic: {MQTT_TOPIC}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.info("Unexpected disconnection from MQTT broker")

if __name__ == "__main__":
    # Logger
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    # Prometheus
    start_http_server(8000)
    h = Histogram('request_latency_seconds', 'Total inference time')
    # Inference Session
    ort_sess = ort.InferenceSession(MODEL_PATH, providers=PROVIDERS)
    # Create a MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Connect to the MQTT broker
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 120)
            break
        except ConnectionRefusedError:
            logger.info("Connection refused, retying in few seconds...")
            time.sleep(3)

    # Start the MQTT loop
    client.loop_forever()
