# app.py
import io
from typing import List, Dict, Any

import streamlit as st
from docx import Document

from generator import generate_lesson_plans_from_pdf
from config import (
    DEFAULT_DOMAINS,
    DEFAULT_CURRICULAR_GOALS,
    DEFAULT_COMPETENCIES,
)

st.set_page_config(
    page_title="Lesson Plan Generator",
    page_icon="📘",
    layout="centered",
)

st.markdown("""
<style>

/* ================================
   GLOBAL RESET & FONT
================================ */
html, body, [class*="css"] {
    font-family: "Inter", "Poppins", sans-serif;
}

body {
    background: radial-gradient(circle at top left, #1a1a2e, #0f0f1a);
    color: #eaeaf0;
}

/* ================================
   MAIN CONTAINER
================================ */
.main {
    padding: 2rem;
}

/* ================================
   HEADINGS
================================ */
h1 {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #9d4edd, #00f5d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

h2, h3 {
    color: #cdb4db;
    font-weight: 700;
}

/* ================================
   SIDEBAR (GLASS EFFECT)
================================ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    backdrop-filter: blur(18px);
    border-right: 1px solid rgba(255,255,255,0.1);
}

section[data-testid="stSidebar"] * {
    color: #1a1a1a !important;
}

/* ================================
   SIDEBAR INPUT VISIBILITY FIX
================================ */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] select {
    border: 1.5px solid rgba(157, 78, 221, 0.8) !important; /* neon purple */
    box-shadow: 0 0 6px rgba(157, 78, 221, 0.25);
}


/* ================================
   INPUTS (SOFT GLOW)
================================ */
input, textarea, select {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    padding: 0.6rem !important;
}

input:focus, textarea:focus {
    border: 1px solid #9d4edd !important;
    box-shadow: 0 0 0 2px rgba(157,78,221,0.35);
}

/* ================================
   CHECKBOXES (NEON)
================================ */
input[type="checkbox"] {
    accent-color: #00f5d4;
}

/* ================================
   BUTTONS (POP & GLOW)
================================ */
button {
    background: linear-gradient(135deg, #9d4edd, #00f5d4) !important;
    color: #0f0f1a !important;
    font-weight: 800 !important;
    border-radius: 16px !important;
    padding: 0.7rem 1.6rem !important;
    border: none !important;
    transition: all 0.25s ease;
    box-shadow: 0 0 18px rgba(157,78,221,0.45);
}

button:hover {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 0 28px rgba(0,245,212,0.6);
}

/* ================================
   EXPANDERS (GLASS CARDS)
================================ */
div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(20px);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
}

/* ================================
   FILE UPLOADER (NEON BORDER)
================================ */
div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.04);
    border-radius: 18px;
    border: 2px dashed #9d4edd;
    padding: 1.2rem;
}

/* ================================
   MARKDOWN SECTIONS
================================ */
.markdown-text-container {
    background: rgba(255,255,255,0.05);
    padding: 1rem;
    border-radius: 16px;
    border-left: 4px solid #00f5d4;
    margin-bottom: 1rem;
}

/* ================================
   ALERTS
================================ */
div[data-testid="stAlert"] {
    background: rgba(0,0,0,0.4);
    border-radius: 14px;
    font-weight: 600;
}

/* ================================
   HIDE STREAMLIT BRANDING
================================ */
footer {
    visibility: hidden;

/* ================================
   STREAMLIT DROPDOWN (REAL FIX)
================================ */

/* Outer select container */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.15) !important;
    border: 2px solid rgba(157, 78, 221, 0.9) !important;
    border-radius: 16px !important;
    box-shadow: 0 0 10px rgba(157, 78, 221, 0.35);
}

/* Selected value text */
section[data-testid="stSidebar"] div[data-baseweb="select"] span {
    color: #000000 !important;
    font-weight: 600;
}

/* Dropdown arrow */
section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: #000000 !important;
}

/* Hover state */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {
    border-color: rgba(0, 245, 212, 0.9) !important;
    box-shadow: 0 0 16px rgba(0, 245, 212, 0.45);
}


}

</style>
""", unsafe_allow_html=True)


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

    lesson_count_for_ui = override_num_lessons or 4

    # ---------- TOPICS ----------
    st.subheader("Topic Names (Required)")
    topic_names = []
    for i in range(lesson_count_for_ui):
        topic = st.text_input(f"Topic for Lesson {i + 1}", key=f"topic_{i}")
        topic_names.append(topic.strip())

    st.markdown("---")

    # ---------- SECTION TOGGLES ----------
    st.subheader("Include Sections")



    include_domains = st.checkbox("Domains", value=True)

    # ---------- OPTIONAL CONTENT ----------
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
        curricular_goals = [
            c.strip() for c in curricular_goals_text.split("\n") if c.strip()
        ]

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
            title = st.text_input(
                "Section Title",
                value=sec["title"],
                key=f"extra_title_{idx}"
            )
            content = st.text_area(
                "Section Content",
                value=sec["content"],
                height=80,
                key=f"extra_content_{idx}"
            )
            if title.strip():
                extra_sections.append({
                    "title": title.strip(),
                    "content": content.strip()
                })

# ---------------------------------------
# MAIN
# ---------------------------------------
uploaded_file = st.file_uploader("Upload chapter/poem PDF", type=["pdf"])

if uploaded_file and st.button("Generate Lesson Plans"):
    if any(not t for t in topic_names):
        st.error("All topic names are required.")
        st.stop()

    result = generate_lesson_plans_from_pdf(
        file_bytes=uploaded_file.read(),
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
        include_extended=include_extended,
    )

    st.session_state["lesson_plan_result"] = result

# ---------------------------------------
# DISPLAY
# ---------------------------------------
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
