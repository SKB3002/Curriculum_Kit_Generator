# llm_client.py
from typing import Dict, Any, List, Optional
import json
import os
from groq import Groq

from config import TARGET_LESSON_DURATION_MIN, MAX_LESSON_DURATION_MIN

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-safeguard-20b")


class LessonPlanLLMClient:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set")
        self.client = Groq(api_key=GROQ_API_KEY)

    def generate_lesson_plan_fields(
        self,
        lesson_text: str,
        grade: str,
        chapter_name: str,
        topic_name: str,
        page_no: str,
        lesson_plan_no: int,
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

        sections = [
            "grade", "chapter_name", "page_no",
            "topic_name", "lesson_plan_no"
        ]

        if domains: sections.append("domains")
        if curricular_goals: sections.append("curricular_goals")
        if competencies: sections.append("competencies")
        if include_learning_outcomes: sections.append("learning_outcomes")
        if include_teaching_aids: sections.append("teaching_aids")
        if include_strategy: sections.append("strategy_pedagogy")
        if include_interdisciplinary: sections.append("interdisciplinary_approach")
        if include_extended: sections.append("extended_learning_assignment")

        for sec in extra_sections:
            sections.append(sec["title"].lower().replace(" ", "_"))

        prompt = f"""
Generate a lesson plan ({TARGET_LESSON_DURATION_MIN}-{MAX_LESSON_DURATION_MIN} minutes).

STRICT TOPIC: {topic_name}

Include ONLY these sections:
{sections}

Lesson Text:
\"\"\"
{lesson_text}
\"\"\"

Rules:
- Use topic exactly
- Do not invent sections
- Output valid JSON only
"""

        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        data = json.loads(response.choices[0].message.content)

        # Hard remove disabled sections
        return {k: v for k, v in data.items() if k in sections}
