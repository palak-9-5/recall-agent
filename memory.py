import json
import os
from datetime import datetime

DEFAULT_MEMORY_FILE = "memory.json"

def load_memory(filepath: str = DEFAULT_MEMORY_FILE) -> dict:
    """Loads the concept memory and review history from a JSON file.
    
    If the file does not exist, returns an empty dictionary.
    """
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {filepath} was corrupted. Starting with empty memory.")
        return {}

def save_memory(memory_data: dict, filepath: str = DEFAULT_MEMORY_FILE) -> None:
    """Saves the concept memory and review history to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, indent=4, ensure_ascii=False)

def add_concept(
    concept_name: str, 
    question: str, 
    expected_answer: str, 
    filepath: str = DEFAULT_MEMORY_FILE
) -> dict:
    """Adds a new concept to the memory database with default SM-2 values.
    
    Initial SM-2 values:
    - easiness: 2.5 (default starting easiness factor)
    - interval: 0 (needs review immediately)
    - repetitions: 0 (no consecutive correct repetitions yet)
    - next_review: today's date (so it shows up in due reviews right away)
    """
    memory_data = load_memory(filepath)
    
    # We use today's date in YYYY-MM-DD format as the initial next review date
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    new_concept = {
        "concept": concept_name,
        "question": question,
        "expected_answer": expected_answer,
        "easiness": 2.5,
        "interval": 0,
        "repetitions": 0,
        "next_review": today_str,
        "history": []
    }
    
    memory_data[concept_name] = new_concept
    save_memory(memory_data, filepath)
    return new_concept

def get_due_concepts(memory_data: dict) -> dict:
    """Filters and returns concepts that are due for review.
    
    A concept is due if its 'next_review' date is less than or equal to today.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    due_concepts = {}
    
    for name, details in memory_data.items():
        # Compare dates alphabetically because 'YYYY-MM-DD' format sorts chronologically
        if details.get("next_review", "") <= today_str:
            due_concepts[name] = details
            
    return due_concepts
