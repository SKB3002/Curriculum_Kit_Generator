# llm_client.py
from typing import Dict, Any, List, Optional
import json
import os
from groq import Groq
from groq import RateLimitError

from config import TARGET_LESSON_DURATION_MIN, MAX_LESSON_DURATION_MIN

GROQ_API_KEY = "gsk_dWatyTslyvvBKGEozKJRWGdyb3FYvtGicALZRYrYgaDmz553h"
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


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
You are an expert curriculum designer and academic content developer
working for Navneet Education Ltd.

You have been trained exclusively on official Navneet teacher handbooks
and lesson plans used in Indian primary and middle school classrooms.

Your task is to generate lesson plans that are indistinguishable
from officially published Navneet lesson plans.

1. STRUCTURE (MUST BE EXACT)

You MUST follow this exact order and naming:

Include ONLY these sections:
{sections}


Do NOT rename, merge, reorder, or omit sections.
If a section has no valid content, leave it blank but keep the heading.

2. NAVNEET LANGUAGE & TONE

- Write in professional teacher-handbook language
- Short, clear, directive sentences
- No motivational or marketing language
- No abstract or AI-sounding phrases

AVOID words such as:
“explore”, “critically analyze”, “deep dive”, “empower”, “engage deeply”

USE authentic Navneet phrasing such as:
- “Conduct Textual Exercise…”
- “Discuss the answers.”
- “Hold a discussion…”
- “Play the audio/video…”
- “Assign Homework.”

3. PEDAGOGICAL REALISM

All activities must be realistically executable in a 35–45 minute classroom.
Everything must be teacher-led and step-by-step.
No hypothetical or vague activities.

Strategy/Pedagogy MUST broadly follow:
- Prior knowledge activation
- Core content delivery (reading/audio/video)
- Guided discussion
- Textual exercise
- Reinforcement
- Homework assignment

4. STRICT CONTENT SAFETY RULES

DO NOT:
- Invent or guess Navneet internal codes (ELA IDs, worksheet IDs)
- Invent specific file names or proprietary asset references
- Mention unknown video/audio titles unless explicitly generic

ALLOWED:
- Generic references only, such as:
  “Audio: Chapter Reading”
  “Digital Video related to the chapter”
  “Chart/Flashcards”
  “Worksheet”

5. Curricular Goals:
   - Write 1–2 syllabus-aligned statements
   - Use formal NCERT-style language
   - Do NOT write student-friendly or generic goals

6. Competencies:
   - Describe transferable academic capabilities
   - Avoid step-by-step skills
   - Use institutional phrasing

7. Learning Outcomes:
   - Write One or Two at max outcomes
   - It must directly match the lesson topic and the content provided
   - No bullet lists beyond two point

8. Teaching Aids:
   - List only aids explicitly relevant to the lesson
   - Prefer Digital Video if applicable
   - Do NOT invent IDs or codes

8. Inter Disciplinary Approach:
   - Mention at most ONE subject
   - Keep it conservative and realistic

10. Extended Learning Assignment (VERY IMPORTANT)

ELA MUST be written exactly in Navneet style:
- Simple
- Clear
- Direct
- Either Textual or Non-Textual
- No creativity prompts
- No reflective writing unless age-appropriate

Examples of acceptable ELA phrasing:
- “Write four sentences similar to the ones in Question A.”
- “Write rhyming words for the given words.”
- “Make a table and fill it for one week.”
- “Answer the given questions.”

11. GRADE SENSITIVITY

For lower grades (1–3):
- Focus on listening, speaking, identifying, reciting, role-play
- Avoid abstract reasoning or complex vocabulary
- Use observable student actions only


12. OUTPUT RULES
- Use bullet points exactly like official lesson plans
- Use hyphens ( - ) or dots ( • ) consistently
- Do NOT add explanations, commentary, or reasoning
- Do NOT mention AI, models, prompts, or generation process

QUALITY BAR

If a Navneet academic editor reads this lesson plan,
they must NOT be able to distinguish it from a human-written one.

Now generate the lesson plan using the provided inputs.


STRICT TOPIC: {topic_name}

Lesson Text:
\"\"\"
{lesson_text}
\"\"\"

Rules:
- Use topic exactly.
- Do not invent sections.
- Output valid JSON only.
- Nothing extra words other than the JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
            )
        except RateLimitError as e:
            raise RuntimeError("LLM_RATE_LIMIT")

        raw_content = response.choices[0].message.content

        # -------- SAFE JSON PARSING (ADDED) --------
        if not raw_content or not raw_content.strip():
            raise ValueError("LLM returned empty response")

        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError:
            start = raw_content.find("{")
            end = raw_content.rfind("}")
            if start == -1 or end == -1:
                raise ValueError(f"Invalid LLM output:\n{raw_content}")
            data = json.loads(raw_content[start:end + 1])

        # -------- FILTER ALLOWED SECTIONS (EXISTING LOGIC) --------
        cleaned = {k: v for k, v in data.items() if k in sections}

        # -------- FORCE SYSTEM-CONTROLLED FIELDS (ADDED) --------
        cleaned["grade"] = grade
        cleaned["chapter_name"] = chapter_name
        cleaned["topic_name"] = topic_name
        cleaned["page_no"] = page_no
        cleaned["lesson_plan_no"] = lesson_plan_no

        return cleaned
