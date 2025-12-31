# chunking.py
from typing import List
from groq import Groq
from groq import RateLimitError
import os
import json

GROQ_API_KEY = "gsk_dWatyTslyvvBKGEozKJRWGdyb3FYvtGicALZRYrYgaDmz553h"
GROQ_MODEL1 = "meta-llama/llama-guard-4-12b"


def split_text_into_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def determine_lesson_count(word_count: int) -> int:
    """
    Lesson count is now driven by number of topics.
    This function exists only for backward compatibility.
    """
    raise RuntimeError(
        "Lesson count should be determined by number of topics in semantic chunking mode."
    )


def semantic_chunk_by_topics(
    text: str,
    topics: List[str],
) -> List[str]:
    """
    Returns one text chunk per topic, aligned strictly to topic meaning.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set")

    client = Groq(api_key=GROQ_API_KEY)
    paragraphs = split_text_into_paragraphs(text)

    chunks = []

    for topic in topics:
        prompt = f"""
You are given textbook paragraphs and a topic.

Select ONLY the paragraphs that are directly relevant to the topic.
Return them as a JSON list of strings.
If nothing is relevant, return an empty list.

Topic:
"{topic}"

Paragraphs:
{json.dumps(paragraphs, indent=2)}

Rules:
- Do not paraphrase
- Do not explain
- Do not add new text
- Output valid JSON only
"""
     
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL1,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
  
        except RateLimitError:
            raise RuntimeError("LLM_RATE_LIMIT")

        raw = response.choices[0].message.content.strip()

        try:
            selected_paragraphs = json.loads(raw)
        except json.JSONDecodeError:
            # fail safe: no paragraphs
            selected_paragraphs = []

        chunk_text = "\n\n".join(selected_paragraphs).strip()
        chunks.append(chunk_text)

    return chunks


def split_into_lesson_chunks(
    text: str,
    num_lessons: int,
    topic_names: List[str],
) -> List[str]:
    """
    Entry point used by generator.py
    """
    if num_lessons != len(topic_names):
        raise ValueError(
            f"Number of lessons ({num_lessons}) must match number of topics ({len(topic_names)})"
        )

    return semantic_chunk_by_topics(text, topic_names)
