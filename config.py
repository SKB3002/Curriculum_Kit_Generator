# config.py
import os

# -----------------------------
# LLM CONFIG
# -----------------------------
GROQ_API_KEY = "gsk_dWatyTslyvvBKGEozKJRWGdyb3FYvtGicALZRYrYgaDmz553h"
GROQ_MODEL = "openai/gpt-oss-20b"


# -----------------------------
# DEFAULT EDUCATIONAL METADATA
# -----------------------------
# You can customize these per grade / subject later
DEFAULT_DOMAINS = [
    "Cognitive Development",
    "Language and Communication",
    "Critical Thinking and Reasoning"
]

DEFAULT_CURRICULAR_GOALS = [
    "Develop conceptual understanding of the topic",
    "Strengthen reading comprehension and analytical skills",
    "Encourage application of knowledge to real-life contexts"
]

DEFAULT_COMPETENCIES = [
    "Students can identify and explain key ideas in the text",
    "Students can ask and answer questions based on the content",
    "Students can express their understanding verbally or in writing"
]

# Lesson duration (for prompts – not hard constraints)
TARGET_LESSON_DURATION_MIN = 45
MAX_LESSON_DURATION_MIN = 50

# Chunking thresholds (word count)
WORD_COUNT_FOR_4_LESSONS = 2500
WORD_COUNT_FOR_5_LESSONS = 4000
