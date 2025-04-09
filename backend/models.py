from pydantic import BaseModel
from typing import List

class ROIInput(BaseModel):
    name: str
    investment_cost: float
    monthly_operational_cost: float
    num_people: int
    development_months: int
    monthly_return_estimate: float
    time_to_results_months: int
    technologies: List[str] = []