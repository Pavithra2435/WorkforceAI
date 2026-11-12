"""
================================================================================
WorkforceAI Copilot - RLHF & Fine-Tuning Feedback Store
Persists human feedback (thumbs up / thumbs down) directly into a Python file
(genai/ai_training_data.py) for retraining, instruction fine-tuning, and alignment.
================================================================================
"""

import os
import json
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINING_FILE_PATH = os.path.join(CURRENT_DIR, "ai_training_data.py")


def init_training_file():
    """Initializes the ai_training_data.py file if it doesn't already exist."""
    if not os.path.exists(TRAINING_FILE_PATH):
        initial_content = '''"""
================================================================================
WorkforceAI Copilot - AI Training & RLHF Dataset
Auto-generated from user feedback (thumbs up / thumbs down).
Use this dataset for instruction fine-tuning, DPO (Direct Preference Optimization),
and model evaluation.
================================================================================
"""

TRAINING_DATASET = []
'''
        with open(TRAINING_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(initial_content)


def record_feedback(query: str, response: str, feedback: str, tool_used: str = None) -> dict:
    """
    Appends a new user feedback record to ai_training_data.py.
    """
    init_training_file()
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    is_positive = feedback.strip().lower() in ["good", "positive", "thumbs_up"]
    rating = 1 if is_positive else -1
    label = "positive_example" if is_positive else "negative_example"
    
    new_entry = {
        "timestamp": timestamp,
        "query": query.strip(),
        "response": response.strip(),
        "feedback": "good" if is_positive else "bad",
        "label": label,
        "rating": rating,
        "tool_used": tool_used or "direct_synthesis"
    }
    
    # Read existing dataset by importing or fallback parsing
    dataset = []
    if os.path.exists(TRAINING_FILE_PATH):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("ai_training_data", TRAINING_FILE_PATH)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            dataset = list(getattr(mod, "TRAINING_DATASET", []))
        except Exception:
            dataset = []
            
    # Append the new feedback entry
    dataset.append(new_entry)
    
    # Serialize cleanly back into the Python file as executable code
    formatted_dataset = json.dumps(dataset, indent=4, ensure_ascii=False)
    file_content = f'''"""
================================================================================
WorkforceAI Copilot - AI Training & RLHF Dataset
Auto-generated from user feedback (thumbs up / thumbs down).
Total training pairs: {len(dataset)}
Last updated: {timestamp}
================================================================================
"""

TRAINING_DATASET = {formatted_dataset}
'''
    with open(TRAINING_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(file_content)
        
    return {
        "status": "success",
        "total_records": len(dataset),
        "file_path": TRAINING_FILE_PATH,
        "recorded_entry": new_entry
    }

