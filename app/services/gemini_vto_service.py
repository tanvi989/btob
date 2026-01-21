import io
import json
import base64
from PIL import Image
from google import genai
from google.genai import types
from app.utils.settings import settings

class GeminiVTOService:
    client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None

    @staticmethod
    def analyze_face_for_vto(image_bytes: bytes):
        if not GeminiVTOService.client:
            raise Exception("Gemini API key not configured")

        # Encode image to base64
        img = Image.open(io.BytesIO(image_bytes))
        
        prompt = """
        Analyze this face for virtual glasses try-on. 
        Provide the exact coordinates (x, y) for:
        1. Left pupil center
        2. Right pupil center
        3. Nose bridge (where glasses would sit)
        
        Return the result as a JSON object with keys: "left_pupil", "right_pupil", "nose_bridge".
        Coordinates should be normalized from 0.0 to 1.0 (top-left is 0,0).
        Example: {"left_pupil": {"x": 0.45, "y": 0.4}, "right_pupil": {"x": 0.55, "y": 0.4}, "nose_bridge": {"x": 0.5, "y": 0.42}}
        """

        response = GeminiVTOService.client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )

        try:
            return json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to parse Gemini response: {str(e)}")
