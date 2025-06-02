import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSO vs Individual Comparison", layout="wide")
st.title("🌱 CSO vs Individual Comparison App")

# Upload files
cso_file = st.file_uploader("📤 Upload CSO CSV", type=["csv"])
indi_file = st.file_uploader("📤 Upload Individual CSV", type=["csv"])

if cso_file and indi_file:
    cso_df = pd.read_csv(cso_file)
    indi_df = pd.read_csv(indi_file)

    # Clean up column names
    cso_df.columns = cso_df.columns.str.strip()
    indi_df.columns = indi_df.columns.str.strip()

    st.markdown("### 🧾 Select relevant column names")

    with st.expander("Select Columns for Comparison", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            plant_type_col_cso = st.selectbox("CSO - Plant Type Column", cso_df.columns)
            plant_qty_col_cso = st.selectbox("CSO - Plant Quantity Column", cso_df.columns)
            act_type_col_cso = st.selectbox("CSO - Activity Type Column", cso_df.columns)
            act_qty_col_cso = st.selectbox("CSO - Activity Quantity Column", cso_df.columns)

        with col2:
            plant_type_col_indi = st.selectbox("Individual - Plant Type Column", indi_df.columns)
            plant_qty_col_indi = st.selectbox("Individual - Plant Quantity Column", indi_df.columns)
            act_type_col_indi = st.selectbox("Individual - Activity Type Column", indi_df.columns)
            act_qty_col_indi = st.selectbox("Individual - Activity Quantity Column", indi_df.columns)

    # --- Plant Comparison ---
    cso_plants = cso_df[[plant_type_col_cso, plant_qty_col_cso]].dropna()
    indi_plants = indi_df[[plant_type_col_indi, plant_qty_col_indi]].dropna()

    cso_plants.columns = ['Type', 'Quantity']
    indi_plants.columns = ['Type', 'Quantity']

    cso_plants['Quantity'] = pd.to_numeric(cso_plants['Quantity'], errors='coerce').fillna(0)
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
    plant_comparison = pd.concat([plant_comparison, total_row], ignore_index=True)

    # --- Activity Comparison ---
    cso_activity = cso_df[[act_type_col_cso, act_qty_col_cso]].dropna()
    indi_activity = indi_df[[act_type_col_indi, act_qty_col_indi]].dropna()

    cso_activity.columns = ['Activity', 'Quantity']
    indi_activity.columns = ['Activity', 'Quantity']

    cso_activity['Quantity'] = pd.to_numeric(cso_activity['Quantity'], errors='coerce').fillna(0)
    indi_activity['Quantity'] = pd.to_numeric(indi_activity['Quantity'], errors='coerce').fillna(0)

    cso_act_summary = cso_activity.groupby('Activity', as_index=False).sum()
    indi_act_summary = indi_activity.groupby('Activity', as_index=False).sum()

    act_comparison = pd.merge(cso_act_summary, indi_act_summary, on='Activity', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
    act_comparison['Difference'] = act_comparison['Quantity_Individual'] - act_comparison['Quantity_CSO']

    act_total_row = pd.DataFrame([{
        'Activity': 'TOTAL Hours',
        'Quantity_CSO': act_comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': act_comparison['Quantity_Individual'].sum(),
        'Difference': act_comparison['Difference'].sum()
    }])
    act_comparison = pd.concat([act_comparison, act_total_row], ignore_index=True)

    # --- Display ---
    st.markdown("## 🌿 Planting Comparison")
    st.dataframe(plant_comparison, use_container_width=True)

    st.markdown("## ⏱️ Activity Hours Comparison")
    st.dataframe(act_comparison, use_container_width=True)

