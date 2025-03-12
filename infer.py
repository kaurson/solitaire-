
import torch
import cv2
import numpy as np
from ultralytics import YOLO

class CardDetector:
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.5):
        """Initialize the YOLO model for detecting playing cards."""
        self.model = YOLO(model_path)  # Load a pre-trained YOLO model
        self.confidence_threshold = confidence_threshold

    def detect_cards(self, image):
        """
        Detect playing cards in the given image using YOLO.
        
        :param image: Input image (numpy array from OpenCV)
        :return: List of detected cards with bounding box coordinates
        """
        results = self.model(image)  # Run YOLO inference
        detected_cards = []

        for result in results:
            boxes = result.boxes.xyxy  # Get bounding box coordinates (x1, y1, x2, y2)
            confidences = result.boxes.conf  # Get confidence scores
            class_ids = result.boxes.cls  # Get class IDs (label indexes)

            for box, conf, class_id in zip(boxes, confidences, class_ids):
                if conf > self.confidence_threshold:
                    x1, y1, x2, y2 = map(int, box)  # Convert to integer values
                    label = f"Card {int(class_id)} ({conf:.2f})"
                    detected_cards.append((x1, y1, x2, y2, label))

                    # Draw bounding box and label
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return detected_cards, image

    def process_video(self, camera_index=0):
        """
        Capture video frames from a webcam and detect playing cards in real-time.
        """
        cap = cv2.VideoCapture(camera_index)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detected_cards, frame = self.detect_cards(frame)

            # Show the processed frame
            cv2.imshow("Card Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


# Usage Example:
if __name__ == "__main__":
    card_detector = CardDetector("yolov8s_playing_cards.pt")  # Load YOLOv8 tiny model
    card_detector.process_video()  # Run real-time card detection from the webcam
