![Logo do Open DataROI](img/logo.png)


Open-source tool to quickly estimate the ROI of data projects based on investment costs, development time, and expected returns. Ideal for managers and data professionals.

## 📦 Features
- ROI calculation based on minimal inputs
- FastAPI backend to use as a service
- Interactive interface using Streamlit
- Return and break-even visualization with charts
- Easy deployment with Docker Compose
- Automated tests using Pytest
- Scenario simulations: optimistic, realistic, pessimistic
- Pre-filled use case templates for quick ROI assessments

## ▶️ How to Run Locally

### Backend (FastAPI)
```bash
cd backend
uvicorn main:app --reload
```

### Frontend (Streamlit)
```bash
cd frontend
streamlit run app.py
```

### Using Docker
```bash
docker-compose up --build
```

Access:
- http://localhost:8501 for the dashboard
- http://localhost:8000/docs to test the API

## ✅ Automated Testing
To run tests for core ROI logic:

```bash
pytest tests/
```

Tests cover basic scenarios for ROI calculation, total cost, and break-even point.

## ✨ Contributions
Pull requests are welcome! Open an issue to suggest improvements.

## 📤 Exporting Results

You can export ROI data in two formats:

### 📄 PDF
- Endpoint: `POST /export/pdf`
- Description: returns a formatted report with key ROI metrics

### 📊 CSV
- Endpoint: `POST /export/csv`
- Description: returns a CSV file with cumulative profit month by month

#### Example Payload (JSON)

```json
{
  "scenarios": [
    {
      "name": "realistic",
      "investment_cost": 10000,
      "monthly_operational_cost": 2000,
      "num_people": 3,
      "development_months": 4,
      "monthly_return_estimate": 5000,
      "time_to_results_months": 6,
      "technologies": ["Python", "BigQuery"]
    },
    {
      "name": "optimistic",
      "investment_cost": 9000,
      "monthly_operational_cost": 1800,
      "num_people": 2,
      "development_months": 3,
      "monthly_return_estimate": 6000,
      "time_to_results_months": 4,
      "technologies": ["Python", "BigQuery"]
    },
    {
      "name": "pessimistic",
      "investment_cost": 12000,
      "monthly_operational_cost": 2500,
      "num_people": 4,
      "development_months": 6,
      "monthly_return_estimate": 4000,
      "time_to_results_months": 8,
      "technologies": ["Python", "BigQuery"]
    }
  ]
}
```

## 🛠 Requirements

Make sure to install the project dependencies:

```bash
pip install -r requirements.txt
```

### requirements.txt
```
fastapi==0.110.0
uvicorn==0.29.0
pydantic==2.6.4
streamlit==1.32.2
matplotlib==3.8.3
requests==2.31.0
fpdf==1.7.2
pytest==8.1.1
plotly==5.21.0
```

---

## 📄 License
MIT License
