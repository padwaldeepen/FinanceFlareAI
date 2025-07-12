from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import openai
import json

from app.api.routers.auth import get_current_user
from app.db.session import get_db
from app.core.config import settings
from app.db.models import User

router = APIRouter()

# Configure OpenAI
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY

# Pydantic models
class CategorizeRequest(BaseModel):
    description: str
    amount: Optional[float] = None
    date: Optional[str] = None

class CategorizeResponse(BaseModel):
    suggested_category: str
    confidence: float
    extracted_amount: Optional[float] = None
    extracted_date: Optional[str] = None
    transaction_type: str  # "income" or "expense"

# Predefined categories for AI to choose from
EXPENSE_CATEGORIES = [
    "Food & Dining", "Transportation", "Shopping", "Entertainment", 
    "Healthcare", "Utilities", "Housing", "Education", "Travel", 
    "Insurance", "Taxes", "Personal Care", "Gifts", "Subscriptions",
    "Business", "Other"
]

INCOME_CATEGORIES = [
    "Salary", "Freelance", "Investment", "Business", "Gift", 
    "Refund", "Other"
]

@router.post("/categorize", response_model=CategorizeResponse)
async def categorize_transaction(
    request: CategorizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured"
        )
    
    try:
        # Prepare the prompt for OpenAI
        prompt = f"""
        Analyze this transaction description and categorize it appropriately.
        
        Description: {request.description}
        Amount: {request.amount if request.amount else 'Not specified'}
        Date: {request.date if request.date else 'Not specified'}
        
        Please categorize this transaction and provide the following information in JSON format:
        {{
            "suggested_category": "category_name",
            "confidence": 0.95,
            "extracted_amount": null,
            "extracted_date": null,
            "transaction_type": "expense"
        }}
        
        Available expense categories: {', '.join(EXPENSE_CATEGORIES)}
        Available income categories: {', '.join(INCOME_CATEGORIES)}
        
        Rules:
        1. Choose the most appropriate category from the provided lists
        2. Set confidence between 0.0 and 1.0 based on how certain you are
        3. If amount is not provided but can be extracted from description, extract it
        4. If date is not provided but can be extracted from description, extract it
        5. Determine if this is income or expense based on the description
        6. For expenses, use expense categories. For income, use income categories
        7. Return only valid JSON, no additional text
        """
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial transaction categorization assistant. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        # Parse the response
        content = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        try:
            # Remove any markdown formatting if present
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content)
            
            # Validate the response
            if not isinstance(result, dict):
                raise ValueError("Invalid response format")
            
            # Ensure required fields are present
            if "suggested_category" not in result:
                raise ValueError("Missing suggested_category")
            if "confidence" not in result:
                raise ValueError("Missing confidence")
            if "transaction_type" not in result:
                raise ValueError("Missing transaction_type")
            
            # Validate category
            if result["transaction_type"] == "expense":
                if result["suggested_category"] not in EXPENSE_CATEGORIES:
                    result["suggested_category"] = "Other"
            elif result["transaction_type"] == "income":
                if result["suggested_category"] not in INCOME_CATEGORIES:
                    result["suggested_category"] = "Other"
            else:
                result["transaction_type"] = "expense"
                result["suggested_category"] = "Other"
            
            # Validate confidence
            if not isinstance(result["confidence"], (int, float)) or result["confidence"] < 0 or result["confidence"] > 1:
                result["confidence"] = 0.5
            
            return CategorizeResponse(
                suggested_category=result["suggested_category"],
                confidence=float(result["confidence"]),
                extracted_amount=result.get("extracted_amount"),
                extracted_date=result.get("extracted_date"),
                transaction_type=result["transaction_type"]
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback categorization
            return CategorizeResponse(
                suggested_category="Other",
                confidence=0.3,
                extracted_amount=request.amount,
                extracted_date=request.date,
                transaction_type="expense"
            )
    
    except Exception as e:
        # Log the error for debugging
        pass
        
        # Return fallback response
        return CategorizeResponse(
            suggested_category="Other",
            confidence=0.1,
            extracted_amount=request.amount,
            extracted_date=request.date,
            transaction_type="expense"
        )

@router.get("/categories")
async def get_available_categories():
    """Get all available categories for the frontend"""
    return {
        "expense_categories": EXPENSE_CATEGORIES,
        "income_categories": INCOME_CATEGORIES
    } 