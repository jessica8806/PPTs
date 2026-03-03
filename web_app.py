"""
AI Presentation Generator — Web UI

Run:
  python web_app.py

Then open http://<your-local-ip>:5000 on your phone.
"""

import os
import uuid
import json
import tempfile
from pathlib import Path

from flask import (
    Flask, request, jsonify, send_file, render_template, abort
)

from src.brand_extractor import BrandExtractor
from src.profile_manager import ProfileManager
from src.content_input import ContentInputProcessor, DeckSpec
from src.slide_generator import SlideGenerator
from src.brand_profile import BrandProfile

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB upload limit

UPLOAD_DIR = Path(tempfile.gettempdir()) / "ppt_gen_uploads"
OUTPUT_DIR = Path(tempfile.gettempdir()) / "ppt_gen_outputs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_BRAND = {".pdf", ".pptx", ".png", ".jpg", ".jpeg", ".webp", ".svg"}
ALLOWED_CONTENT = {".pdf", ".docx", ".md", ".txt", ".csv", ".xlsx"}


def _api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    return key


def _save_upload(file) -> Path:
    ext = Path(file.filename).suffix.lower()
    dest = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
    file.save(dest)
    return dest


# ------------------------------------------------------------------
# Pages
# ------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------------------------------------------
# Brand profile API
# ------------------------------------------------------------------

@app.route("/api/profiles", methods=["GET"])
def list_profiles():
    mgr = ProfileManager()
    profiles = mgr.list_profiles()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "primary_color": p.colors.primary.hex if p.colors.primary else None,
            "heading_font": p.typography.heading_font.name if p.typography.heading_font else None,
            "sources": p.source_materials,
            "review_flags": p.review_flags,
            "updated_at": p.updated_at[:10],
        }
        for p in profiles
    ])


@app.route("/api/profiles/<profile_id>", methods=["GET"])
def get_profile(profile_id):
    mgr = ProfileManager()
    try:
        p = mgr.get(profile_id)
        return jsonify(p.to_dict())
    except FileNotFoundError:
        abort(404, "Profile not found")


@app.route("/api/profiles/<profile_id>", methods=["DELETE"])
def archive_profile(profile_id):
    mgr = ProfileManager()
    try:
        mgr.archive(profile_id)
        return jsonify({"ok": True})
    except FileNotFoundError:
        abort(404, "Profile not found")


@app.route("/api/profiles/extract", methods=["POST"])
def extract_profile():
    """
    multipart/form-data:
      file   — brand reference file (optional)
      url    — website URL (optional, if no file)
      name   — brand name
    """
    if not _api_key():
        return jsonify({"error": "ANTHROPIC_API_KEY not set on server"}), 500

    brand_name = request.form.get("name", "Brand")
    url = request.form.get("url", "").strip()
    extractor = BrandExtractor(api_key=_api_key())
    mgr = ProfileManager()

    try:
        if "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            ext = Path(f.filename).suffix.lower()
            if ext not in ALLOWED_BRAND:
                return jsonify({"error": f"Unsupported file type: {ext}"}), 400
            path = _save_upload(f)

            if ext == ".pdf":
                profile = extractor.from_pdf(str(path), brand_name=brand_name)
            elif ext == ".pptx":
                profile = extractor.from_presentation(str(path), brand_name=brand_name)
            elif ext == ".svg":
                profile = extractor.from_logo(str(path), brand_name=brand_name)
            else:
                # image / logo
                profile = extractor.from_image(str(path), brand_name=brand_name,
                                               source_type="screenshot")
        elif url:
            profile = extractor.from_website(url, brand_name=brand_name)
        else:
            return jsonify({"error": "Provide a file or URL"}), 400

        mgr.save(profile)
        return jsonify({
            "id": profile.id,
            "name": profile.name,
            "primary_color": profile.colors.primary.hex if profile.colors.primary else None,
            "heading_font": (profile.typography.heading_font.name
                             if profile.typography.heading_font else None),
            "review_flags": profile.review_flags,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/profiles/manual", methods=["POST"])
def create_manual_profile():
    data = request.get_json(force=True)
    brand_name = data.pop("name", "Brand")
    extractor = BrandExtractor(api_key=_api_key())
    mgr = ProfileManager()
    profile = extractor.from_manual(data, brand_name=brand_name)
    mgr.save(profile)
    return jsonify({"id": profile.id, "name": profile.name})


# ------------------------------------------------------------------
# Generation API
# ------------------------------------------------------------------

@app.route("/api/generate", methods=["POST"])
def generate_deck():
    """
    multipart/form-data OR application/json:
      profile_id   — required
      text         — inline content (optional)
      file         — content file (optional)
      url          — content URL (optional)
      purpose      — General | Pitch | Report | …
      audience     — string
      target_slides — integer or blank
      density      — Low | Medium | High
      no_notes     — true/false
      language     — English
      title        — deck title override
    """
    if not _api_key():
        return jsonify({"error": "ANTHROPIC_API_KEY not set on server"}), 500

    # Support both form and JSON body
    if request.content_type and "application/json" in request.content_type:
        form = request.get_json(force=True)
        files = {}
    else:
        form = request.form
        files = request.files

    profile_id = form.get("profile_id", "")
    if not profile_id:
        return jsonify({"error": "profile_id is required"}), 400

    mgr = ProfileManager()
    try:
        profile = mgr.get(profile_id)
    except FileNotFoundError:
        return jsonify({"error": "Profile not found"}), 404

    params = {
        "purpose": form.get("purpose", "General"),
        "audience": form.get("audience", "General"),
        "content_density": form.get("density", "Medium"),
        "include_speaker_notes": form.get("no_notes", "false").lower() != "true",
        "language": form.get("language", "English"),
        "title": form.get("title", ""),
    }
    raw_slides = form.get("target_slides", "")
    if raw_slides.isdigit():
        params["target_slide_count"] = int(raw_slides)
    else:
        params["target_slide_count"] = "Auto"

    processor = ContentInputProcessor(api_key=_api_key())

    try:
        inline_text = form.get("text", "").strip()
        url = form.get("url", "").strip()

        if "file" in files and files["file"].filename:
            f = files["file"]
            ext = Path(f.filename).suffix.lower()
            if ext not in ALLOWED_CONTENT:
                return jsonify({"error": f"Unsupported content file type: {ext}"}), 400
            path = _save_upload(f)
            if ext in (".csv", ".xlsx"):
                deck = processor.from_csv(str(path), params)
            else:
                deck = processor.from_document(str(path), params)
        elif url:
            deck = processor.from_url(url, params)
        elif inline_text:
            # Detect outline vs freeform
            if inline_text.strip().startswith("#"):
                deck = processor.from_outline(inline_text, params)
            else:
                deck = processor.from_freeform(inline_text, params)
        else:
            return jsonify({"error": "Provide text, file, or url"}), 400

        gen = SlideGenerator(profile)
        out_name = f"{uuid.uuid4()}.pptx"
        out_path = OUTPUT_DIR / out_name
        gen.generate(deck, str(out_path))

        return jsonify({
            "download_url": f"/api/download/{out_name}",
            "slide_count": len(deck.slides),
            "title": deck.title,
            "filename": f"{deck.title.replace(' ', '_')}.pptx",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download/<filename>")
def download_file(filename):
    # Sanitise: only allow uuid-named .pptx files
    if not filename.endswith(".pptx") or "/" in filename or ".." in filename:
        abort(400)
    path = OUTPUT_DIR / filename
    if not path.exists():
        abort(404)
    return send_file(
        path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


if __name__ == "__main__":
    import socket
    # Print local IP so user knows what to open on phone
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"
    print(f"\n  Open on your phone: http://{local_ip}:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
