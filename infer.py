import cv2
import torch
from ultralytics import YOLO

class CardDetectorImage:
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.5):
        """Initialize the YOLO model for detecting playing cards in an image."""
        self.model = YOLO(model_path)  # Load the YOLO model (pre-trained or custom)
        self.confidence_threshold = confidence_threshold

    def detect_cards(self, image_path):
        """
        Detect playing cards in an image using YOLO.
        
        :param image_path: Path to the image file.
        :return: List of detected cards with bounding box coordinates.
        """
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print("Error: Unable to load image.")
            return [], None

        # Run YOLO inference on the image
        results = self.model(image)

        detected_cards = []
        for result in results:
            boxes = result.boxes.xyxy  # Bounding boxes (x1, y1, x2, y2)
            confidences = result.boxes.conf  # Confidence scores
            class_ids = result.boxes.cls  # Class IDs (object labels)

            for box, conf, class_id in zip(boxes, confidences, class_ids):
                if conf > self.confidence_threshold:
                    x1, y1, x2, y2 = map(int, box)  # Convert to integers
                    label = f"Card {int(class_id)} ({conf:.2f})"
                    detected_cards.append((x1, y1, x2, y2, label))

                    # Draw bounding box and label
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return detected_cards, image

    def process_image(self, image_path, output_path="output.jpg"):
        """
        Detects cards in an image and saves the result with bounding boxes.

        :param image_path: Path to the input image.
        :param output_path: Path to save the output image.
        """
        detected_cards, processed_image = self.detect_cards(image_path)

        if processed_image is not None:
            # Save the processed image
            #cv2.imwrite(output_path, processed_image)
            print(f"Processed image saved as {output_path}")

        return detected_cards


# Example Usage
if __name__ == "__main__":
    image_path = "/Users/kaur/PycharmProjects/experiments/Kooliproge_11kl/solitaire/playing-cards-royal-flush-on-black-background-natalie-kinnear.jpg"  # Replace with your image file
    card_detector = CardDetectorImage("yolov8s_playing_cards.pt")  # Load YOLOv8 model
    detected_cards = card_detector.process_image(image_path)

    # Print detected card positions
    print("\nDetected Cards:")
    for card in detected_cards:
        print(f"Card at (x1={card[0]}, y1={card[1]}, x2={card[2]}, y2={card[3]}) -> {card[4]}")
