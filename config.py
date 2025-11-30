import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Database Configuration
DATABASE_PATH = "data/emails.db"

# Default Prompts
DEFAULT_PROMPTS = {
    "categorization": {
        "name": "Email Categorization",
        "template": """Categorize this email into one of these categories: Important, Newsletter, Spam, To-Do.

To-Do emails must include a direct request requiring user action.

Email Details:
From: {sender}
Subject: {subject}
Body: {body}

Respond with ONLY the category name (Important, Newsletter, Spam, or To-Do)."""
    },
    "action_extraction": {
        "name": "Action Item Extraction",
        "template": """Extract all tasks and action items from this email. Respond in valid JSON format ONLY.

Email Details:
From: {sender}
Subject: {subject}
Body: {body}

Format your response as a JSON array:
{{"tasks": [{{"task": "task description", "deadline": "deadline if mentioned or null"}}]}}

If no tasks found, return: {{"tasks": []}}"""
    },
    "auto_reply": {
        "name": "Auto-Reply Draft",
        "template": """Draft a polite and professional reply to this email. 

Email Details:
From: {sender}
Subject: {subject}
Body: {body}

{additional_context}

Generate a complete email draft with:
- An appropriate subject line (Re: ...)
- Professional greeting
- Response body
- Professional closing

Keep the tone professional and concise."""
    }
}

