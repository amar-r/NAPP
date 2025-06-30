# Nanny Automated Payroll Profiler (NAPP)

A FastAPI backend service for tracking and calculating nanny payroll, including estimated tax calculations, CSV exports, and cumulative totals.

## Project Status

**Work in Progress:** This is a personal project created for the purpose of learning Python, FastAPI, and general backend development concepts. The code is under active development and should be considered a learning exercise.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd NAPP
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`, and the interactive documentation can be found at `http://127.0.0.1:8000/docs`.


## Disclaimer

This project is for educational purposes only. The tax calculations are estimates based on configurable rates and may not be accurate. I am not a financial advisor. Users should consult with a professional for financial advice and use this application at their own risk. 