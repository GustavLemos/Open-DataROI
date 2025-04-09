import streamlit as st 
import requests
import plotly.graph_objects as go
import base64

st.set_page_config(page_title="ROI Estimator", layout="wide")
st.title("📊 ROI Estimator for Data Initiatives")

# Slider para tempo de projeção
projection_months = st.slider("📆 Projection Timeframe (months)", 12, 120, 60)

# Templates
TEMPLATES = {
    "Realistic": {
        "name": "Realistic example",
        "investment_cost": 10000,
        "monthly_operational_cost": 2000,
        "num_people": 3,
        "development_months": 4,
        "monthly_return_estimate": 5000,
        "time_to_results_months": 6,
        "technologies": ["Python", "BigQuery"]
    },
    "Optimistic": {
        "name": "Optimistic example",
        "investment_cost": 9000,
        "monthly_operational_cost": 1800,
        "num_people": 2,
        "development_months": 3,
        "monthly_return_estimate": 6000,
        "time_to_results_months": 4,
        "technologies": ["Python", "BigQuery"]
    },
    "Pessimistic": {
        "name": "Pessimistic example",
        "investment_cost": 12000,
        "monthly_operational_cost": 2500,
        "num_people": 4,
        "development_months": 6,
        "monthly_return_estimate": 4000,
        "time_to_results_months": 8,
        "technologies": ["Python", "BigQuery"]
    }
}

# Seleção de cenários
selected_templates = st.multiselect("Select scenarios to simulate:", list(TEMPLATES.keys()), default=list(TEMPLATES.keys()))

# Lista para os dados dos cenários
scenarios = []

# Formulário de cada cenário selecionado
for key in selected_templates:
    with st.expander(f"🔧 Customize {key} Scenario"):
        tpl = TEMPLATES[key]
        name = st.text_input(f"{key} - Project Name", value=tpl["name"])
        investment = st.number_input(f"{key} - Initial Investment (R$)", value=tpl["investment_cost"])
        monthly = st.number_input(f"{key} - Monthly Operational Cost (R$)", value=tpl["monthly_operational_cost"])
        people = st.number_input(f"{key} - Number of People", value=tpl["num_people"], step=1)
        dev_months = st.slider(f"{key} - Development Months", 1, 24, tpl["development_months"])
        monthly_return = st.number_input(f"{key} - Estimated Monthly Return (R$)", value=tpl["monthly_return_estimate"])
        results_time = st.slider(f"{key} - Months Until Results", 1, 36, tpl["time_to_results_months"])
        techs = st.text_input(f"{key} - Technologies", value=", ".join(tpl["technologies"]))

        scenarios.append({
            "name": name,
            "investment_cost": investment,
            "monthly_operational_cost": monthly,
            "num_people": int(people),
            "development_months": dev_months,
            "monthly_return_estimate": monthly_return,
            "time_to_results_months": results_time,
            "technologies": [t.strip() for t in techs.split(",") if t.strip()]
        })

# Botão de cálculo
if st.button("Calculate ROI"):
    response = requests.post(f"http://localhost:8000/calculate?projection_months={projection_months}", json=scenarios)

    if response.ok:
        data = response.json()

        col1, col2 = st.columns(2)
        chart_data = []

        for result in data:
            name = result["name"]
            with col1:
                st.subheader(name)
                st.metric("ROI (%)", f"{result['roi'] * 100:.2f}%")
                st.metric("Break-even (months)", result['break_even_month'])
                st.metric("Total Cost (R$)", f"{result['total_cost']:.2f}")
                st.metric("Total Return (R$)", f"{result['total_return']:.2f}")

            roi_over_time = []
            for i, profit in enumerate(result["monthly_profits"]):
                investment = result["total_cost"]
                roi = (profit / investment) * 100 if investment > 0 else 0
                roi_over_time.append(roi)
            
            chart_data.append((name, roi_over_time))

        fig = go.Figure()
        for name, roi_list in chart_data:
            fig.add_trace(go.Scatter(
                x=list(range(1, len(roi_list) + 1)),
                y=roi_list,
                mode="lines+markers",
                name=name
            ))

        fig.update_layout(
            title="ROI Over Time (%)",
            xaxis_title="Months",
            yaxis_title="ROI (%)",
            height=500
        )
        with col2:
            st.plotly_chart(fig)

        st.markdown("### 📄 Export Results")
        colpdf, colcsv = st.columns(2)

        with colpdf:
            pdf_resp = requests.post(
                f"http://localhost:8000/export/pdf?projection_months={projection_months}",
                json=scenarios
            )
            if pdf_resp.ok:
                pdf_bytes = pdf_resp.content
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name="roi_report.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("❌ Failed to generate PDF.")

        with colcsv:
            csv_resp = requests.post(
                f"http://localhost:8000/export/csv?projection_months={projection_months}",
                json=scenarios
            )

            if csv_resp.ok:
                csv_str = csv_resp.text
                st.download_button(
                    label="📈 Download CSV File",
                    data=csv_str,
                    file_name="roi_data.csv",
                    mime="text/csv"
                )
            else:
                st.error("❌ Failed to generate CSV.")