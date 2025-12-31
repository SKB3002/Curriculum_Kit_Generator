# app.py
import io
from typing import List, Dict, Any

import streamlit as st
from docx import Document
from groq import Groq
from groq import RateLimitError
import json
import os

from generator import generate_lesson_plans_from_pdf
from pdf_utils import extract_text_from_pdf
from config import (
    DEFAULT_DOMAINS,
    DEFAULT_CURRICULAR_GOALS,
    DEFAULT_COMPETENCIES,
)

# -------------------------------
# LLM SETUP (AUTO TOPIC INFERENCE)
# -------------------------------
GROQ_API_KEY = "gsk_dWatyTslyvvBKGEozKJRWGdyb3FYvtGicALZRYrYgaDmz553h"
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

if "lesson_plan_result" not in st.session_state:
    st.session_state.lesson_plan_result = None


def infer_topics_from_text(text: str) -> List[str]:
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are a curriculum expert.

Divide the chapter into 45–50 minute lesson-sized TOPICS.
Return ONLY a JSON array of short topic names.
No explanations. No markdown.

Chapter Text:
\"\"\"
{text[:12000]}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
    except RateLimitError:
        raise RuntimeError("LLM_RATE_LIMIT")

    raw = response.choices[0].message.content.strip()

    try:
        topics = json.loads(raw)
        if isinstance(topics, list) and topics:
            return [str(t).strip() for t in topics if str(t).strip()]
    except Exception:
        pass

    # ---------- FALLBACK ----------
    return [
        "Introduction and Overview",
        "Core Concepts",
        "Detailed Explanation",
        "Examples and Applications",
        "Summary and Recap",
    ]


# -------------------------------
# PAGE CONFIG & STYLES (UNCHANGED)
# -------------------------------
st.set_page_config(
    page_title="Lesson Plan Generator",
    page_icon="📘",
    layout="centered",
)

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
        ["Auto-decide (4–6)", "3", "4", "5", "6", "7", "8", "9", "10"],
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
        competencies = [
            c.strip() for c in competencies_text.split("\n") if c.strip()
        ]

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
                key=f"extra_title_{idx}",
            )
            content = st.text_area(
                "Section Content",
                value=sec["content"],
                height=80,
                key=f"extra_content_{idx}",
            )
            if title.strip():
                extra_sections.append(
                    {"title": title.strip(), "content": content.strip()}
                )

# ---------------------------------------
# MAIN
# ---------------------------------------
uploaded_file = st.file_uploader("Upload chapter/poem PDF", type=["pdf"])

generate_clicked = st.button(
    "Generate Lesson Plans",
    disabled=st.session_state.is_generating,
)

if uploaded_file and generate_clicked:
    st.session_state.is_generating = True

    with st.spinner("Generating lesson plans. Please wait..."):
        try:
            file_bytes = uploaded_file.read()

            # ✅ CRITICAL FIX: Extract real PDF text
            raw_text = extract_text_from_pdf(file_bytes)

            if override_num_lessons is None:
                topic_names = infer_topics_from_text(raw_text)
                if not topic_names:
                    st.error("Could not infer topics automatically.")
                    st.stop()
                override_num_lessons = len(topic_names)

            if any(not t for t in topic_names):
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
                include_extended=include_extended,
            )

            st.session_state.lesson_plan_result = result

        except RuntimeError as e:
            if str(e) == "LLM_RATE_LIMIT":
                st.warning(
                    "⚠️ LLM usage limit reached.\n\n"
                    "Please wait for some time and try again."
                )
            else:
                raise e

        finally:
            st.session_state.is_generating = False

# ---------------------------------------
# DISPLAY
# ---------------------------------------
if st.session_state.lesson_plan_result:
    lesson_plans = st.session_state.lesson_plan_result.get("lesson_plans", [])

    if not lesson_plans:
        st.warning(
            "No lesson plans were generated. "
            "Try refining topics or using manual mode."
        )

    for lp in lesson_plans:
        with st.expander(f"Lesson Plan {lp.get('lesson_plan_no', '')}"):
            for k, v in lp.items():
                st.markdown(f"**{k.replace('_',' ').title()}:**")
                if isinstance(v, list):
                    for i in v:
                        st.markdown(f"- {i}")
                else:
                    st.write(v)
