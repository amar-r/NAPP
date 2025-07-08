"""
NAPP - Nanny Automated Payroll Profiler

Main FastAPI application that provides:
- API endpoints for payroll management
- Frontend interface using FastHTML
- Database integration
- Tax calculation services
"""

from fastapi import FastAPI, Depends, Form as FastApiForm, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
from typing import List, Optional
import json

from app.database import get_db, engine
from app.models import Base, PayrollEntry
from app.schemas import PayrollCreate, PayrollResponse
from app.api.payroll import router as payroll_router
from app.frontend.pages import get_home_page, get_home_page_html
from fastcore.xml import to_xml
from app.services.tax_calculator import TaxCalculator

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="NAPP - Nanny Automated Payroll Profiler",
    description="Comprehensive nanny payroll management with tax calculations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API routers
app.include_router(payroll_router, prefix="/api/payroll", tags=["payroll"])

# Test route to debug FastHTML
@app.get("/test", response_class=HTMLResponse)
def test_page():
    """Test page to debug FastHTML rendering."""
    from fasthtml.common import H1, P, Div
    
    test_content = Div(
        H1("Test Page"),
        P("This is a test to see if FastHTML is working."),
        P("If you can see this, FastHTML is working correctly.")
    )
    
    return to_xml(test_content)

@app.post("/test", response_class=HTMLResponse)
def test_post():
    """Test POST handler."""
    return HTMLResponse(content="<h1>Form submitted successfully!</h1><p>FastHTML forms are working!</p>")

@app.get("/", response_class=HTMLResponse)
def home(db: Session = Depends(get_db)):
    """Main home page with payroll management interface."""
    entries = db.query(PayrollEntry).order_by(desc(PayrollEntry.week_end_date)).all()
    return HTMLResponse(content=get_home_page_html(entries))

@app.get("/debug", response_class=HTMLResponse)
def debug_home(db: Session = Depends(get_db)):
    """Debug route to see what to_xml produces."""
    entries = db.query(PayrollEntry).order_by(desc(PayrollEntry.week_end_date)).all()
    home_page = get_home_page(entries)
    xml_output = to_xml(home_page)
    
    # Return the raw XML output for debugging
    return HTMLResponse(content=f"""
    <html>
    <head><title>Debug Output</title></head>
    <body>
        <h1>Debug: Raw XML Output</h1>
        <pre>{xml_output}</pre>
    </body>
    </html>
    """)

@app.post("/payroll/new", response_class=HTMLResponse)
def create_payroll_from_form(
    request: Request,
    db: Session = Depends(get_db),
    week_start_date: date = FastApiForm(...),
    week_end_date: date = FastApiForm(...),
    gross_pay: float = FastApiForm(...),
    notes: str = FastApiForm(None)
):
    """
    Create a new payroll entry from the frontend form.
    Returns updated table content for AJAX replacement.
    """
    # Validate dates
    if week_end_date <= week_start_date:
        return HTMLResponse(
            content='<div class="message error">Week end date must be after week start date</div>',
            status_code=400
        )
    
    # Get the last entry for cumulative calculations
    last_entry = db.query(PayrollEntry).order_by(desc(PayrollEntry.week_end_date)).first()
    
    # Calculate all tax amounts
    calculator = TaxCalculator()
    calculated_data = calculator.calculate_all_payroll_data(
        gross_pay=gross_pay,
        last_entry=last_entry
    )
    
    # Create the new entry
    entry_data = {
        'week_start_date': week_start_date,
        'week_end_date': week_end_date,
        'gross_pay': gross_pay,
        'notes': notes
    }
    entry_data.update(calculated_data)
    
    db_entry = PayrollEntry(**entry_data)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    # Get updated entries for the table
    entries = db.query(PayrollEntry).order_by(desc(PayrollEntry.week_end_date)).all()
    
    # Generate table rows with checkboxes
    table_rows = ""
    for entry in entries:
        # Calculate total federal tax
        total_federal_tax = entry.federal_income_tax + entry.federal_social_security_tax + entry.federal_medicare_tax
        # Calculate total state tax
        total_state_tax = entry.virginia_income_tax + entry.virginia_unemployment_tax
        
        table_rows += f"""
        <tr>
            <td class="checkbox-cell">
                <input type="checkbox" name="entry_ids" value="{entry.id}" onchange="updateDeleteButton()">
            </td>
            <td>{entry.week_start_date}</td>
            <td>{entry.week_end_date}</td>
            <td style="text-align: right;">${entry.gross_pay:,.2f}</td>
            <td style="text-align: right;">${total_federal_tax:,.2f}</td>
            <td style="text-align: right;">${total_state_tax:,.2f}</td>
            <td style="text-align: right;">${entry.net_pay:,.2f}</td>
            <td>{entry.notes or ''}</td>
        </tr>
        """
    
    # Return just the table section for AJAX update
    table_html = f"""
    <div class="table-box">
        <h2>Payroll History</h2>
        <div class="table-actions">
            <button class="export-btn" onclick="exportToCSV()">
                Export to CSV
            </button>
            <button class="export-btn secondary" onclick="exportToJSON()">
                Export to JSON
            </button>
            <button id="deleteSelectedBtn" class="delete-btn" onclick="deleteSelectedEntries()" disabled>
                Delete Selected ({len(entries)} entries)
            </button>
        </div>
        <table>
            <thead>
                <tr>
                    <th class="checkbox-cell">
                        <input type="checkbox" onclick="toggleAllEntries(this)">
                    </th>
                    <th>Week Start</th>
                    <th>Week End</th>
                    <th style="text-align: right;">Gross Pay</th>
                    <th style="text-align: right;">Federal Tax</th>
                    <th style="text-align: right;">State Tax</th>
                    <th style="text-align: right;">Net Pay</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    """
    
    return HTMLResponse(content=table_html)

@app.post("/payroll/delete")
async def delete_payroll_entries(request: Request, db: Session = Depends(get_db)):
    """Delete multiple payroll entries by their IDs."""
    try:
        # Parse the JSON body
        body = await request.json()
        entry_ids = body.get("entry_ids", [])
        
        if not entry_ids:
            return JSONResponse(
                content={"success": False, "message": "No entry IDs provided"},
                status_code=400
            )
        
        # Delete the entries
        deleted_count = 0
        for entry_id in entry_ids:
            entry = db.query(PayrollEntry).filter(PayrollEntry.id == entry_id).first()
            if entry:
                db.delete(entry)
                deleted_count += 1
        
        db.commit()
        
        return JSONResponse(
            content={
                "success": True, 
                "message": f"Successfully deleted {deleted_count} entries",
                "deleted_count": deleted_count
            }
        )
        
    except Exception as e:
        db.rollback()
        return JSONResponse(
            content={"success": False, "message": f"Error deleting entries: {str(e)}"},
            status_code=500
        )

@app.get("/payroll/export-csv")
def export_csv_from_frontend(
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_gross_pay: Optional[float] = None,
    max_gross_pay: Optional[float] = None,
    entry_ids: Optional[str] = None
):
    """Export CSV from frontend filters or selected entries."""
    from app.api.payroll import export_payroll_csv
    
    # If entry_ids provided, filter by those specific IDs
    if entry_ids:
        try:
            ids = [int(id.strip()) for id in entry_ids.split(',') if id.strip()]
            entries = db.query(PayrollEntry).filter(PayrollEntry.id.in_(ids)).all()
            
            # Create CSV content manually for selected entries
            import csv
            from io import StringIO
            from fastapi.responses import Response
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Week Start', 'Week End', 'Gross Pay', 'Federal Income Tax',
                'Federal Social Security Tax', 'Federal Medicare Tax', 'Federal Unemployment Tax',
                'Virginia Income Tax', 'Virginia Unemployment Tax', 'Net Pay', 'Total Taxes',
                'Total Cost', 'Notes'
            ])
            
            # Write data rows
            for entry in entries:
                writer.writerow([
                    entry.week_start_date,
                    entry.week_end_date,
                    entry.gross_pay,
                    entry.federal_income_tax,
                    entry.federal_social_security_tax,
                    entry.federal_medicare_tax,
                    entry.federal_unemployment_tax,
                    entry.virginia_income_tax,
                    entry.virginia_unemployment_tax,
                    entry.net_pay,
                    entry.total_taxes,
                    entry.total_cost,
                    entry.notes or ''
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=payroll_entries.csv"}
            )
            
        except Exception as e:
            return JSONResponse(
                content={"error": f"Error exporting selected entries: {str(e)}"},
                status_code=500
            )
    
    # Otherwise use the existing filter-based export
    return export_payroll_csv(
        start_date=start_date,
        end_date=end_date,
        min_gross_pay=min_gross_pay,
        max_gross_pay=max_gross_pay,
        db=db
    )

@app.get("/payroll/export-json")
def export_json_from_frontend(
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_gross_pay: Optional[float] = None,
    max_gross_pay: Optional[float] = None,
    entry_ids: Optional[str] = None
):
    """Export JSON from frontend filters or selected entries."""
    from app.api.payroll import export_payroll_json
    
    # If entry_ids provided, filter by those specific IDs
    if entry_ids:
        try:
            ids = [int(id.strip()) for id in entry_ids.split(',') if id.strip()]
            entries = db.query(PayrollEntry).filter(PayrollEntry.id.in_(ids)).all()
            
            # Convert entries to JSON-serializable format
            data = []
            for entry in entries:
                data.append({
                    'id': entry.id,
                    'week_start_date': str(entry.week_start_date),
                    'week_end_date': str(entry.week_end_date),
                    'gross_pay': entry.gross_pay,
                    'federal_income_tax': entry.federal_income_tax,
                    'federal_social_security_tax': entry.federal_social_security_tax,
                    'federal_medicare_tax': entry.federal_medicare_tax,
                    'federal_unemployment_tax': entry.federal_unemployment_tax,
                    'virginia_income_tax': entry.virginia_income_tax,
                    'virginia_unemployment_tax': entry.virginia_unemployment_tax,
                    'net_pay': entry.net_pay,
                    'total_taxes': entry.total_taxes,
                    'total_cost': entry.total_cost,
                    'notes': entry.notes,
                    'created_at': str(entry.created_at) if entry.created_at else None,
                    'updated_at': str(entry.updated_at) if entry.updated_at else None
                })
            
            return JSONResponse(
                content=data,
                headers={"Content-Disposition": "attachment; filename=payroll_entries.json"}
            )
            
        except Exception as e:
            return JSONResponse(
                content={"error": f"Error exporting selected entries: {str(e)}"},
                status_code=500
            )
    
    # Otherwise use the existing filter-based export
    return export_payroll_json(
        start_date=start_date,
        end_date=end_date,
        min_gross_pay=min_gross_pay,
        max_gross_pay=max_gross_pay,
        db=db
    )

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "NAPP - Nanny Automated Payroll Profiler"}

# API documentation redirect
@app.get("/api")
def api_redirect():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    
    