from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from typing import List
import io
import csv

from estimator import DataInitiativeROI
from models import ROIInput

app = FastAPI()

@app.post("/calculate")
def calculate_roi(inputs: List[ROIInput], projection_months: int = Query(60)):
    results = []
    for scenario in inputs:
        model = DataInitiativeROI(
 
            investment_cost=scenario.investment_cost,
            monthly_operational_cost=scenario.monthly_operational_cost,
            num_people=scenario.num_people,
            development_months=scenario.development_months,
            monthly_return_estimate=scenario.monthly_return_estimate,
            time_to_results_months=scenario.time_to_results_months,
            technologies=scenario.technologies
        )
        roi_data = model.estimate_roi(projection_months)

        # Calcular lucros mensais acumulados
        monthly_profits = []
        profit = 0
        cost = model.investment_cost
        for i in range(1, projection_months + 1):
            if i <= model.development_months:
                cost += model.monthly_operational_cost
            elif i >= model.time_to_results_months:
                profit += model.monthly_return_estimate - model.monthly_operational_cost
            else:
                cost += model.monthly_operational_cost
            monthly_profits.append(profit - cost)

        results.append({
            "name": getattr(scenario, "name", "unknown"),
            "roi": roi_data["roi"],
            "total_cost": roi_data["total_cost"],
            "total_return": roi_data["total_return"],
            "break_even_month": roi_data["break_even_month"],
            "monthly_profits": monthly_profits
        })
    return results

@app.post("/export/pdf")
def export_pdf(inputs: List[ROIInput], projection_months: int = Query(60)):
    results = []
    for scenario in inputs:
        model = DataInitiativeROI(
            investment_cost=scenario.investment_cost,
            monthly_operational_cost=scenario.monthly_operational_cost,
            num_people=scenario.num_people,
            development_months=scenario.development_months,
            monthly_return_estimate=scenario.monthly_return_estimate,
            time_to_results_months=scenario.time_to_results_months,
            technologies=scenario.technologies
        )
        roi_data = model.estimate_roi(projection_months)
        results.append({
            f"{getattr(scenario, 'name', 'unknown')}_roi": roi_data["roi"],
            f"{getattr(scenario, 'name', 'unknown')}_break_even": roi_data["break_even_month"]
        })

    merged = {}
    for r in results:
        merged.update(r)

    dummy_model = DataInitiativeROI(0, 0, 0, 0, 0, 0)
    pdf_bytes = dummy_model.export_to_pdf(merged)

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=roi_report.pdf"})

@app.post("/export/csv")
def export_csv(inputs: List[ROIInput], projection_months: int = Query(60)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Scenario", "Month", "Profit"])

    for scenario in inputs:
        model = DataInitiativeROI(
            investment_cost=scenario.investment_cost,
            monthly_operational_cost=scenario.monthly_operational_cost,
            num_people=scenario.num_people,
            development_months=scenario.development_months,
            monthly_return_estimate=scenario.monthly_return_estimate,
            time_to_results_months=scenario.time_to_results_months,
            technologies=scenario.technologies
        )
        csv_data = model.export_to_csv(projection_months)
        reader = csv.reader(io.StringIO(csv_data))
        next(reader)  # Skip header
        for row in reader:
            writer.writerow([getattr(scenario, "name", "unknown")] + row)

    output.seek(0)
    return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=roi_data.csv"})
