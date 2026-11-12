"""
================================================================================
WorkforceAI Copilot - AI Training & RLHF Dataset
Auto-generated from user feedback (thumbs up / thumbs down).
Total training pairs: 3
Last updated: 2026-11-10T04:08:45.883338Z
================================================================================
"""

TRAINING_DATASET = [
    {
        "timestamp": "2026-11-08T16:20:32.890938Z",
        "query": "Which department has highest attrition?",
        "response": "HR has the highest attrition at 22.58%.",
        "feedback": "good",
        "label": "positive_example",
        "rating": 1,
        "tool_used": "tool_department_breakdown"
    },
    {
        "timestamp": "2026-11-08T16:22:32.851989Z",
        "query": "what is the attendance of customer support?",
        "response": "Here is how attendance and daily engagement look for the **Customer Support** department:\n\n• **On-site / In-office**: 80.12%\n• **Remote Work**: 9.43%\n• **Absenteeism**: 5.2%\n\nOn average, colleagues log **8.25 productive work hours per day**, demonstrating strong and steady day-to-day engagement.",
        "feedback": "good",
        "label": "positive_example",
        "rating": 1,
        "tool_used": "tool_attendance_kpis"
    },
    {
        "timestamp": "2026-11-10T04:08:45.883338Z",
        "query": "What are the workforce movement totals?",
        "response": "Here is our high-level workforce summary:\n\n• **Total Workforce Tracked**: **500 team members** (**430 currently active**, 70 departed)\n• **Overall Attrition Rate**: **14.0%**, well-aligned with enterprise benchmarks\n• **Average Employee Tenure**: **2.91 years** (35.0 months) of organizational experience\n\nOur team foundations are stable, with healthy retention in core operational units.",
        "feedback": "good",
        "label": "positive_example",
        "rating": 1,
        "tool_used": "tool_executive_kpis"
    }
]
