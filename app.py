# app.py
import io
from typing import List, Dict, Any

import streamlit as st
from docx import Document
from groq import Groq
import json
import os

from generator import generate_lesson_plans_from_pdf
from config import (
    DEFAULT_DOMAINS,
    DEFAULT_CURRICULAR_GOALS,
    DEFAULT_COMPETENCIES,
)

# -------------------------------
# LLM SETUP (AUTO TOPIC INFERENCE)
# -------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-safeguard-20b")


def infer_topics_from_text(text: str) -> List[str]:
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are a curriculum expert.

Given a chapter, divide it into 45–50 minute lesson-sized TOPICS.
Return ONLY a JSON array of strings.
No explanations. No markdown.

Chapter Text:
\"\"\"
{text[:12000]}
\"\"\"
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()

    if not raw:
        raise ValueError("LLM returned empty response while inferring topics.")

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: extract JSON array from text
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1:
            raise ValueError(f"Invalid topic inference output:\n{raw}")
        return json.loads(raw[start:end + 1])



# -------------------------------
# PAGE CONFIG & STYLES (UNCHANGED)
# -------------------------------
st.set_page_config(
    page_title="Lesson Plan Generator",
    page_icon="📘",
    layout="centered",
)

# (YOUR EXISTING CSS BLOCK IS UNCHANGED — OMITTED HERE FOR BREVITY)
# -------------------------------

st.title("📘 Lesson Plan Generator")

# ---------------------------------------
# SIDEBAR
# ---------------------------------------
with st.sidebar:
    st.header("Configuration")

    grade = st.text_input("Grade", "")
    chapter_name = st.text_input("Chapter Name", "")
    page_no = st.text_input("Page No / Range", "")

    num_lessons_option = st.selectbox(
        "Number of Lesson Plans",
        ["Auto-decide (4–6)", "3", "4", "5", "6"],
    )

    override_num_lessons = (
        int(num_lessons_option)
        if num_lessons_option != "Auto-decide (4–6)"
        else None
    )

    st.markdown("---")

    # ---------- TOPICS ----------
    st.subheader("Topic Names")

    topic_names = []

    if override_num_lessons is not None:
        # MANUAL MODE (UNCHANGED)
        for i in range(override_num_lessons):
            topic = st.text_input(f"Topic for Lesson {i + 1}", key=f"topic_{i}")
            topic_names.append(topic.strip())
    else:
        st.info("Topics will be generated automatically.")

    st.markdown("---")

    # ---------- SECTION TOGGLES ----------
    st.subheader("Include Sections")

    include_domains = st.checkbox("Domains", value=True)
    domains = None
    if include_domains:
        domains_text = st.text_area(
            "Domains (one per line)",
            value="\n".join(DEFAULT_DOMAINS),
            height=80,
        )
        domains = [d.strip() for d in domains_text.split("\n") if d.strip()]

    include_curricular = st.checkbox("Curricular Goals", value=True)
    curricular_goals = None
    if include_curricular:
        curricular_goals_text = st.text_area(
            "Curricular Goals (one per line)",
            value="\n".join(DEFAULT_CURRICULAR_GOALS),
            height=80,
        )
        curricular_goals = [c.strip() for c in curricular_goals_text.split("\n") if c.strip()]

    include_competencies = st.checkbox("Competencies", value=True)
    competencies = None
    if include_competencies:
        competencies_text = st.text_area(
            "Competencies (one per line)",
            value="\n".join(DEFAULT_COMPETENCIES),
            height=80,
        )
        competencies = [c.strip() for c in competencies_text.split("\n") if c.strip()]

    include_learning_outcomes = st.checkbox("Learning Outcomes", value=True)
    include_teaching_aids = st.checkbox("Teaching Aids", value=True)
    include_strategy = st.checkbox("Strategy / Pedagogy", value=True)
    include_interdisciplinary = st.checkbox("Interdisciplinary Approach", value=True)
    include_extended = st.checkbox("Extended Learning Assignment", value=True)

    # ---------- CUSTOM SECTIONS ----------
    st.markdown("---")
    st.subheader("Additional Custom Sections")

    if "extra_sections" not in st.session_state:
        st.session_state.extra_sections = []

    if st.button("+ Add Section"):
        st.session_state.extra_sections.append({"title": "", "content": ""})

    extra_sections = []
    for idx, sec in enumerate(st.session_state.extra_sections):
        with st.expander(f"Custom Section {idx + 1}", expanded=True):
            title = st.text_input("Section Title", value=sec["title"], key=f"extra_title_{idx}")
            content = st.text_area("Section Content", value=sec["content"], height=80, key=f"extra_content_{idx}")
            if title.strip():
                extra_sections.append({"title": title.strip(), "content": content.strip()})

# ---------------------------------------
# MAIN
# ---------------------------------------
uploaded_file = st.file_uploader("Upload chapter/poem PDF", type=["pdf"])

if uploaded_file and st.button("Generate Lesson Plans"):

    file_bytes = uploaded_file.read()
    raw_text = file_bytes.decode(errors="ignore")

    # ---------- AUTO MODE ----------
    if override_num_lessons is None:
        topic_names = infer_topics_from_text(raw_text)
        override_num_lessons = len(topic_names)

    # ---------- MANUAL VALIDATION ----------
    if override_num_lessons is not None and any(not t for t in topic_names):
        st.error("All topic names are required.")
        st.stop()

    result = generate_lesson_plans_from_pdf(
        file_bytes=file_bytes,
        grade=grade,
        chapter_name=chapter_name,
        topic_names=topic_names,
        page_no=page_no,
        override_num_lessons=override_num_lessons,
        domains=domains,
        curricular_goals=curricular_goals,
        competencies=competencies,
        extra_sections=extra_sections,
        include_learning_outcomes=include_learning_outcomes,
        include_teaching_aids=include_teaching_aids,
        include_strategy=include_strategy,
        include_interdisciplinary=include_interdisciplinary,
        include_extended=include_extended
    )


    st.session_state["lesson_plan_result"] = result
    
    st.write("DEBUG result:", result)

# ---------------------------------------
# DISPLAY (UNCHANGED)
# ---------------------------------------
    if not st.session_state["lesson_plan_result"]["lesson_plans"]:
        st.warning("No lesson plans were generated. Try refining topics or using manual mode.")

if "lesson_plan_result" in st.session_state:
    for lp in st.session_state["lesson_plan_result"]["lesson_plans"]:
        with st.expander(f"Lesson Plan {lp['lesson_plan_no']}"):
            for k, v in lp.items():
                st.markdown(f"**{k.replace('_',' ').title()}:**")
                if isinstance(v, list):
                    for i in v:
                        st.markdown(f"- {i}")
                else:
                    st.write(v)
