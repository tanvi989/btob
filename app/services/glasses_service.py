from app.glasses.detector import detector
from PIL import Image
import io
from app.services.glasses_removal import remove_glasses_service

class GlassesService:

    @staticmethod
    def detect(image_bytes: bytes):
        if detector is None:
            return {"glasses_detected": False, "confidence": 0.0}
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        result = detector.predict(image)

        return {
            "glasses_detected": result["glasses_detected"],
            "confidence": result.get("confidence", 0.0)
        }

    @staticmethod
    def remove_glasses(image_bytes: bytes):
        return remove_glasses_service(image_bytes)  # raw bytes
