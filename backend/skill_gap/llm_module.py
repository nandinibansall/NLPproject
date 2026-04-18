from dotenv import load_dotenv
import os
import json
import requests
from pathlib import Path

print("THIS IS THE FILE BEING EXECUTED")

# ✅ Load .env safely (no stale key issue)
env_path = Path(__file__).parent / ".env"
os.environ.pop("OPENROUTER_API_KEY", None)
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("OPENROUTER_API_KEY")

print("📂 ENV PATH:", env_path)
print("🔑 API KEY:", api_key)

if not api_key:
    raise ValueError("API key not found. Fix .env path or content.")


def get_course_suggestions(skill_gap_data):

    missing_required = skill_gap_data.get("missing_required_skills", [])
    missing_preferred = skill_gap_data.get("missing_preferred_skills", [])
    role = skill_gap_data.get("role", "role")

    prompt = f"""
    You are a career assistant.

    Role: {role}
    Missing Required Skills: {missing_required}
    Missing Preferred Skills: {missing_preferred}

    Suggest:
    - 3 to 5 courses
    - A clear roadmap

    STRICT RULES:
    - Return ONLY valid JSON
    - DO NOT wrap response in ```json
    - DO NOT include backticks
    - No explanation text

    FORMAT:
    {{
      "courses": [
        {{
          "course_name": "...",
          "platform": "...",
          "skill_covered": "...",
          "link": "https://..."
        }}
      ],
      "roadmap": [
        "Step 1 ...",
        "Step 2 ..."
      ]
    }}
    """

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Career Assistant App",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openrouter/auto",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        print("🚀 Sending request...")

        response = requests.post(url, headers=headers, json=data)

        print("🧪 STATUS CODE:", response.status_code)
        print("🧾 RAW RESPONSE:", response.text[:500])

        if response.status_code != 200:
            raise ValueError(f"API Error: {response.text}")

        result = response.json()

        raw_text = result["choices"][0]["message"]["content"].strip()

        print("🧾 LLM OUTPUT:\n", raw_text)

        # ✅ Remove markdown if model still sends it
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        # ✅ Parse JSON cleanly
        parsed = json.loads(raw_text)
        print("✅ JSON parsed successfully")

        # ✅ Ensure link exists (frontend safety)
        for course in parsed.get("courses", []):
            if "link" not in course:
                course["link"] = "#"

        # ✅ Validate structure
        if "courses" not in parsed or "roadmap" not in parsed:
            raise ValueError("Invalid response structure from LLM")

        return parsed

    except Exception as e:
        print("🔥 ERROR:", str(e))


# 🔹 TEST
if __name__ == "__main__":
    test_data = {
        "role": "Data Scientist",
        "missing_required_skills": ["Machine Learning", "Deep Learning"],
        "missing_preferred_skills": ["NLP"]
    }

    result = get_course_suggestions(test_data)

    print("\n📊 FINAL OUTPUT:\n", json.dumps(result, indent=2))