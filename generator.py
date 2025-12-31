# generator.py
from typing import List, Dict, Any, Optional
import time

from pdf_utils import (
    extract_text_from_pdf,
    rough_word_count,
    clean_pdf_text,
    clean_extracted_text,
)
from chunking import determine_lesson_count, split_into_lesson_chunks
from llm_client import LessonPlanLLMClient
from groq import RateLimitError


# -------------------------------------------------
# 🔒 HARD TOKEN CAP (≈8K TOKENS SAFETY)
# -------------------------------------------------
def hard_cap_text(text: str, max_tokens: int = 8000) -> str:
    """
    Enforces a hard token cap using a safe character approximation.
    ~4 characters per token → 8000 tokens ≈ 32000 chars.
    """
    if not text:
        return text

    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]

    # Try to cut at a clean boundary
    for sep in [". ", "\n\n", "\n"]:
        cut = truncated.rfind(sep)
        if cut > max_chars * 0.8:
            return truncated[: cut + 1]

    return truncated


def generate_lesson_plans_from_pdf(
    file_bytes: bytes,
    grade: str,
    chapter_name: str,
    topic_names: List[str],
    page_no: str,
    override_num_lessons: Optional[int],
    domains,
    curricular_goals,
    competencies,
    extra_sections,
    include_learning_outcomes: bool,
    include_teaching_aids: bool,
    include_strategy: bool,
    include_interdisciplinary: bool,
    include_extended: bool,
) -> Dict[str, Any]:

    # -------------------------
    # TEXT EXTRACTION & CLEANING
    # -------------------------
    text = extract_text_from_pdf(file_bytes)
    text = clean_pdf_text(text)
    text = clean_extracted_text(text)
    wc = rough_word_count(text)

    # -------------------------
    # LESSON COUNT
    # -------------------------
    num_lessons = override_num_lessons or len(topic_names)

    # -------------------------
    # SEMANTIC CHUNKING
    # -------------------------
    chunks = split_into_lesson_chunks(text, num_lessons, topic_names)

    client = LessonPlanLLMClient()
    lesson_plans = []

    # -------------------------
    # LLM GENERATION (SAFE)
    # -------------------------
    for i, chunk in enumerate(chunks):
        # 🔒 HARD 8K TOKEN CAP (ADDED)
        safe_chunk = hard_cap_text(chunk, max_tokens=8000)

        # 🔁 RATE-LIMIT SAFE EXECUTION
        try:
            lp = client.generate_lesson_plan_fields(
                lesson_text=safe_chunk,
                grade=grade,
                chapter_name=chapter_name,
                topic_name=topic_names[i],
                page_no=page_no,
                lesson_plan_no=i + 1,
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

        except RateLimitError:
            # ⏳ WAIT AND RETRY ONCE
            time.sleep(60)

            try:
                lp = client.generate_lesson_plan_fields(
                    lesson_text=safe_chunk,
                    grade=grade,
                    chapter_name=chapter_name,
                    topic_name=topic_names[i],
                    page_no=page_no,
                    lesson_plan_no=i + 1,
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
            except RateLimitError:
                raise RuntimeError("LLM_RATE_LIMIT")

        lesson_plans.append(lp)

    return {
        "num_lessons": num_lessons,
        "lesson_plans": lesson_plans,
    }
