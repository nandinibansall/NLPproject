"""
tests/test_pipeline.py
-----------------------
Unit tests for preprocessor and recommender modules.
Run with: python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.preprocessor import clean_text, extract_features
from app.recommender import recommend_jobs


# ── Fixtures ───────────────────────────────────────────────────────────────────

SAMPLE_DS_RESUME = """
Jane Doe | Data Scientist
B.S. in Computer Science, University of Delhi, 2021

Skills:
Python, Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, SQL, 
Matplotlib, Seaborn, Machine Learning, Deep Learning, NLP,
Statistical Analysis, Hypothesis Testing

Experience (2 years):
- Built classification and regression models using scikit-learn
- Designed NLP pipeline for sentiment analysis using BERT (HuggingFace)
- Automated ETL pipelines with Apache Airflow and SQL

Education:
Bachelor of Science in Computer Science
"""

SAMPLE_WEB_RESUME = """
Alex Smith | Full Stack Developer
Bachelor of Engineering, 2020

Experience: 3 years

Technologies:
JavaScript, React, Node.js, Express, HTML, CSS, TypeScript,
MongoDB, PostgreSQL, REST API, Docker, Git, AWS, Agile, Scrum, Jira
"""

SAMPLE_SECURITY_RESUME = """
Bob Martin | Cybersecurity Analyst
Bachelor's Degree in Information Security

Skills:
Penetration Testing, Ethical Hacking, Metasploit, Burp Suite, Nmap, Wireshark,
OWASP, SIEM, Splunk, Network Security, Firewall, IDS, IPS,
Linux, Bash scripting, Python, CEH, OSCP
"""


# ── Tests: Preprocessor ────────────────────────────────────────────────────────

class TestCleanText:
    def test_lowercase(self):
        assert clean_text("PYTHON Django") == "python django"

    def test_removes_punctuation(self):
        result = clean_text("hello, world! test.")
        assert "," not in result
        assert "!" not in result

    def test_collapses_whitespace(self):
        result = clean_text("a  b   c")
        assert "  " not in result


class TestExtractFeatures:
    def test_ds_resume_detects_python(self):
        features = extract_features(SAMPLE_DS_RESUME)
        assert "python" in features["skill_domains"]

    def test_ds_resume_detects_ml(self):
        features = extract_features(SAMPLE_DS_RESUME)
        assert "machine_learning" in features["skill_domains"]

    def test_ds_resume_detects_education(self):
        features = extract_features(SAMPLE_DS_RESUME)
        assert features["education_level"] == "bachelors"

    def test_web_resume_detects_javascript(self):
        features = extract_features(SAMPLE_WEB_RESUME)
        assert "javascript" in features["skill_domains"]

    def test_web_resume_detects_experience(self):
        features = extract_features(SAMPLE_WEB_RESUME)
        assert features["years_experience"] == 3

    def test_security_resume_detects_security(self):
        features = extract_features(SAMPLE_SECURITY_RESUME)
        assert "security" in features["skill_domains"]

    def test_tokens_not_empty(self):
        features = extract_features(SAMPLE_DS_RESUME)
        assert len(features["tokens"]) > 10

    def test_skills_dict_structure(self):
        features = extract_features(SAMPLE_DS_RESUME)
        assert isinstance(features["skills"], dict)
        for domain, kws in features["skills"].items():
            assert isinstance(kws, list)
            assert len(kws) > 0


# ── Tests: Recommender ─────────────────────────────────────────────────────────

class TestRecommender:
    def test_returns_list(self):
        features = extract_features(SAMPLE_DS_RESUME)
        recs = recommend_jobs(features, top_n=5)
        assert isinstance(recs, list)
        assert len(recs) == 5

    def test_recommendation_structure(self):
        features = extract_features(SAMPLE_DS_RESUME)
        recs = recommend_jobs(features, top_n=3)
        for rec in recs:
            assert "title" in rec
            assert "match_score" in rec
            assert "matched_skills" in rec
            assert "reasoning" in rec
            assert 0 <= rec["match_score"] <= 100

    def test_ds_resume_recommends_data_roles(self):
        features = extract_features(SAMPLE_DS_RESUME)
        recs = recommend_jobs(features, top_n=3)
        titles = [r["title"] for r in recs]
        data_roles = {"Data Scientist", "Machine Learning Engineer", "NLP Engineer",
                      "Data Analyst", "Data Engineer", "AI Research Scientist"}
        assert any(t in data_roles for t in titles), f"Expected data roles, got: {titles}"

    def test_web_resume_recommends_web_roles(self):
        features = extract_features(SAMPLE_WEB_RESUME)
        recs = recommend_jobs(features, top_n=3)
        titles = [r["title"] for r in recs]
        web_roles = {"Full Stack Developer", "Backend Software Engineer",
                     "Frontend Developer", "DevOps / Cloud Engineer"}
        assert any(t in web_roles for t in titles), f"Expected web roles, got: {titles}"

    def test_security_resume_recommends_security_roles(self):
        features = extract_features(SAMPLE_SECURITY_RESUME)
        recs = recommend_jobs(features, top_n=3)
        titles = [r["title"] for r in recs]
        sec_roles = {"Cybersecurity Analyst", "Penetration Tester"}
        assert any(t in sec_roles for t in titles), f"Expected security roles, got: {titles}"

    def test_scores_sorted_descending(self):
        features = extract_features(SAMPLE_DS_RESUME)
        recs = recommend_jobs(features, top_n=5)
        scores = [r["match_score"] for r in recs]
        assert scores == sorted(scores, reverse=True)

    def test_top_n_respected(self):
        features = extract_features(SAMPLE_DS_RESUME)
        for n in [1, 3, 7]:
            recs = recommend_jobs(features, top_n=n)
            assert len(recs) == n


if __name__ == "__main__":
    import unittest

    # Quick manual run without pytest
    test_classes = [TestCleanText, TestExtractFeatures, TestRecommender]
    passed = failed = 0

    for cls in test_classes:
        instance = cls()
        for method in [m for m in dir(cls) if m.startswith("test_")]:
            try:
                getattr(instance, method)()
                print(f"  ✓ {cls.__name__}.{method}")
                passed += 1
            except AssertionError as e:
                print(f"  ✗ {cls.__name__}.{method}: {e}")
                failed += 1
            except Exception as e:
                print(f"  ✗ {cls.__name__}.{method}: {type(e).__name__}: {e}")
                failed += 1

    print(f"\n{passed} passed, {failed} failed")
