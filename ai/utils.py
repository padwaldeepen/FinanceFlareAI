import openai
from typing import List, Dict, Any
import json
from app.core.config import settings

# Configure OpenAI
openai.api_key = settings.OPENAI_API_KEY

def categorize_expense(description: str, amount: float) -> str:
    """
    Use OpenAI to categorize an expense based on description and amount.
    """
    try:
        with open('ai/expenseCategorizationPrompt.txt', 'r') as f:
            prompt_template = f.read()
        
        prompt = prompt_template.format(description=description, amount=amount)
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial categorization expert. Respond with only the category name."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        category = response.choices[0].message.content.strip()
        return category
    except Exception as e:
        return "Other"

def get_budgeting_advice(
    monthly_income: float,
    current_month_spending: float,
    top_categories: List[Dict[str, Any]],
    budget_goals: List[str],
    recent_transactions: List[Dict[str, Any]]
) -> str:
    """
    Get personalized budgeting advice from OpenAI.
    """
    try:
        with open('ai/budgetingAdvicePrompt.txt', 'r') as f:
            prompt_template = f.read()
        
        # Format the data for the prompt
        top_categories_str = ", ".join([f"{cat['name']} (${cat['total']})" for cat in top_categories])
        budget_goals_str = ", ".join(budget_goals) if budget_goals else "No specific goals set"
        
        recent_transactions_str = "\n".join([
            f"- {t['description']}: ${t['amount']} ({t['category']})"
            for t in recent_transactions[:10]  # Limit to last 10 transactions
        ])
        
        prompt = prompt_template.format(
            monthly_income=monthly_income,
            current_month_spending=current_month_spending,
            top_categories=top_categories_str,
            budget_goals=budget_goals_str,
            recent_transactions=recent_transactions_str
        )
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly financial advisor providing personalized budgeting advice."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        advice = response.choices[0].message.content.strip()
        return advice
    except Exception as e:
        return "Unable to generate budgeting advice at this time. Please try again later."

def parse_natural_language_transaction(text: str) -> Dict[str, Any]:
    """
    Parse natural language input to extract transaction details.
    """
    try:
        prompt = f"""
        Parse the following natural language transaction input and extract the amount, description, and type (income or expense).
        
        Input: "{text}"
        
        Return a JSON object with the following structure:
        {{
            "amount": float,
            "description": "string",
            "type": "income" or "expense",
            "confidence": float (0-1)
        }}
        
        Only return the JSON object, nothing else.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial transaction parser. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        return result
    except Exception as e:
        return {
            "amount": 0.0,
            "description": "Unable to parse",
            "type": "expense",
            "confidence": 0.0
        } 