# AgroShield AI – Climate Risk Intelligent System

AgroShield AI is an applied Agritech project that uses Artificial Intelligence and data-driven analytics
to predict climate risk, mitigate agricultural losses, and support decision-making for farms.

This repository is part of a professional portfolio that combines **Agribusiness Management** and
**Software Engineering**, with focus on food security, reduction of waste, and resilience to extreme weather.

## Purpose

- Help producers and cooperatives anticipate climate events (drought, frost, heavy rain).
- Estimate potential yield loss and financial impact.
- Support the design of preventive strategies and smarter resource allocation.

## Main Features (roadmap)

- Climate data ingestion (NOAA, INMET, satellite).
- Data cleaning and feature engineering for agricultural use.
- Machine Learning models for climate risk and yield loss prediction.
- REST API (FastAPI) to expose predictions.
- Web dashboard for visualization and alerts.
- Automatic reports for farm managers and stakeholders.

## Tech Stack

- Python (Pandas, NumPy, Scikit-learn)
- FastAPI + Uvicorn
- PostgreSQL (or SQLite for local development)
- Docker (optional, for deployment)
- React/Next.js (for the future dashboard – `src/dashboard/`)

## Quickstart

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/AgroShield-AI.git
   cd AgroShield-AI
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate   # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the API (development mode):
   ```bash
   uvicorn src.api.main:app --reload
   ```

5. Open in your browser:
   - API docs: http://127.0.0.1:8000/docs

## Repository Structure

```text
AgroShield-AI/
├── data/
│   ├── raw/          # Raw climate and production data
│   ├── processed/    # Cleaned and engineered data
│   └── samples/      # Small demo datasets
├── src/
│   ├── api/          # FastAPI application
│   ├── models/       # ML models and training code
│   ├── dashboard/    # Future web frontend (React/Next.js)
│   └── services/     # Auxiliary services (alerts, reports, etc.)
├── notebooks/        # Jupyter notebooks (EDA, modeling, experiments)
├── docs/             # Whitepaper, technical notes, architecture
├── README.md
├── roadmap.md
├── requirements.txt
└── .gitignore
```

## License

This project is released under the MIT License. Feel free to adapt and extend for research,
portfolio, and practical applications in Agribusiness.
