import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000/api"

st.set_page_config(page_title="Skill Gap", layout="wide")

st.title(" Skill Gap Analysis")

# Check if job selected
if "selected_job" not in st.session_state:
    st.warning(" No job selected. Go back and choose a role.")
    if st.button(" Go Back"):
        st.switch_page("app.py")
    st.stop()

job = st.session_state["selected_job"]

st.markdown(f"## {job['title']}")

# Show job info
st.info(f"Match Score: {job['match_score']}")
st.write("**Your Skills:**", ", ".join(job["matched_skills"]))

# Button to fetch skill gap
if st.button("Analyze Skill Gap"):
    with st.spinner("Analyzing..."):

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
            st.error("Error fetching skill gap")

# Show results
if "skill_gap" in st.session_state:
    data = st.session_state["skill_gap"]

    st.markdown("##  Results")

    st.progress(int(data["match_percentage"]))
    st.write(f"{data['match_percentage']}% match")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("###  Missing Required Skills")
        if data["missing_required_skills"]:
            for skill in data["missing_required_skills"]:
                st.write(f" {skill}")
        else:
            st.success("No missing required skills ")

    with col2:
        st.markdown("###  Missing Preferred Skills")
        if data["missing_preferred_skills"]:
            for skill in data["missing_preferred_skills"]:
                st.write(f" {skill}")
        else:
            st.success("You're doing great here too ")

# Back button
if st.button(" Back to Jobs"):
    st.switch_page("Job_Recommendation.py")