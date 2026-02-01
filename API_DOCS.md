# API Documentation (localhost:8000/docs)

Base URL: **http://localhost:8000**

---

## Root

| Method | Path | Description |
|--------|------|-------------|
| **GET** | `/` | Health check. Returns `{"message": "API running"}`. |

---

## Glasses Detection (`/glasses`)

| Method | Path | Description |
|--------|------|-------------|
| **POST** | `/glasses/detect` | Detect if the face image has glasses. |
| **POST** | `/glasses/remove` | Remove glasses from the face image and return edited image. |

### POST `/glasses/detect`

- **Body:** `multipart/form-data`
  - `file` (required): image file (e.g. capture.jpg)
  - `guest_id` (optional): default `"temp_guest"`
  - `session_id` (optional): default `"temp_session"`

- **Success response:**
  ```json
  {
    "success": true,
    "glasses_detected": true,
    "confidence": 0.95
  }
  ```

- **Error response:**
  ```json
  { "success": false, "error": "..." }
  ```

### POST `/glasses/remove`

- **Body:** `multipart/form-data`
  - `image` (required): image file
  - `guest_id` (optional): default `"temp_guest"`
  - `session_id` (optional): default `"temp_session"`

- **Success response:**
  ```json
  {
    "success": true,
    "edited_image_base64": "<base64 string>"
  }
  ```

- **Error response:**
  ```json
  { "success": false, "error": "..." }
  ```

---

## Landmark Detection (`/landmarks`)

| Method | Path | Description |
|--------|------|-------------|
| **POST** | `/landmarks/detect` | Detect face landmarks and return measurements (PD, face shape, etc.). |
| **POST** | `/landmarks/credit-card` | Measure scale using a credit card in the image. |

### POST `/landmarks/detect`

- **Body:** `multipart/form-data`
  - `file` (required): image file
  - `guest_id` (optional): default `"temp_guest"`
  - `session_id` (optional): default `"temp_session"`

- **Success response:**
  ```json
  {
    "success": true,
    "landmarks": {
      "scale": { "mm_per_pixel": ..., "iris_diameter_px": ... },
      "mm": {
        "pd": 62,
        "pd_left": 31,
        "pd_right": 31,
        "nose_bridge_left": ...,
        "nose_bridge_right": ...,
        "face_width": ...,
        "face_height": ...,
        "face_ratio": ...,
        ...
      },
      "face_shape": "oval",
      "debug": { ... }
    }
  }
  ```

- **Error response:**
  ```json
  { "success": false, "error": "..." }
  ```

### POST `/landmarks/credit-card`

- **Body:** `multipart/form-data`
  - `file` (required): image file (with credit card for scale)

- **Success response:**
  ```json
  { "success": true, "landmarks": { ... } }
  ```

---

## Virtual Try-On (`/virtual-tryon`)

| Method | Path | Description |
|--------|------|-------------|
| **GET** | `/virtual-tryon/session` | Get session details by guest_id and session_id. |
| **POST** | `/virtual-tryon/select-frame` | Save selected frame and compute fitting height. |
| **POST** | `/virtual-tryon/gemini-analyze` | Analyze face for VTO using Gemini. |

### GET `/virtual-tryon/session`

- **Query params:**
  - `guest_id` (required)
  - `session_id` (required)

- **Success response:**
  ```json
  { "success": true, "data": { ... } }
  ```

- **Error response:**
  ```json
  { "success": false, "error": "Session not found" }
  ```

### POST `/virtual-tryon/select-frame`

- **Body:** `multipart/form-data`
  - `guest_id` (required)
  - `session_id` (required)
  - `frame_id` (required) — SKU ID
  - `frame_name` (required)
  - `dimensions` (required) — e.g. `"51-18-142-41"`
  - `selected_frame_image` (required): image file

- **Success response:**
  ```json
  {
    "success": true,
    "frame_image": "<signed_url>",
    "fitting_height": ...
  }
  ```

### POST `/virtual-tryon/gemini-analyze`

- **Body:** `multipart/form-data`
  - `file` (required): face image

- **Success response:**
  ```json
  { "success": true, "analysis": { ... } }
  ```

---

## OpenAPI / Swagger

- **Swagger UI:** http://localhost:8000/docs  
- **ReDoc:** http://localhost:8000/redoc  
- **OpenAPI JSON:** http://localhost:8000/openapi.json  
