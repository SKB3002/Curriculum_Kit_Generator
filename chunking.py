# chunking.py
from typing import List
from config import (
    WORD_COUNT_FOR_4_LESSONS,
    WORD_COUNT_FOR_5_LESSONS,
)

def determine_lesson_count(word_count: int) -> int:
    """
    Heuristic for number of lesson plans.
    """
    if word_count <= WORD_COUNT_FOR_4_LESSONS:
        return 4
    elif word_count <= WORD_COUNT_FOR_5_LESSONS:
        return 5
    else:
        return 6


def split_text_into_paragraphs(text: str) -> List[str]:
    """
    Splits text into rough paragraphs using blank lines.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs


def split_into_lesson_chunks(text: str, num_lessons: int) -> List[str]:
    """
    Splits text into num_lessons chunks, keeping paragraphs intact.
    Approximate equal total word count per chunk.
    """
    paragraphs = split_text_into_paragraphs(text)
    if not paragraphs:
        return [text]

    total_words = sum(len(p.split()) for p in paragraphs)
    target_words_per_chunk = max(1, total_words // num_lessons)

    chunks = []
    current_chunk = []
    current_count = 0
    remaining_chunks = num_lessons

    for i, p in enumerate(paragraphs):
        p_words = len(p.split())
        # If adding this paragraph would exceed target and we still have chunks left,
        # start a new chunk
        if (current_count + p_words > target_words_per_chunk) and (remaining_chunks > 1):
            chunks.append("\n\n".join(current_chunk).strip())
            remaining_chunks -= 1
            current_chunk = [p]
            current_count = p_words
        else:
            current_chunk.append(p)
            current_count += p_words

    if current_chunk:
        chunks.append("\n\n".join(current_chunk).strip())

    # If for some reason we have fewer chunks than requested, pad last ones
    while len(chunks) < num_lessons:
        chunks.append("")

    return chunks
