"""YOLO person detector. Weights stay local and are never downloaded implicitly."""
from pathlib import Path


class PersonDetector:
    def __init__(self, model_path, device="cpu", confidence=0.32, image_size=640):
        path = Path(model_path)
        if not path.is_file():
            raise FileNotFoundError(f"Model not found: {path}")
        if not 0.1 <= confidence <= 1:
            raise ValueError("confidence must be between 0.1 and 1")
        if image_size < 32:
            raise ValueError("image_size must be at least 32")
        from ultralytics import YOLO

        self.model = YOLO(str(path))
        self.person_classes = [key for key, value in self.model.names.items() if value == "person"]
        if not self.person_classes:
            raise ValueError("Model has no person class")
        self.device = device
        self.confidence = confidence
        self.image_size = image_size

    def detect(self, frame):
        return self.model.predict(
            frame, classes=self.person_classes, conf=0.1, iou=0.7,
            imgsz=self.image_size, device=self.device, verbose=False, max_det=300,
        )[0].boxes.cpu().numpy()
