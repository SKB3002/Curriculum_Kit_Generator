# generator.py
from typing import List, Dict, Any, Optional
from pdf_utils import extract_text_from_pdf, rough_word_count
from chunking import determine_lesson_count, split_into_lesson_chunks
from llm_client import LessonPlanLLMClient


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

    text = extract_text_from_pdf(file_bytes)
    wc = rough_word_count(text)

    num_lessons = override_num_lessons or determine_lesson_count(wc)
    chunks = split_into_lesson_chunks(text, num_lessons)

    client = LessonPlanLLMClient()
    lesson_plans = []

    for i, chunk in enumerate(chunks):
        lp = client.generate_lesson_plan_fields(
            lesson_text=chunk,
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
        lesson_plans.append(lp)

    return {
        "num_lessons": num_lessons,
        "lesson_plans": lesson_plans,
    }
