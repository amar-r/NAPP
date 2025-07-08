"""
Payroll API endpoints

Provides comprehensive CRUD operations for payroll entries:
- Get single payroll entry
- Get all payroll entries with filtering
- Create single payroll entry
- Create multiple payroll entries
- Export data in JSON, CSV, and table formats
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import date
import csv
import io
import json

from app.database import get_db
from app.models import PayrollEntry
from app.schemas import (
    PayrollCreate, 
    PayrollResponse, 
    PayrollUpdate, 
    PayrollList, 
    ExportFilters
)
from app.services.tax_calculator import TaxCalculator

router = APIRouter()

@router.get("/", response_model=List[PayrollResponse])
def get_payroll_entries(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    min_gross_pay: Optional[float] = Query(None, ge=0, description="Minimum gross pay"),
    max_gross_pay: Optional[float] = Query(None, ge=0, description="Maximum gross pay"),
    db: Session = Depends(get_db)
):
    """
    Get all payroll entries with optional filtering.
    
    Supports filtering by date range and gross pay amount.
    """
    query = db.query(PayrollEntry)
    
    # Apply filters
    if start_date:
        query = query.filter(PayrollEntry.week_start_date >= start_date)
    if end_date:
        query = query.filter(PayrollEntry.week_end_date <= end_date)
    if min_gross_pay is not None:
        query = query.filter(PayrollEntry.gross_pay >= min_gross_pay)
    if max_gross_pay is not None:
        query = query.filter(PayrollEntry.gross_pay <= max_gross_pay)
    
    # Order by most recent first
    query = query.order_by(desc(PayrollEntry.week_end_date))
    
    # Apply pagination
    entries = query.offset(skip).limit(limit).all()
    
    return entries

@router.get("/{entry_id}", response_model=PayrollResponse)
def get_payroll_entry(entry_id: int, db: Session = Depends(get_db)):
    """
    Get a single payroll entry by ID.
    """
    entry = db.query(PayrollEntry).filter(PayrollEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Payroll entry not found")
    return entry

@router.post("/", response_model=PayrollResponse)
def create_payroll_entry(payroll: PayrollCreate, db: Session = Depends(get_db)):
    """
    Create a new payroll entry with automatic tax calculations.
    """
    # Get the last entry for cumulative calculations
    last_entry = db.query(PayrollEntry).order_by(desc(PayrollEntry.week_end_date)).first()
    
    # Calculate all tax amounts
    calculator = TaxCalculator()
    calculated_data = calculator.calculate_all_payroll_data(
        gross_pay=payroll.gross_pay,
        last_entry=last_entry
    )
    
    # Create the new entry
    entry_data = payroll.model_dump()
    entry_data.update(calculated_data)
    
    db_entry = PayrollEntry(**entry_data)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry

@router.post("/batch", response_model=List[PayrollResponse])
def create_payroll_entries(payrolls: List[PayrollCreate], db: Session = Depends(get_db)):
    """
    Create multiple payroll entries at once.
    """
    entries = []
    calculator = TaxCalculator()
    
    for payroll in payrolls:
        # Get the last entry for cumulative calculations
        last_entry = db.query(PayrollEntry).order_by(desc(PayrollEntry.week_end_date)).first()
        
        # Calculate all tax amounts
        calculated_data = calculator.calculate_all_payroll_data(
            gross_pay=payroll.gross_pay,
            last_entry=last_entry
        )
        
        # Create the new entry
        entry_data = payroll.model_dump()
        entry_data.update(calculated_data)
        
        db_entry = PayrollEntry(**entry_data)
        db.add(db_entry)
        entries.append(db_entry)
    
    db.commit()
    
    # Refresh all entries to get their IDs
    for entry in entries:
        db.refresh(entry)
    
    return entries

@router.put("/{entry_id}", response_model=PayrollResponse)
def update_payroll_entry(
    entry_id: int, 
    payroll_update: PayrollUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing payroll entry.
    """
    entry = db.query(PayrollEntry).filter(PayrollEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Payroll entry not found")
    
    # Update only provided fields
    update_data = payroll_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    
    # Recalculate taxes if gross pay was updated
    if 'gross_pay' in update_data:
        calculator = TaxCalculator()
        calculated_data = calculator.calculate_all_payroll_data(
            gross_pay=entry.gross_pay,
            last_entry=None  # Would need to get previous entry for proper recalculation
        )
        
        # Update calculated fields
        for field, value in calculated_data.items():
            if hasattr(entry, field):
                setattr(entry, field, value)
    
    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/{entry_id}")
def delete_payroll_entry(entry_id: int, db: Session = Depends(get_db)):
    """
    Delete a payroll entry.
    """
    entry = db.query(PayrollEntry).filter(PayrollEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Payroll entry not found")
    
    db.delete(entry)
    db.commit()
    
    return {"message": "Payroll entry deleted successfully"}

@router.get("/export/csv")
def export_payroll_csv(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    min_gross_pay: Optional[float] = Query(None, ge=0, description="Minimum gross pay"),
    max_gross_pay: Optional[float] = Query(None, ge=0, description="Maximum gross pay"),
    db: Session = Depends(get_db)
):
    """
    Export payroll entries to CSV format with optional filtering.
    """
    query = db.query(PayrollEntry)
    
    # Apply filters
    if start_date:
        query = query.filter(PayrollEntry.week_start_date >= start_date)
    if end_date:
        query = query.filter(PayrollEntry.week_end_date <= end_date)
    if min_gross_pay is not None:
        query = query.filter(PayrollEntry.gross_pay >= min_gross_pay)
    if max_gross_pay is not None:
        query = query.filter(PayrollEntry.gross_pay <= max_gross_pay)
    
    entries = query.order_by(desc(PayrollEntry.week_end_date)).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Week Start Date', 'Week End Date', 'Gross Pay', 'Net Pay', 'Total Cost',
        'Federal Income Tax', 'Federal Social Security Tax', 'Federal Medicare Tax',
        'Federal Unemployment Tax', 'Virginia Income Tax', 'Virginia Unemployment Tax',
        'Total Taxes', 'Notes', 'Created At'
    ])
    
    # Write data
    for entry in entries:
        writer.writerow([
            entry.id, entry.week_start_date, entry.week_end_date,
            f"${entry.gross_pay:,.2f}", f"${entry.net_pay:,.2f}", f"${entry.total_cost:,.2f}",
            f"${entry.federal_income_tax:,.2f}", f"${entry.federal_social_security_tax:,.2f}",
            f"${entry.federal_medicare_tax:,.2f}", f"${entry.federal_unemployment_tax:,.2f}",
            f"${entry.virginia_income_tax:,.2f}", f"${entry.virginia_unemployment_tax:,.2f}",
            f"${entry.total_taxes:,.2f}", entry.notes or '', entry.created_at
        ])
    
    # Return CSV response
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=payroll_entries.csv"}
    )

@router.get("/export/json")
def export_payroll_json(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    min_gross_pay: Optional[float] = Query(None, ge=0, description="Minimum gross pay"),
    max_gross_pay: Optional[float] = Query(None, ge=0, description="Maximum gross pay"),
    db: Session = Depends(get_db)
):
    """
    Export payroll entries to JSON format with optional filtering.
    """
    query = db.query(PayrollEntry)
    
    # Apply filters
    if start_date:
        query = query.filter(PayrollEntry.week_start_date >= start_date)
    if end_date:
        query = query.filter(PayrollEntry.week_end_date <= end_date)
    if min_gross_pay is not None:
        query = query.filter(PayrollEntry.gross_pay >= min_gross_pay)
    if max_gross_pay is not None:
        query = query.filter(PayrollEntry.gross_pay <= max_gross_pay)
    
    entries = query.order_by(desc(PayrollEntry.week_end_date)).all()
    
    # Convert to JSON-serializable format
    json_data = []
    for entry in entries:
        json_data.append({
            'id': entry.id,
            'week_start_date': entry.week_start_date.isoformat(),
            'week_end_date': entry.week_end_date.isoformat(),
            'gross_pay': entry.gross_pay,
            'net_pay': entry.net_pay,
            'total_cost': entry.total_cost,
            'federal_income_tax': entry.federal_income_tax,
            'federal_social_security_tax': entry.federal_social_security_tax,
            'federal_medicare_tax': entry.federal_medicare_tax,
            'federal_unemployment_tax': entry.federal_unemployment_tax,
            'virginia_income_tax': entry.virginia_income_tax,
            'virginia_unemployment_tax': entry.virginia_unemployment_tax,
            'total_taxes': entry.total_taxes,
            'notes': entry.notes,
            'created_at': entry.created_at.isoformat() if entry.created_at else None
        })
    
    return {"entries": json_data, "total_count": len(json_data)}

@router.get("/summary")
def get_payroll_summary(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for payroll entries.
    """
    query = db.query(PayrollEntry)
    
    # Apply filters
    if start_date:
        query = query.filter(PayrollEntry.week_start_date >= start_date)
    if end_date:
        query = query.filter(PayrollEntry.week_end_date <= end_date)
    
    entries = query.all()
    
    if not entries:
        return {
            "total_entries": 0,
            "total_gross_pay": 0.0,
            "total_net_pay": 0.0,
            "total_cost": 0.0,
            "total_taxes": 0.0,
            "average_gross_pay": 0.0
        }
    
    total_gross_pay = sum(entry.gross_pay for entry in entries)
    total_net_pay = sum(entry.net_pay for entry in entries)
    total_cost = sum(entry.total_cost for entry in entries)
    total_taxes = sum(entry.total_taxes for entry in entries)
    
    return {
        "total_entries": len(entries),
        "total_gross_pay": round(total_gross_pay, 2),
        "total_net_pay": round(total_net_pay, 2),
        "total_cost": round(total_cost, 2),
        "total_taxes": round(total_taxes, 2),
        "average_gross_pay": round(total_gross_pay / len(entries), 2)
    }
