import os
import sys

from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the workspace root is on sys.path when running this file directly.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.jobReccomendations.pdf_extractor import extract_text_from_pdf
from backend.jobReccomendations.preprocessor import extract_features
from backend.jobReccomendations.recommender import JOB_PROFILES, recommend_jobs
from backend.skill_gap.skill_gap import get_skill_gap
from backend.skill_gap.llm_module import get_course_suggestions

ALLOWED_EXTENSION = "pdf"
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    @app.route("/api/health", methods=["GET"])
    def health() -> tuple[dict, int]:
        return {"status": "ok", "service": "Career Assistant API"}, 200

    @app.route("/api/recommend", methods=["POST"])
    def recommend() -> tuple[dict, int]:
        if "resume" not in request.files:
            return {"error": "No file provided. Send the PDF under the key 'resume'."}, 400

        file = request.files["resume"]
        if file.filename == "":
            return {"error": "Empty filename."}, 400

        if not _allowed_file(file.filename):
            return {"error": "Only PDF files are accepted."}, 400

        try:
            top_n = int(request.args.get("top_n", 5))
            top_n = max(1, min(top_n, 10))
        except ValueError:
            top_n = 5

        try:
            raw_text = extract_text_from_pdf(file.read())
            features = extract_features(raw_text)
            recommendations = recommend_jobs(features, top_n=top_n)
        except ValueError as ve:
            return {"error": str(ve)}, 422
        except Exception as exc:
            return {"error": f"Internal processing error: {str(exc)}"}, 500

        response = [
            {
                "title": item["title"],
                "match_score": item["match_score"],
                "matched_skills": item["matched_skills"],
                "required_domains_matched": item["required_domains_matched"],
                "preferred_domains_matched": item["preferred_domains_matched"],
            }
            for item in recommendations
        ]
        return jsonify(response), 200

    @app.route("/api/skill-gap", methods=["POST"])
    def skill_gap() -> tuple[dict, int]:
        payload = request.get_json(silent=True)
        if not payload:
            return {"error": "Invalid JSON payload."}, 400

        role = payload.get("role")
        user_skills = payload.get("skills")

        if not role or not isinstance(role, str):
            return {"error": "Role must be provided as a string in the JSON payload."}, 400
        if not isinstance(user_skills, list):
            return {"error": "Skills must be provided as a list of strings in the JSON payload."}, 400

        # 🔹 Existing skill gap logic
        result = get_skill_gap(role, [str(skill) for skill in user_skills])

        # 🔥 NEW: Add LLM course suggestions
        # 🔥 NEW: Add LLM course suggestions
        try:
            courses_data = get_course_suggestions(result)

            # ✅ FIX: match frontend structure
            result["courses"] = courses_data.get("courses", [])
            result["roadmap"] = courses_data.get("roadmap", [])

        except Exception as e:
            result["courses"] = []
            result["roadmap"] = []
            result["error"] = str(e)

        status_code = 200 if "error" not in result else 404
        return jsonify(result), status_code
    @app.route("/api/job-roles", methods=["GET"])
    def job_roles() -> tuple[dict, int]:
        return jsonify(
            [
                {
                    "title": job["title"],
                    "required_domains": job["required_domains"],
                    "preferred_domains": job.get("preferred_domains", []),
                }
                for job in JOB_PROFILES
            ]
        ), 200

    return app


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() == ALLOWED_EXTENSION


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
