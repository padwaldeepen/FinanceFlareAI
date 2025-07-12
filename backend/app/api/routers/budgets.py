from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.api.routers.auth import get_current_user
from app.db.session import get_db
from app.db.models import User, Budget

router = APIRouter()

# Pydantic models
class BudgetCreate(BaseModel):
    name: str
    amount: float
    period: str  # "monthly", "weekly", "yearly"
    category_id: Optional[int] = None
    start_date: str
    end_date: Optional[str] = None

class BudgetResponse(BaseModel):
    id: int
    name: str
    amount: float
    period: str
    category_id: Optional[int]
    start_date: str
    end_date: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/", response_model=List[BudgetResponse])
async def get_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    return budgets

@router.post("/", response_model=BudgetResponse)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Budget creation will be implemented in future updates
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Budget creation not yet implemented"
    )

@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    return budget 