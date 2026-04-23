from dotenv import load_dotenv
import os
import json
import requests
from pathlib import Path

print("THIS IS THE FILE BEING EXECUTED")

# ✅ Load .env safely
env_path = Path(__file__).parent / ".env"
os.environ.pop("OPENROUTER_API_KEY", None)
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("OPENROUTER_API_KEY")

print("📂 ENV PATH:", env_path)
print("🔑 API KEY:", api_key)

if not api_key:
    raise ValueError("API key not found. Fix .env path or content.")


def get_course_suggestions(skill_gap_data):
    
    # ✅ FIXED KEYS (match frontend)
    missing_required = skill_gap_data.get("missing_required", [])
    missing_preferred = skill_gap_data.get("missing_preferred", [])
    role = skill_gap_data.get("role", "role")
    user_skills = skill_gap_data.get("user_skills", [])

    prompt = f"""
    You are an expert AI career mentor.

    Target Role: {role}

    User Skills: {user_skills}
    Missing Required Skills: {missing_required}
    Missing Preferred Skills: {missing_preferred}

    Return ONLY valid JSON.

    FORMAT:
    {{
      "courses": [
        {{
          "course_name": "",
          "platform": "",
          "skill_covered": "",
          "link": ""
        }}
      ],
      "projects": [
        {{
          "project_name": "",
          "description": "",
          "link": ""
        }}
      ],
      "roadmap": [
        {{
          "step": 1,
          "description": ""
        }}
      ],
      "internships": [
        {{
          "title": "",
          "platform": "",
          "link": ""
        }}
      ]
    }}

    Rules:
    - Give 3–5 courses
    - Give 2–3 projects
    - Roadmap must be step-by-step
    - Keep response clean JSON only
    """

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        # ✅ FREE MODEL
        "model": "openai/gpt-4o-mini",
        # "model": "meta-llama/llama-3-70b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            raise ValueError(response.text)

        result = response.json()
        raw_text = result["choices"][0]["message"]["content"].strip()

        # Clean markdown
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(raw_text)

        # ✅ SAFE DEFAULTS (important for UI)
        return {
            "courses": parsed.get("courses", []),
            "projects": parsed.get("projects", []),
            "roadmap": parsed.get("roadmap", []),
            "internships": parsed.get("internships", [])
        }

    except Exception as e:
        print("🔥 ERROR:", str(e))

        return {
            "courses": [],
            "projects": [],
            "roadmap": [],
            "internships": [],
            "error": str(e)
        }


# 🔹 TEST
if __name__ == "__main__":
    test_data = {
        "role": "Data Scientist",
        "user_skills": ["Python"],
        "missing_required_skills": ["Machine Learning", "Deep Learning"],
        "missing_preferred_skills": ["NLP"]
    }

    result = get_course_suggestions(test_data)

    print("\n📊 FINAL OUTPUT:\n", json.dumps(result, indent=2))