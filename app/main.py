from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
import pandas as pd
import io
from datetime import date
from typing import Optional

from app.models import Base, PayrollEntry
from app.database import engine, get_db
from app.schemas import PayrollCreate, PayrollResponse
from app.services.tax_calc import TaxCalculator


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title = "Nanny Automated Payroll Profiler",
    version = "0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/payroll", response_model=list[PayrollResponse])
def list_payroll_entries(db: Session = Depends(get_db)):
    """
    List all payroll entries.
    """
    return db.query(PayrollEntry).all()

@app.get("/payroll/export-csv")
def export_payroll_csv(
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """
    Export payroll entries to a CSV file.
    """
    query = db.query(PayrollEntry)
    if start_date:
        query = query.filter(PayrollEntry.week_end_date >= start_date)
    if end_date:
        query = query.filter(PayrollEntry.week_end_date <= end_date)
    
    entries = query.order_by(PayrollEntry.week_end_date).all()

    if not entries:
        raise HTTPException(status_code=404, detail="No payroll entries found in the specified date range.")

    # Convert to pandas DataFrame
    df = pd.DataFrame([entry.__dict__ for entry in entries])
    # Drop SQLAlchemy internal state
    df = df.drop(columns=['_sa_instance_state'])

    # Create an in-memory CSV file
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=payroll_export.csv"}
    )
    
    return response

@app.post("/payroll", response_model=PayrollResponse)
def create_payroll(
    *,
    db: Session = Depends(get_db),
    payroll_in: PayrollCreate,
):
    """
    Create a new payroll entry.
    """
    # 1. Get the last payroll entry to find cumulative totals
    last_entry = db.query(PayrollEntry).order_by(desc(PayrollEntry.week_end_date)).first()

    # 2. Calculate all taxes and new totals
    calculator = TaxCalculator()
    calculated_data = calculator.calculate_all_payroll_data(
        gross_pay=payroll_in.gross_pay,
        last_entry=last_entry
    )

    # 3. Create the new payroll entry object
    new_entry_data = payroll_in.model_dump()
    new_entry_data.update(calculated_data)
    
    db_entry = PayrollEntry(**new_entry_data)

    # 4. Add to session and commit
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    return db_entry

    
    