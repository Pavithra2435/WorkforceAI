"""
================================================================================
AI-Powered HR Workforce Insights Dashboard
Step 4: GenAI Assistant Test & Evaluation Runner (genai/test_agent.py)
Technology: Python
================================================================================

This test runner executes representative natural-language workforce questions
through `ask_hr_copilot` to demonstrate:
1. Intent Recognition & Entity Extraction
2. Controlled Tool Calling (KPI Engine & ML Engine)
3. Grounded Natural-Language Answer Generation
4. Strategic HR Action Recommendations
"""

import os
import sys

# Ensure root directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from genai.hr_agent import ask_hr_copilot


def run_evaluations():
    test_queries = [
        "Which department has the highest attrition rate?",
        "Show me employees at high flight risk.",
        "What are the primary drivers of voluntary employee turnover?",
        "Are there any attendance anomalies detected across departments?",
        "What is our projected exit forecast for next quarter?",
        "What is the flight risk for employee E0087?"  # Entity extraction bonus test
    ]

    print("\n" + "=" * 90)
    print(" AI-POWERED HR WORKFORCE INSIGHTS DASHBOARD — GENAI COPILOT EVALUATION")
    print("=" * 90)

    for i, query in enumerate(test_queries, start=1):
        print(f"\n[{i}] USER QUESTION: \"{query}\"")
        print("-" * 90)

        response = ask_hr_copilot(query)

        print(f"  • Recognized Intent : {response['intent']}")
        print(f"  • Tool Invoked      : {response['tool_used']}()")
        print(f"\n  • AI RESPONSE:")
        print(f"    {response['natural_language_answer']}")
        print(f"\n  • STRATEGIC HR RECOMMENDATION:")
        print(f"    {response['recommended_action']}")
        print("-" * 90)

    print("\n" + "=" * 90)
    print(" All Generative AI Copilot evaluations completed successfully!")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    run_evaluations()

