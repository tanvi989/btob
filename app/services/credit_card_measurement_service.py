import io
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class CreditCardMeasurementService:
    CARD_WIDTH_MM = 85.6  # ISO standard credit card

    _model_path = "app/models/face_landmarker.task"
    _base_options = python.BaseOptions(model_asset_path=_model_path)
    _options = vision.FaceLandmarkerOptions(
        base_options=_base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1)
    _detector = vision.FaceLandmarker.create_from_options(_options)

    @staticmethod
    def _dist(p1, p2):
        return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) ** 0.5

    # -----------------------------
    # CREDIT CARD DETECTION
    # -----------------------------
    @staticmethod
    def detect_credit_card_width_px(img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        best_width = None

        for cnt in contours:
            rect = cv2.minAreaRect(cnt)
            (w, h) = rect[1]

            if w == 0 or h == 0:
                continue

            aspect_ratio = max(w, h) / min(w, h)
            area = w * h

            # Credit card constraints
            if 1.5 < aspect_ratio < 1.7 and area > 5000:
                width_px = max(w, h)
                if best_width is None or width_px > best_width:
                    best_width = width_px

        if best_width is None:
            raise Exception("Credit card not detected. Ensure full card visibility.")

        return best_width

    # -----------------------------
    # FACE SHAPE CLASSIFICATION
    # -----------------------------
    @staticmethod
    def classify_face_shape(width, height, chin_width):
        ratio = width / height

        if ratio > 0.9:
            return "round"
        elif 0.85 <= ratio <= 0.9:
            return "square"
        elif 0.75 <= ratio < 0.85:
            return "oval"
        elif chin_width < width * 0.7:
            return "heart"
        else:
            return "rectangle"

    # -----------------------------
    # MAIN PROCESS
    # -----------------------------
    @staticmethod
    def process(image_bytes: bytes):
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = np.array(image)
        h, w, _ = img.shape

        # ---- Credit card width ----
        card_width_px = CreditCardMeasurementService.detect_credit_card_width_px(img)
        mm_per_pixel = CreditCardMeasurementService.CARD_WIDTH_MM / card_width_px

        # ---- Face landmarks ----
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        result = CreditCardMeasurementService._detector.detect(mp_image)
        
        if not result.face_landmarks:
            raise Exception("No face detected")

        face = result.face_landmarks[0]
        points = [(int(l.x * w), int(l.y * h)) for l in face]

        # ---- Core points ----
        left_eye = points[468]
        right_eye = points[473]
        nose = points[1]

        # ---- PD ----
        pd_px = CreditCardMeasurementService._dist(left_eye, right_eye)
        pd_mm = pd_px * mm_per_pixel

        pd_left = CreditCardMeasurementService._dist(left_eye, nose) * mm_per_pixel
        pd_right = CreditCardMeasurementService._dist(right_eye, nose) * mm_per_pixel

        # ---- Face dimensions ----
        jaw_left = points[234]
        jaw_right = points[454]
        chin = points[152]
        forehead = points[10]

        face_width_mm = CreditCardMeasurementService._dist(jaw_left, jaw_right) * mm_per_pixel
        face_height_mm = CreditCardMeasurementService._dist(chin, forehead) * mm_per_pixel

        chin_width_mm = CreditCardMeasurementService._dist(points[132], points[361]) * mm_per_pixel

        face_shape = CreditCardMeasurementService.classify_face_shape(
            face_width_mm,
            face_height_mm,
            chin_width_mm
        )

        return {
            "scale": {
                "reference": "credit_card",
                "card_width_px": round(card_width_px, 1),
                "mm_per_pixel": round(mm_per_pixel, 4)
            },
            "mm": {
                "pd": round(pd_mm, 1),
                "pd_left": round(pd_left, 1),
                "pd_right": round(pd_right, 1),
                "nose_left": round(pd_left, 1),
                "nose_right": round(pd_right, 1),
                "face_width": round(face_width_mm, 1),
                "face_height": round(face_height_mm, 1)
            },
            "face_shape": face_shape
        }
