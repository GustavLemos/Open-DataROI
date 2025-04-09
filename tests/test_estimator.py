from backend.estimator import DataInitiativeROI

def test_basic_roi_calculation():
    model = DataInitiativeROI(
        investment_cost=10000,
        monthly_operational_cost=2000,
        num_people=3,
        development_months=3,
        monthly_return_estimate=5000,
        time_to_results_months=4
    )
    result = model.estimate_roi()
    assert result["total_cost"] == 10000 + (3 * 2000)
    assert result["roi"] > 0
    assert result["break_even_month"] > 0
