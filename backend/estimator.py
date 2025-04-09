from typing import List, Dict
import csv
import io
from fpdf import FPDF

class DataInitiativeROI:
    def __init__(
        self,
        investment_cost: float,
        monthly_operational_cost: float,
        num_people: int,
        development_months: int,
        monthly_return_estimate: float,
        time_to_results_months: int,
        technologies: List[str] = []
    ):
        self.investment_cost = investment_cost
        self.monthly_operational_cost = monthly_operational_cost
        self.num_people = num_people
        self.development_months = development_months
        self.monthly_return_estimate = monthly_return_estimate
        self.time_to_results_months = time_to_results_months
        self.technologies = technologies

    def total_cost(self) -> float:
        return self.investment_cost + (self.monthly_operational_cost * self.development_months)

    def estimate_roi(self, projection_months: int = 24) -> Dict[str, float]:
        total_cost = self.total_cost()
        profit_months = max(projection_months - self.time_to_results_months, 0)
        total_return = profit_months * self.monthly_return_estimate
        roi = (total_return - total_cost) / total_cost if total_cost else 0

        return {
            "total_cost": total_cost,
            "total_return": total_return,
            "roi": roi,
            "break_even_month": self._calculate_break_even_month()
        }

    def _calculate_break_even_month(self) -> int:
        cumulative_profit = 0
        cumulative_cost = self.investment_cost

        for month in range(1, 61):  # até 5 anos
            if month <= self.development_months:
                cumulative_cost += self.monthly_operational_cost
            elif month >= self.time_to_results_months:
                cumulative_profit += self.monthly_return_estimate - self.monthly_operational_cost
            else:
                cumulative_cost += self.monthly_operational_cost

            if cumulative_profit >= cumulative_cost:
                return month
        return -1

    def export_to_csv(self, projection_months: int = 24) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Mês", "Lucro Acumulado"])

        profit = 0
        cost = self.investment_cost

        for i in range(1, projection_months + 1):
            if i <= self.development_months:
                cost += self.monthly_operational_cost
            elif i >= self.time_to_results_months:
                profit += self.monthly_return_estimate - self.monthly_operational_cost
            else:
                cost += self.monthly_operational_cost

            writer.writerow([i, profit - cost])

        return output.getvalue()

    def export_to_pdf(self, roi_result: Dict[str, float]) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Relatório de ROI", ln=True, align='C')
        pdf.ln(10)

        for key, value in roi_result.items():
            pdf.cell(200, 10, txt=f"{key.replace('_', ' ').capitalize()}: {value:.2f}", ln=True)

        return pdf.output(dest='S').encode('latin1')
