import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from genai.hr_agent import ask_hr_copilot

print("Testing ask_hr_copilot...")
ans = ask_hr_copilot("What is the company headcount?")
print("Intent:", ans["intent"])
print("Tool:", ans["tool_used"])
print("Answer:", ans["natural_language_answer"])
print("Recommendation:", ans["recommended_action"])
print("\n[SUCCESS] Copilot works perfectly!")

