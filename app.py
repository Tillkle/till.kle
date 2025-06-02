import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

st.title("CSO vs Individual Comparison")

st.markdown("Upload the **CSO** and **Individual** CSV files below:")

cso_file = st.file_uploader("Upload CSO CSV", type="csv")
indi_file = st.file_uploader("Upload Individual CSV", type="csv")

def create_pdf(df1, df2):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def add_table(title, df):
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=title, ln=True, align='L')
        pdf.set_font("Arial", size=10)
        col_widths = [50, 40, 40, 40]
        header = df.columns.tolist()
        for i, col in enumerate(header):
            pdf.cell(col_widths[i], 10, col, border=1)
        pdf.ln()
        for _, row in df.iterrows():
            for i, col in enumerate(row):
                pdf.cell(col_widths[i], 10, str(col), border=1)
            pdf.ln()

    add_table("🌱 Plant Comparison", df1)
    pdf.ln(5)
    add_table("⏱️ Activity Hours Comparison", df2)

    output = BytesIO()
    pdf.output(output)
    return output.getvalue()

if cso_file and indi_file:
    # Load files
    cso_df = pd.read_csv(cso_file)
    indi_df = pd.read_csv(indi_file)

    # --- Plant Comparison ---
    cso_plants = cso_df.iloc[:, [11, 12]].dropna()
    indi_plants = indi_df.iloc[:, [22, 23]].dropna()

    cso_plants.columns = ['Type', 'Quantity']
    indi_plants.columns = ['Type', 'Quantity']

    cso_plants['Quantity'] = (
        cso_plants['Quantity']
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .astype(float)
    )
    indi_plants['Quantity'] = pd.to_numeric(indi_plants['Quantity'], errors='coerce').fillna(0)

    cso_summary = cso_plants.groupby('Type', as_index=False).sum()
    indi_summary = indi_plants.groupby('Type', as_index=False).sum()

    plant_comparison = pd.merge(cso_summary, indi_summary, on='Type', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
    plant_comparison['Difference'] = plant_comparison['Quantity_Individual'] - plant_comparison['Quantity_CSO']

    total_row = pd.DataFrame([{
        'Type': 'TOTAL Plants',
        'Quantity_CSO': plant_comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': plant_comparison['Quantity_Individual'].sum(),
        'Difference': plant_comparison['Difference'].sum()
    }])
    plant_result = pd.concat([plant_comparison, total_row], ignore_index=True)

    st.markdown("### 🌱 Plant Comparison")
    st.dataframe(plant_result)

    # --- Activity Comparison (including non-planting items) ---
    cso_activities = cso_df.iloc[:, [23, 24]].dropna()
    indi_activities = indi_df.iloc[:, [41, 42]].dropna()

    cso_activities.columns = ['Activity', 'Quantity']
    indi_activities.columns = ['Activity', 'Quantity']

    cso_activities['Quantity'] = pd.to_numeric(cso_activities['Quantity'], errors='coerce').fillna(0)
    indi_activities['Quantity'] = pd.to_numeric(indi_activities['Quantity'], errors='coerce').fillna(0)

    cso_act_summary = cso_activities.groupby('Activity', as_index=False).sum()
    indi_act_summary = indi_activities.groupby('Activity', as_index=False).sum()

    act_comparison = pd.merge(cso_act_summary, indi_act_summary, on='Activity', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
    act_comparison['Difference'] = act_comparison['Quantity_Individual'] - act_comparison['Quantity_CSO']

    act_total = pd.DataFrame([{
        'Activity': 'TOTAL Hours',
        'Quantity_CSO': act_comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': act_comparison['Quantity_Individual'].sum(),
        'Difference': act_comparison['Difference'].sum()
    }])
    act_result = pd.concat([act_comparison, act_total], ignore_index=True)

    st.markdown("### ⏱️ Activity Hours Comparison (incl. non-planting)")
    st.dataframe(act_result)

    # --- PDF Export ---
    pdf_bytes = create_pdf(plant_result, act_result)
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_bytes,
        file_name="comparison_report.pdf",
        mime="application/pdf"
    )

