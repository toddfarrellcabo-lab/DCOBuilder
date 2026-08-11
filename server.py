from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from werkzeug.utils import secure_filename
import re

ROOT = Path(__file__).resolve().parent
UPLOADS = ROOT / "uploads"
UPLOADS.mkdir(exist_ok=True)

ALLOWED = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")

def safe_upload_name(filename: str) -> str:
    original = secure_filename(filename or "")
    stem = Path(original).stem
    ext = Path(original).suffix.lower()

    if ext not in ALLOWED:
        raise ValueError("Only PNG, JPG, JPEG, GIF, and WEBP images are allowed.")

    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_") or "image"
    candidate = f"{stem}{ext}"
    path = UPLOADS / candidate

    counter = 2
    while path.exists():
        candidate = f"{stem}_{counter:02d}{ext}"
        path = UPLOADS / candidate
        counter += 1

    return candidate

@app.post("/api/upload")
def upload_image():
    if "image" not in request.files:
        return jsonify(error="No image file was provided."), 400

    file = request.files["image"]
    if not file or not file.filename:
        return jsonify(error="No image file was selected."), 400

    try:
        filename = safe_upload_name(file.filename)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    file.save(UPLOADS / filename)
    return jsonify(path=f"uploads/{filename}", filename=filename)

@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")

@app.get("/<path:path>")
def static_files(path):
    return send_from_directory(ROOT, path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
