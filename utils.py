import requests

import cv2.dnn
import numpy as np

CLASSES = {
  0: "SpeedLimit_30",
  1: "SpeedLimit_50",
  2: "TrafficSignalsAhead",
  3: "PedestiranCrossingAhead",
  4: "RedTrafficLight",
  5: "GreenTrafficLight"
}
colors = np.random.uniform(0, 255, size=(len(CLASSES), 3))


def preprocess(original_image):
    # original_image: np.ndarray = cv2.imread(image_path)
    [height, width, _] = original_image.shape

    # Prepare a square image for inference
    length = max((height, width))
    image = np.zeros((length, length, 3), np.uint8)
    image[0:height, 0:width] = original_image

    # Calculate scale factor
    scale = length / 640

    # Preprocess the image and prepare blob for model
    blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255, size=(640, 640), swapRB=True)
    return blob, scale, original_image


# def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
#     """
#     Draws bounding boxes on the input image based on the provided arguments.

#     Args:
#         img (numpy.ndarray): The input image to draw the bounding box on.
#         class_id (int): Class ID of the detected object.
#         confidence (float): Confidence score of the detected object.
#         x (int): X-coordinate of the top-left corner of the bounding box.
#         y (int): Y-coordinate of the top-left corner of the bounding box.
#         x_plus_w (int): X-coordinate of the bottom-right corner of the bounding box.
#         y_plus_h (int): Y-coordinate of the bottom-right corner of the bounding box.
#     """
#     font = cv2.FONT_HERSHEY_SIMPLEX,
#     text_color_bg = colors[class_id]
#     label = f'{CLASSES[class_id]} {confidence:.2f}'
#     (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
#     cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), text_color_bg, 2) # Box
#     cv2.rectangle(img, (x, y-label_height), (x+label_width, y), text_color_bg, cv2.FILLED)  # Background label
#     cv2.putText(img, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)

# def postprocess(response, scale, original_image):
#     outputs = np.array([cv2.transpose(response[0])])
#     rows = outputs.shape[1]

#     boxes = []
#     scores = []
#     class_ids = []

#     # Iterate through output to collect bounding boxes, confidence scores, and class IDs
#     for i in range(rows):
#         classes_scores = outputs[0][i][4:]
#         (minScore, maxScore, minClassLoc, (x, maxClassIndex)) = cv2.minMaxLoc(classes_scores)
#         if maxScore >= 0.25:
#             box = [
#                 outputs[0][i][0] - (0.5 * outputs[0][i][2]), outputs[0][i][1] - (0.5 * outputs[0][i][3]),
#                 outputs[0][i][2], outputs[0][i][3]]
#             boxes.append(box)
#             scores.append(maxScore)
#             class_ids.append(maxClassIndex)
#     result_boxes = cv2.dnn.NMSBoxes(boxes, scores, 0.25, 0.45, 0.5)

#     detections = []

#     # Iterate through NMS results to draw bounding boxes and labels
#     for i in range(len(result_boxes)):
#         index = result_boxes[i]
#         box = boxes[index]
#         detection = {
#             'class_id': class_ids[index],
#             'class_name': CLASSES[class_ids[index]],
#             'confidence': scores[index],
#             'box': box,
#             'scale': scale}
#         detections.append(detection)
#         draw_bounding_box(original_image, class_ids[index], scores[index], round(box[0] * scale), round(box[1] * scale),
#                           round((box[0] + box[2]) * scale), round((box[1] + box[3]) * scale))
#     return original_image

def postprocess(response):
    outputs = np.array([cv2.transpose(response[0])])
    rows = outputs.shape[1]

    boxes = []
    scores = []
    class_ids = []

    # Iterate through output to collect bounding boxes, confidence scores, and class IDs
    for i in range(rows):
        classes_scores = outputs[0][i][4:]
        (minScore, maxScore, minClassLoc, (x, maxClassIndex)) = cv2.minMaxLoc(classes_scores)
        if maxScore >= 0.25:
            box = [
                outputs[0][i][0] - (0.5 * outputs[0][i][2]), outputs[0][i][1] - (0.5 * outputs[0][i][3]),
                outputs[0][i][2], outputs[0][i][3]]
            boxes.append(box)
            scores.append(maxScore)
            class_ids.append(maxClassIndex)

    detections = []
    result_boxes = cv2.dnn.NMSBoxes(boxes, scores, 0.25, 0.45, 0.5)
    # Iterate through NMS results to draw bounding boxes and labels
    for i in range(len(result_boxes)):
        index = result_boxes[i]
        box = boxes[index]
        detection = {
            'class_id': class_ids[index],
            'class_name': CLASSES[class_ids[index]],
            'confidence': f"{scores[index]:.2f}",
            'box': [f"{c:.2f}" for c in box]}
        detections.append(detection)
    return detections