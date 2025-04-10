from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from typing import List
import io
import csv
from estimator import DataInitiativeROI
from models import ROIInput
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from estimator import DataInitiativeROI


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
        scenario_result = {
            "name": getattr(scenario, "name", "Unknown"),
            "roi": roi_data["roi"],
            "break_even": roi_data["break_even_month"],
            "total_cost": roi_data["total_cost"],
            "total_return": roi_data["total_return"],
            "risk_level": _calculate_risk_level(roi_data["roi"]),
            "technologies": scenario.technologies,
            "num_people": scenario.num_people,
            "development_months": scenario.development_months,
            "time_to_results": scenario.time_to_results_months
        }
        results.append(scenario_result)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=20, rightMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("<b>Open Data ROI Report</b>", styles['Title'])
    date = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal'])
    subtitle = Paragraph("This report provides an overview of different data initiative scenarios and their estimated ROI, payback period, and viability.", styles['Normal'])
    elements.extend([title, date, subtitle, Spacer(1, 12)])

    table_data = [["Scenario", "ROI (%)", "Break-even (months)", "Total Cost (R$)", "Total Return (R$)", "Viability"]]
    for result in results:
        break_even_display = result["break_even"] if result["break_even"] >= 0 else "🔴 Not viable"
        table_data.append([
            result["name"],
            f"{result['roi'] * 100:.2f}%",
            break_even_display,
            f"{result['total_cost']:.2f}",
            f"{result['total_return']:.2f}",
            result["risk_level"]
        ])

    col_widths = [100, 80, 120, 120, 130, 180]
    table = Table(table_data, hAlign='LEFT', colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#254d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e6f2e6')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    footer = Paragraph("This report was generated using <b>Open Data ROI</b>.", styles['Italic'])
    elements.extend([Spacer(1, 24), footer])
    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=roi_report.pdf"})


def _calculate_risk_level(roi: float) -> str:
    if roi < 0:
        return "🔴 High Risk (Not viable)"
    elif roi < 1:
        return "🟡 Medium Risk (Moderate viability)"
    else:
        return "🟢 Low Risk (Viable)"

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
