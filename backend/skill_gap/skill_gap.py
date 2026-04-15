# Import JOB_PROFILES 
# Adjust path if needed based on actual structure
from backend.jobReccomendations.recommender import JOB_PROFILES
def get_role_data(role):
    """
    Finds the job profile dictionary for a given role
    """
    for job in JOB_PROFILES:
        if job["title"].lower() == role.lower():
            return job
    return None


def get_skill_gap(role, user_skills):
    """
    Computes missing skills for a selected role
    """

    job = get_role_data(role)

    if not job:
        return {
            "error": "Role not found"
        }

    # Extract required and preferred skills
    required_skills = job.get("required_domains", [])
    preferred_skills = job.get("preferred_domains", [])

    # Normalize
    user_skills = [skill.lower() for skill in user_skills]
    required_skills = [skill.lower() for skill in required_skills]
    preferred_skills = [skill.lower() for skill in preferred_skills]

    # Compute gaps
    missing_required = list(set(required_skills) - set(user_skills))
    missing_preferred = list(set(preferred_skills) - set(user_skills))

    # Optional: match percentage
    match_percentage = 0
    if required_skills:
        match_percentage = (
            len(set(user_skills).intersection(set(required_skills))) 
            / len(required_skills)
        ) * 100

    return {
        "role": role,
        "missing_required_skills": missing_required,
        "missing_preferred_skills": missing_preferred,
        "match_percentage": round(match_percentage, 2)
    }


# 🔹 Testing (you can run this file directly)
if __name__ == "__main__":
    test_role = "Frontend Developer"
    test_user_skills = []

    result = get_skill_gap(test_role, test_user_skills)
    print(result)