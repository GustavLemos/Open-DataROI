import streamlit as st 
import requests
import plotly.graph_objects as go
import base64

st.set_page_config(page_title="Open DataROI", layout="wide")


col1, col2 = st.columns([1, 5])

with col1:
    st.image("../img/logo2.png", width=240)

with col2:

    # Título centralizado com margem superior
    st.markdown(
        """
        <h1 style='text-align: center; margin-top: 30px; color: #19472f;'>
             ROI Estimator for Data Initiatives
        </h1>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
    <style>

    /* Slider: barra preenchida */
        .stSlider > div[data-baseweb="slider"] > div > div  {
        background: #6ab08b;
        
        
    }
    /* Slider: barra preenchida bolinha */                
    .stSlider > div[data-baseweb="slider"] > div > div > div {
        background: #19472f; /* verde escuro */
    }
    /* Título do slider */
    div[data-testid="stMarkdownContainer"] p,li {
        color: #19472f;
        font-weight: 700;
        font-size: 16px;
    }
    /* Min e Max */
    div[data-testid="stSliderTickBarMin"],
    div[data-testid="stSliderTickBarMax"] {
        background: transparent !important;
        color: #19472f !important;
        font-weight: 600;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# Slider
projection_months = st.slider("📆 Projection Timeframe (months)", 12, 120, 60)

TEMPLATES = {
    "Realistic": {
        "name": "Realistic example",
        "investment_cost": 150000,  # custo inicial de setup, ferramentas, onboarding
        "monthly_operational_cost": 35000,  # equipe de 4-5 pessoas, ferramentas, cloud
        "num_people": 4,
        "development_months": 6,
        "monthly_return_estimate": 50000,  # retorno mensal projetado após implementação
        "time_to_results_months": 7,
        "technologies": ["Python", "dbt", "BigQuery", "Looker"]
    },
    "Optimistic": {
        "name": "Optimistic example",
        "investment_cost": 100000,
        "monthly_operational_cost": 30000,
        "num_people": 3,
        "development_months": 4,
        "monthly_return_estimate": 70000,
        "time_to_results_months": 5,
        "technologies": ["Python", "Spark", "BigQuery", "Streamlit"]
    },
    "Pessimistic": {
        "name": "Pessimistic example",
        "investment_cost": 180000,
        "monthly_operational_cost": 40000,
        "num_people": 5,
        "development_months": 8,
        "monthly_return_estimate": 30000,
        "time_to_results_months": 10,
        "technologies": ["Python", "Airflow", "BigQuery", "Power BI"]
    }
}


# CSS projection timeline
st.markdown("""
    <style>
    /* Container do multiselect */
    div[data-testid="stMultiSelect"] {
        background-color: #f9fafb !important;
        border: 1px solid #236b45 !important;
        border-radius: 8px;
        padding: 5px;
    }

    /* Label acima do multiselect */
    div[data-testid="stMultiSelect"] label {
        font-size: 16px;
        font-weight: 600;
        color: #2c7be5 !important;
    }

    /* Input de texto */
    div[data-testid="stMultiSelect"] input {
        font-size: 12px;
        color: #236b45;
    }

    /* TAGS SELECIONADAS: cor de fundo, texto e borda */
    div[data-testid="stMultiSelect"] span {
        background-color: #236b45 !important;
        color: white !important;
        border-radius: 5px;
        padding: 2px 8px;
        margin-right: 5px;
    }

    /* Ícone de remover (X) */
    div[data-testid="stMultiSelect"] svg {
        fill: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Seleção de cenários
selected_templates = st.multiselect("Select scenarios to simulate:", list(TEMPLATES.keys()), default=list(TEMPLATES.keys()))

# Intro parameters and CSS templates 
st.markdown("""
    <style>
    details {
        background-color: #f0f2f6;
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 15px;
    }

    summary {
        font-size: 18px;
        font-weight: 600;
        color: #236b45;
        cursor: pointer;
    }

    details[open] summary {
        color: #236b45;
    }
    </style>

    <details>
        <summary>📈 ROI Calculation Parameters</summary>
        <br>
            <ul>
                <li>Initial investment: R$ 180,000</li>
                <li>Monthly operational cost: R$ 40,000</li>
                <li>Team size: 5 people</li>
                <li>Project duration: 8 months</li>
                <li>Estimated monthly return: R$ 30,000</li>
                <li>Time to expected results: 10 months</li>
                <li>Technologies: Python, Airflow, BigQuery, Power BI</li>
            </ul>
    </details>
""", unsafe_allow_html=True)

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


# CSS Botão de Cálculo
st.markdown("""
    <style>
    /* Botão */
    div.stButton > button {
        background-color: #6ab08b;
        color: white;
        padding: 0.5em 1.2em;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #276748;
        color: #ffffff;
        cursor: pointer;
    }

    /* Subheader */
    h2 {
        color: #19472f;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }

    /* Card container para métricas e colunas */
    .custom-card {
        background-color: #f0f8f4;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #cce3d4;
    }

    .metric-label {
        font-weight: 600;
        color: #19472f;
        font-size: 16px;
    }

    .metric-value {
        font-size: 22px;
        font-weight: bold;
        color: #19472f;
    }
    </style>
""", unsafe_allow_html=True)


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
        
        #Gráfico comparativo
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