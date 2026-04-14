"""
routes.py
---------
Flask API endpoints.

POST /api/recommend
    Accepts: multipart/form-data with field "resume" (PDF file)
    Optional query param: top_n (default 5, max 10)
    Returns: JSON with job recommendations

GET /api/health
    Health check
"""

from flask import Blueprint, request, jsonify
from app.pdf_extractor import extract_text_from_pdf
from app.preprocessor import extract_features
from app.recommender import recommend_jobs

api_bp = Blueprint("api", __name__)

ALLOWED_EXTENSION = "pdf"


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() == ALLOWED_EXTENSION


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Job Recommender API"})


@api_bp.route("/recommend", methods=["POST"])
def recommend():
    # ── Validate file presence ─────────────────────────────────────────────
    if "resume" not in request.files:
        return jsonify({"error": "No file provided. Send the PDF under the key 'resume'."}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are accepted."}), 400

    # ── top_n param ────────────────────────────────────────────────────────
    try:
        top_n = int(request.args.get("top_n", 5))
        top_n = max(1, min(top_n, 10))  # clamp between 1 and 10
    except ValueError:
        top_n = 5

    # ── Pipeline ───────────────────────────────────────────────────────────
    try:
        file_bytes = file.read()
        raw_text = extract_text_from_pdf(file_bytes)
        features = extract_features(raw_text)
        recommendations = recommend_jobs(features, top_n=top_n)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 422
    except Exception as e:
        return jsonify({"error": f"Internal processing error: {str(e)}"}), 500

    # ── Response ───────────────────────────────────────────────────────────
    response = {
        "status": "success",
        "resume_summary": {
            "detected_education": features["education_level"],
            "detected_experience_years": features["years_experience"],
            "detected_skill_domains": features["skill_domains"],
        },
        "recommendations": recommendations,
    }
    return jsonify(response), 200
