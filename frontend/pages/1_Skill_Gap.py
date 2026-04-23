import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000/api"

st.set_page_config(page_title="Skill Gap", layout="wide")

st.title(" Skill Gap Analysis")

# -------------------------------
# Check if job selected
# -------------------------------
if "selected_job" not in st.session_state:
    st.warning(" No job selected. Go back and choose a role.")
    if st.button(" Go Back"):
        st.switch_page("Job_Recommendations.py")
    st.stop()

job = st.session_state["selected_job"]

#  Reset skill gap if job changes
if "last_job" not in st.session_state or st.session_state["last_job"] != job["title"]:
    st.session_state.pop("skill_gap", None)
    st.session_state["last_job"] = job["title"]

# -------------------------------
# Job Info
# -------------------------------
st.markdown(f"## {job['title']}")

# Match Score
st.info(f" Match Score: {job['match_score']}")

# Skills (better UI)
st.markdown("##### Your Skills")
st.write(", ".join(job["matched_skills"]))

# -------------------------------
# Analyze Button
# -------------------------------
if st.button(" Analyze Skill Gap", use_container_width=True):
    with st.spinner("Analyzing skill gap..."):

        response = requests.post(
            f"{BACKEND_URL}/skill-gap",
            json={
                "role": job["title"],
                "skills": job["matched_skills"]
            }
        )

        if response.status_code == 200:
            st.session_state["skill_gap"] = response.json()
        else:
            st.error(" Error fetching skill gap")

# -------------------------------
# Show Results
# -------------------------------
# -------------------------------
# Show Results
# -------------------------------
if "skill_gap" in st.session_state:
    data = st.session_state["skill_gap"]

    st.markdown("## Results")

    # Progress
    st.progress(int(data["match_percentage"]))
    st.write(f"**{data['match_percentage']}% match**")

    col1, col2 = st.columns(2)

    # -------------------------------
    # Missing Required Skills
    # -------------------------------
    with col1:
        st.markdown("### Missing Required Skills")

        if data["missing_required_skills"]:
            for skill in data["missing_required_skills"]:
                st.markdown(f"- **{skill}**")
        else:
            st.success("No missing required skills 🎉")

    # -------------------------------
    # Missing Preferred Skills
    # -------------------------------
    with col2:
        st.markdown("### Missing Preferred Skills")

        if data["missing_preferred_skills"]:
            for skill in data["missing_preferred_skills"]:
                st.markdown(f"- **{skill}**")
        else:
            st.success("You're doing great here too 🎉")

    # -------------------------------
    # Courses (UPDATED)
    # -------------------------------
    if "courses" in data:
        st.markdown("## Recommended Courses")

        for course in data["courses"]:
            link = course.get("link", "#")

            link_html = (
                f'<a href="{link}" target="_blank">🔗 Open Course</a>'
                if link != "#"
                else '<p style="color:gray;">No link available</p>'
            )

            st.markdown(f"""
            <div style="
                padding:15px;
                border-radius:12px;
                background-color:#1e1e2f;
                margin-bottom:12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            ">
                <h4 style="color:#4CAF50;">{course['course_name']}</h4>
                <p><b>Platform:</b> {course['platform']}</p>
                <p><b>Skill Covered:</b> {course['skill_covered']}</p>
                {link_html}
            </div>
            """, unsafe_allow_html=True)

        # -------------------------------
        # Roadmap (FIXED)
        # -------------------------------
        if data.get("roadmap"):
            st.markdown("## Learning Roadmap")

            for step in data["roadmap"]:
                st.markdown(f"**Step {step.get('step', '')}:** {step.get('description', '')}")

# -------------------------------
# Back Button
# -------------------------------
st.markdown("---")
if st.button("Back to Jobs", use_container_width=True):
    st.switch_page("Job_Recommendations.py")