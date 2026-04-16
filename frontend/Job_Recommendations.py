import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000/api"

st.set_page_config(page_title="Career Assistant", layout="wide")

st.title("JobEra: Your AI Career Assistant")
st.caption("Upload your resume and discover your best career paths")

# -------------------------------
# Upload Resume
# -------------------------------
st.markdown("## Upload Resume")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    if st.button(" Analyze Resume"):
        with st.spinner("Analyzing your resume..."):

            files = {"resume": uploaded_file}

            response = requests.post(
                f"{BACKEND_URL}/recommend",
                files=files
            )

            if response.status_code == 200:
                jobs = response.json()
                st.session_state["jobs"] = jobs
                st.success("Analysis complete ")
            else:
                st.error("Something went wrong")

# -------------------------------
# Show Jobs (CARD UI)
# -------------------------------
if "jobs" in st.session_state:
    st.markdown("##  Recommended Roles")

    cols = st.columns(2)

    for idx, job in enumerate(st.session_state["jobs"]):
        with cols[idx % 2]:
            st.markdown(f"""
            <div style="
                padding:20px;
                border-radius:15px;
                background-color:#000000;
                margin-bottom:15px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            ">
                <h3 style="color:#4CAF50;">{job['title']}</h3>
                <p><b>Match Score:</b> {job['match_score']}</p>
                <p><b>Skills:</b> {', '.join(job['matched_skills'])}</p>
            </div>
            """, unsafe_allow_html=True)

            # Button to go to skill gap page
            if st.button(f"Check Skill Gap → {job['title']}", key=job["title"]):
                st.session_state["selected_job"] = job
                st.switch_page("pages/1_Skill_Gap.py")