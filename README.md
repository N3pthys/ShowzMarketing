## PSet4_Showz_Marketing

This project analyzes marketing performance and user behavior data for a fictional company called Showz. The analysis uses cleaned data from visits, orders, and marketing costs, producing valuable KPIs like:

- DAU, WAU, MAU (Daily, Weekly, Monthly Active Users)
- Conversion Rates
- Customer Acquisition Cost (CAC)
- Return on Marketing Investment (ROMI)
- Customer Lifetime Value (LTV)
- Cohort Retention and Revenue Patterns

## Project Structure

 data/
    raw/ archivos originales CSV
    interim/ datos limpios intermedios
    processed/ tablas agregadas para modelado
notebooks/
    PSet4_Showz_Marketing.ipynb
src/
    data_prep.py funciones de carga y limpieza
    metrics.py funciones de KPI y cohortes
    viz.py utilidades de visualización
reports/
    figures/ imágenes generadas
    executive_summary.md
requirements.txt librerías (pandas, numpy, matplotlib, seaborn, etc.)
.gitignore
README.md

## ▶️ How to Run

1. Install required packages:
    pip install -r requirements.txt
2. To generate all tables and visualizations:
    python src/data_aggregate.py
3. Or open and run the Jupyter notebook:
    jupyter notebook PSet4_Showz_Marketing.ipynb


## Outputs
- cohort_table.csv and ltv_table.csv: Cohort-based user and revenue tables
- marketing_summary.csv: Total cost per channel
- cohort_heatmap.png: Visual of user retention by cohort
- ltv_chart.png: Customer lifetime value by month

## Tools Used
- Python (Pandas, NumPy, Matplotlib, Seaborn)
- Jupyter Notebook
- CSV-based data processing


