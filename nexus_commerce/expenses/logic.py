"""
Nexus Commerce Suite — Expense Management Logic
=================================================
Recording and retrieving business overheads.
"""
import logging
import streamlit as st
from ..common.supabase_client import get_supabase_client

logger = logging.getLogger("nexus_commerce.expenses")

def get_all_expenses(limit: int = 100) -> list:
    """Retrieve all expense records ordered by date."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("expenses").select("*") \
            .eq("user_id", st.session_state.get("user_id")) \
            .order("expense_date", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        logger.error("Failed to fetch expenses: %s", e)
        return []

def record_expense(category: str, amount: float, description: str = "", expense_date: str = None) -> dict:
    """Record a new business expense."""
    supabase = get_supabase_client()
    try:
        data = {
            "category": category,
            "amount": amount,
            "description": description,
            "user_id": st.session_state.get("user_id")
        }
        if expense_date:
            data["expense_date"] = expense_date

        response = supabase.table("expenses").insert(data).execute()
        logger.info("Recorded expense: %s - ₹%.2f", category, amount)
        return {"success": True, "message": f"Expense of ₹{amount:,.2f} recorded under '{category}'."}
    except Exception as e:
        logger.error("Failed to record expense: %s", e)
        return {"success": False, "message": f"Error: {e}"}

def get_expense_summary(period_days: int = 30) -> dict:
    """Get total expenses group by category for a period."""
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        start_date = (datetime.now() - timedelta(days=period_days)).date().isoformat()
        
        response = supabase.table("expenses").select("category, amount") \
            .eq("user_id", st.session_state.get("user_id")) \
            .gte("expense_date", start_date).execute()
        if not response.data:
            return {"total": 0, "breakdown": {}}
        
        total = sum(item['amount'] for item in response.data)
        breakdown = {}
        for item in response.data:
            cat = item['category']
            breakdown[cat] = breakdown.get(cat, 0) + item['amount']
            
        return {"total": total, "breakdown": breakdown}
    except Exception as e:
        logger.error("Failed to get expense summary: %s", e)
        return {"total": 0, "breakdown": {}, "error": str(e)}
