
from openai import OpenAI
import os

print("THIS IS THE FILE BEING EXECUTED")

# Create OpenRouter client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def get_course_suggestions(skill_gap_data):

    missing_required = skill_gap_data.get("missing_required_skills", [])
    missing_preferred = skill_gap_data.get("missing_preferred_skills", [])
    role = skill_gap_data.get("role", "role")

    prompt = f"""
    The user wants to become a {role}.

    Missing Required Skills: {missing_required}
    Missing Preferred Skills: {missing_preferred}

    Suggest:
    1. Best courses (with platform names)
    2. Simple step-by-step roadmap

    Format:
    - Courses list
    - Roadmap steps
    """

    # ✅ FIXED MODEL (guaranteed working)
    model_name = "openai/gpt-4o-mini"
    print("MODEL USED:", model_name)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    test_data = {
        "role": "Data Scientist",
        "missing_required_skills": ["Machine Learning", "Deep Learning"],
        "missing_preferred_skills": ["NLP"]
    }

    result = get_course_suggestions(test_data)
    print("\nLLM OUTPUT:\n", result)