import paho.mqtt.client as mqtt
from io import BytesIO
import base64
import cv2
import numpy as np
import time
import onnxruntime as ort
import json
import os

from utils import *


# Define the MQTT settings
MQTT_BROKER = os.environ.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "train-image")
MQTT_PUB_TOPIC = os.environ.get("MQTT_PUB_TOPIC", "train-model-result")
# Other variables
MODEL_PATH = os.environ.get("MODEL_PATH", "models/model.onnx")
IMG_IN_RESPONSE = bool(os.environ.get("IMG_IN_RESPONSE", True))


# Define the MQTT event handler
def on_message(client, userdata, msg):
    start_fun = time.time()
    print(f"Received message on topic {msg.topic}")
    # Process the received image
    #processed_image = process_image(msg.payload)
    payload = json.loads(msg.payload)
    image_id = payload["id"]
    image = payload["image"]
    print(f"Received image with id {image_id}")
    #print(f"Received image with size {len(image)}")

    nparr = np.frombuffer(base64.b64decode(payload["image"]), np.uint8)
    #print(f"Received image with shape {nparr.shape}")
    nparr = nparr.reshape(480, 640, 3)
    #print(f"shape after reshape {nparr.shape}")

    #print(nparr)
    #img_data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # Example: Save the processed image to disk
    #cv2.imwrite("test.jpg", nparr)
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
    #cv2.imwrite("last.png", new_image)
    payload = {
        "id": image_id, "image": img_b64, "detections": detections, "pre-process": f'{time_pre:.2f}s', 
        "inference": f'{time_inf:.2f}s', "post-process": f'{time_post:.2f}s', 
        "total": f'{time_fun:.2f}s', "scale": scale
    }
   
    payload = json.dumps(payload)
    #print(f"Processed payload: {payload}")
    start_pub = time.time()
    client.publish(MQTT_PUB_TOPIC, payload)
    stop_pub = time.time() - start_pub
    print(f"Published a message to \"{MQTT_PUB_TOPIC}\" topic")

def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected with result code {rc}")
    # Subscribe to the MQTT topic when connected
    client.subscribe(MQTT_TOPIC)
    print(f"Subscribed to topic: {MQTT_TOPIC}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection from MQTT broker")

if __name__ == "__main__":
    ort_sess = ort.InferenceSession(MODEL_PATH, providers=['CUDAExecutionProvider'])

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
            print("Connection refused, retying in few seconds...")
            time.sleep(3)

    # Start the MQTT loop
    client.loop_forever()
