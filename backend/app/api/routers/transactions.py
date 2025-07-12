from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from app.api.routers.auth import get_current_user
from app.db.session import get_db
from app.db.models import User, Transaction, Category

router = APIRouter()

# Pydantic models
class TransactionCreate(BaseModel):
    amount: float
    description: str
    transaction_type: str  # "income" or "expense"
    category_id: Optional[int] = None
    date: datetime
    notes: Optional[str] = None

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    transaction_type: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str
    transaction_type: str
    category_id: Optional[int]
    category_name: Optional[str]
    category_color: Optional[str]
    date: datetime
    notes: Optional[str]
    ai_categorized: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CategorySummary(BaseModel):
    category_id: Optional[int]
    category_name: str
    category_color: str
    total_amount: float
    transaction_count: int

class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_amount: float
    category_summaries: List[CategorySummary]
    recent_transactions: List[TransactionResponse]

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate category belongs to user if provided
    if transaction_data.category_id:
        category = db.query(Category).filter(
            Category.id == transaction_data.category_id,
            Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Create transaction
    db_transaction = Transaction(
        amount=transaction_data.amount,
        description=transaction_data.description,
        transaction_type=transaction_data.transaction_type,
        category_id=transaction_data.category_id,
        user_id=current_user.id,
        date=transaction_data.date,
        notes=transaction_data.notes
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    # Get category info for response
    category = None
    if db_transaction.category_id:
        category = db.query(Category).filter(Category.id == db_transaction.category_id).first()
    
    return TransactionResponse(
        id=db_transaction.id,
        amount=db_transaction.amount,
        description=db_transaction.description,
        transaction_type=db_transaction.transaction_type,
        category_id=db_transaction.category_id,
        category_name=category.name if category else None,
        category_color=category.color if category else None,
        date=db_transaction.date,
        notes=db_transaction.notes,
        ai_categorized=db_transaction.ai_categorized,
        created_at=db_transaction.created_at
    )

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    transaction_type: Optional[str] = None,
    category_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    # Apply filters
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    # Get transactions with category info
    transactions = query.offset(skip).limit(limit).all()
    
    # Get category info for each transaction
    result = []
    for transaction in transactions:
        category = None
        if transaction.category_id:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
        
        result.append(TransactionResponse(
            id=transaction.id,
            amount=transaction.amount,
            description=transaction.description,
            transaction_type=transaction.transaction_type,
            category_id=transaction.category_id,
            category_name=category.name if category else None,
            category_color=category.color if category else None,
            date=transaction.date,
            notes=transaction.notes,
            ai_categorized=transaction.ai_categorized,
            created_at=transaction.created_at
        ))
    
    return result

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Get category info
    category = None
    if transaction.category_id:
        category = db.query(Category).filter(Category.id == transaction.category_id).first()
    
    return TransactionResponse(
        id=transaction.id,
        amount=transaction.amount,
        description=transaction.description,
        transaction_type=transaction.transaction_type,
        category_id=transaction.category_id,
        category_name=category.name if category else None,
        category_color=category.color if category else None,
        date=transaction.date,
        notes=transaction.notes,
        ai_categorized=transaction.ai_categorized,
        created_at=transaction.created_at
    )

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Validate category belongs to user if provided
    if transaction_data.category_id:
        category = db.query(Category).filter(
            Category.id == transaction_data.category_id,
            Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Update transaction
    update_data = transaction_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    
    # Get category info for response
    category = None
    if transaction.category_id:
        category = db.query(Category).filter(Category.id == transaction.category_id).first()
    
    return TransactionResponse(
        id=transaction.id,
        amount=transaction.amount,
        description=transaction.description,
        transaction_type=transaction.transaction_type,
        category_id=transaction.category_id,
        category_name=category.name if category else None,
        category_color=category.color if category else None,
        date=transaction.date,
        notes=transaction.notes,
        ai_categorized=transaction.ai_categorized,
        created_at=transaction.created_at
    )

@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    db.delete(transaction)
    db.commit()
    
    return {"message": "Transaction deleted successfully"}

@router.get("/summary/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get date range for current month
    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get total income and expenses for current month
    income_result = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "income",
        Transaction.date >= start_of_month
    ).scalar() or 0
    
    expense_result = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        Transaction.date >= start_of_month
    ).scalar() or 0
    
    # Get category summaries for expenses
    category_summaries = db.query(
        Transaction.category_id,
        Category.name.label('category_name'),
        Category.color.label('category_color'),
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count')
    ).outerjoin(Category, Transaction.category_id == Category.id).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        Transaction.date >= start_of_month
    ).group_by(Transaction.category_id, Category.name, Category.color).all()
    
    # Format category summaries
    formatted_summaries = []
    for summary in category_summaries:
        formatted_summaries.append(CategorySummary(
            category_id=summary.category_id,
            category_name=summary.category_name or "Uncategorized",
            category_color=summary.category_color or "#6B7280",
            total_amount=float(summary.total_amount),
            transaction_count=summary.transaction_count
        ))
    
    # Get recent transactions (last 10)
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.date.desc()).limit(10).all()
    
    # Format recent transactions
    formatted_transactions = []
    for transaction in recent_transactions:
        category = None
        if transaction.category_id:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
        
        formatted_transactions.append(TransactionResponse(
            id=transaction.id,
            amount=transaction.amount,
            description=transaction.description,
            transaction_type=transaction.transaction_type,
            category_id=transaction.category_id,
            category_name=category.name if category else None,
            category_color=category.color if category else None,
            date=transaction.date,
            notes=transaction.notes,
            ai_categorized=transaction.ai_categorized,
            created_at=transaction.created_at
        ))
    
    return DashboardSummary(
        total_income=float(income_result),
        total_expenses=float(expense_result),
        net_amount=float(income_result - expense_result),
        category_summaries=formatted_summaries,
        recent_transactions=formatted_transactions
    ) 