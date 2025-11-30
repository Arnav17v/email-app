from google import genai
import os
import json
import re

class LLMService:
    def __init__(self):
        # The client automatically gets API key from GEMINI_API_KEY environment variable
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client()
        # Using gemini-2.5-flash - stable version with excellent capabilities
        # Supports up to 1 million tokens and works well with free tier
        self.model_name = "gemini-2.5-flash"
    
    def generate_response(self, prompt):
        """Generate response from Gemini"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def categorize_email(self, sender, subject, body, prompt_template):
        """Categorize email using custom prompt"""
        prompt = prompt_template.format(
            sender=sender,
            subject=subject,
            body=body
        )
        
        response = self.generate_response(prompt)
        # Clean up response to get just the category
        category = response.strip()
        
        # Ensure it's one of the valid categories
        valid_categories = ["Important", "Newsletter", "Spam", "To-Do"]
        for valid_cat in valid_categories:
            if valid_cat.lower() in category.lower():
                return valid_cat
        
        return category
    
    def extract_action_items(self, sender, subject, body, prompt_template):
        """Extract action items using custom prompt"""
        prompt = prompt_template.format(
            sender=sender,
            subject=subject,
            body=body
        )
        
        response = self.generate_response(prompt)
        
        # Try to parse JSON response
        try:
            # Clean response - sometimes LLM wraps JSON in markdown
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            action_data = json.loads(cleaned_response)
            return action_data
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract tasks manually
            return {"tasks": [], "raw_response": response}
    
    def generate_reply(self, sender, subject, body, prompt_template, additional_context=""):
        """Generate email reply using custom prompt"""
        prompt = prompt_template.format(
            sender=sender,
            subject=subject,
            body=body,
            additional_context=additional_context
        )
        
        response = self.generate_response(prompt)
        return response
    
    def chat_with_agent(self, user_query, email_context, stored_prompts):
        """Chat interface for email agent"""
        # Build context from emails and prompts
        context = f"""You are an intelligent Email Productivity Agent. You help users manage their emails.

User Query: {user_query}

Available Email Context:
{email_context}

You have access to these capabilities based on stored prompts:
- Email categorization
- Action item extraction
- Draft generation

Respond to the user's query in a helpful and concise manner."""
        
        response = self.generate_response(context)
        return response
    
    def summarize_email(self, sender, subject, body):
        """Summarize an email"""
        prompt = f"""Provide a brief, clear summary of this email in 2-3 sentences.

From: {sender}
Subject: {subject}
Body: {body}

Summary:"""
        
        return self.generate_response(prompt)
    
    def generate_custom_response(self, prompt):
        """Generate response for custom prompts"""
        return self.generate_response(prompt)

