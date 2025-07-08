# NAPP - Nanny Automated Payroll Profiler

A comprehensive web application for managing nanny payroll with automatic tax calculations for Virginia state and Federal taxes.

## Features

### 🏠 **Modern Web Interface**
- Responsive design with modern UI/UX
- Real-time form submission with auto-refresh
- Interactive data table with sorting and filtering
- Summary statistics dashboard
- **5-Entry Simultaneous Creation** - Create up to 5 payroll entries at once
- **Bulk Operations** - Select and delete multiple entries
- **Export Functionality** - Export selected or all entries to CSV/JSON

### 💰 **Comprehensive Tax Calculations**
- **Federal Taxes**: Income tax, Social Security (FICA), Medicare, Unemployment (FUTA)
- **Virginia State Taxes**: Income tax (5.75%), Unemployment (SUTA)
- **Automatic Calculations**: All taxes calculated automatically on entry creation
- **YTD Tracking**: Cumulative year-to-date amounts for tax limits

### 📊 **Data Management**
- Complete CRUD operations for payroll entries
- Export to CSV and JSON formats
- Advanced filtering by date range and amount
- Summary statistics and reporting
- **Bulk Delete** - Select multiple entries for deletion
- **Smart Export** - Export all entries or selected entries only

### 🔌 **RESTful API**
- Full REST API with comprehensive endpoints
- Swagger/OpenAPI documentation
- Multiple export formats
- Proper error handling and validation

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NAPP
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Advanced Features

### 🚀 **Multiple Entry Creation**
- **Single Entry Mode**: Create one entry at a time
- **Multiple Entry Mode**: Create up to 5 entries simultaneously
- **Dynamic Form Controls**: Add/remove additional forms as needed
- **Sequential Processing**: Entries are created in order for data integrity
- **Smart Validation**: Only validates visible forms

### 🗑️ **Bulk Operations**
- **Checkbox Selection**: Select individual entries or use "Select All"
- **Bulk Delete**: Delete multiple selected entries with confirmation
- **Smart Export**: Export only selected entries or all entries

### 📤 **Export Options**
- **CSV Export**: Complete payroll data with all tax calculations
- **JSON Export**: Full entry data including metadata
- **Filtered Export**: Export based on date ranges and amount filters
- **Selected Export**: Export only checked entries

## Usage

### Web Interface

1. **Create Payroll Entry**
   - Fill out the form with week dates, gross pay, and optional notes
   - Submit to automatically calculate all taxes
   - Table updates in real-time

2. **Create Multiple Entries**
   - Click "Add Multiple Entries" to enable multi-entry mode
   - Use form controls to add up to 5 additional forms
   - Fill out all visible forms
   - Click "Create X Entries" to submit all at once

3. **View Payroll History**
   - Browse all entries in the interactive table
   - Use checkboxes to select entries for bulk operations
   - Use filters to narrow down results
   - Export data in CSV or JSON format

4. **Bulk Operations**
   - Check entries you want to delete or export
   - Use "Delete Selected" to remove multiple entries
   - Use "Export to CSV/JSON" to export selected entries

5. **Export Data**
   - Set date range and amount filters
   - Choose export format (CSV or JSON)
   - Download filtered data

### API Usage

#### Get All Payroll Entries
```bash
curl http://localhost:8000/api/payroll/
```

#### Create New Entry
```bash
curl -X POST http://localhost:8000/api/payroll/ \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2024-01-01",
    "week_end_date": "2024-01-07",
    "gross_pay": 500.00,
    "notes": "Regular week"
  }'
```

#### Export CSV
```bash
curl http://localhost:8000/api/payroll/export/csv?start_date=2024-01-01
```

## Tax Calculation Details

### Federal Taxes (2024)
- **Income Tax**: Progressive brackets (10%, 12%, 22%, 24%, 32%)
- **Social Security**: 6.2% on first $168,600
- **Medicare**: 1.45% on all wages
- **FUTA**: 0.6% on first $7,000 (employer only)

### Virginia State Taxes
- **Income Tax**: 5.75% flat rate
- **SUTA**: 2.71% on first $8,000 (employer only)

## API Endpoints

### Core Endpoints
- `GET /api/payroll/` - List all entries with filtering
- `GET /api/payroll/{id}` - Get single entry
- `POST /api/payroll/` - Create single entry
- `POST /api/payroll/batch` - Create multiple entries
- `PUT /api/payroll/{id}` - Update entry
- `DELETE /api/payroll/{id}` - Delete entry

### Export Endpoints
- `GET /api/payroll/export/csv` - Export to CSV
- `GET /api/payroll/export/json` - Export to JSON
- `GET /api/payroll/summary` - Get summary statistics

### Frontend Routes
- `GET /` - Main web interface
- `POST /payroll/new` - Form submission
- `GET /payroll/export-csv` - Frontend CSV export
- `GET /payroll/export-json` - Frontend JSON export

## Project Structure

```
NAPP/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database configuration
│   ├── config.py               # App configuration
│   ├── api/
│   │   └── payroll.py          # API endpoints
│   ├── services/
│   │   └── tax_calculator.py   # Tax calculation logic
│   └── frontend/
│       └── pages.py            # Web interface
├── tests/                      # Test files
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
isort app/
```

### Database Migrations
The application uses SQLAlchemy with automatic table creation. For production, consider using Alembic for migrations.

## Docker Deployment

### Build and Run
```bash
docker-compose up --build
```

### Production
```bash
docker build -t napp .
docker run -p 8000:8000 napp
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the comprehensive documentation in `AI_did_this.md`

## Roadmap

- [ ] User authentication and authorization
- [ ] Multi-state tax support
- [ ] Advanced reporting and analytics
- [ ] Mobile application
- [ ] Integration with payroll services
- [ ] Automated tax filing assistance 