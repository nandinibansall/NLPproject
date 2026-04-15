
from flask import Blueprint, request, jsonify
from pdf_extractor import extract_text_from_pdf
from preprocessor import extract_features
from recommender import recommend_jobs

api_bp = Blueprint("api", __name__)

ALLOWED_EXTENSION = "pdf"


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() == ALLOWED_EXTENSION


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Job Recommender API"})


@api_bp.route("/recommend", methods=["POST"])
def recommend():
    if "resume" not in request.files:
        return jsonify({"error": "No file provided. Send the PDF under the key 'resume'."}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are accepted."}), 400

    try:
        top_n = int(request.args.get("top_n", 5))
        top_n = max(1, min(top_n, 10))
    except ValueError:
        top_n = 5

    try:
        file_bytes = file.read()
        raw_text = extract_text_from_pdf(file_bytes)
        features = extract_features(raw_text)
        recommendations = recommend_jobs(features, top_n=top_n)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 422
    except Exception as e:
        return jsonify({"error": f"Internal processing error: {str(e)}"}), 500


    filtered = [
    {
        "title": r["title"],
        "match_score": r["match_score"]
    }
    for r in recommendations
]

    return jsonify(filtered), 200
