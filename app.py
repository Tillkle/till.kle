import streamlit as st
import pandas as pd

st.title("🌱 CSO vs Individual Comparison App")

st.markdown("Upload the CSO and Individual CSV files:")

cso_file = st.file_uploader("📤 Upload CSO CSV", type=["csv"])
indi_file = st.file_uploader("📤 Upload Individual CSV", type=["csv"])

if cso_file and indi_file:
    # Load and clean
    cso_df = pd.read_csv(cso_file)
    indi_df = pd.read_csv(indi_file)
    cso_df.columns = cso_df.columns.str.strip()
    indi_df.columns = indi_df.columns.str.strip()

    # --- Plant Comparison ---
    try:
        cso_plants = cso_df[['Type', 'Quantity']].dropna()
        indi_plants = indi_df[['Type', 'Quantity']].dropna()

        cso_plants['Quantity'] = pd.to_numeric(cso_plants['Quantity'], errors='coerce').fillna(0)
        indi_plants['Quantity'] = pd.to_numeric(indi_plants['Quantity'], errors='coerce').fillna(0)

        cso_summary = cso_plants.groupby('Type', as_index=False).sum()
        indi_summary = indi_plants.groupby('Type', as_index=False).sum()

        plant_comparison = pd.merge(cso_summary, indi_summary, on='Type', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
        plant_comparison['Difference'] = plant_comparison['Quantity_Individual'] - plant_comparison['Quantity_CSO']

        plant_total = pd.DataFrame([{
            'Type': 'TOTAL Plants',
            'Quantity_CSO': plant_comparison['Quantity_CSO'].sum(),
            'Quantity_Individual': plant_comparison['Quantity_Individual'].sum(),
            'Difference': plant_comparison['Difference'].sum()
        }])
        plant_comparison = pd.concat([plant_comparison, plant_total], ignore_index=True)

        st.subheader("🌿 Plant Comparison")
        st.dataframe(plant_comparison)
    except Exception as e:
        st.error(f"Error processing plant data: {e}")

    # --- Activity Comparison ---
    try:
        cso_activity = cso_df[['Activity', 'Quantity']].dropna()
        indi_activity = indi_df[['Activity', 'Quantity']].dropna()

        cso_activity['Quantity'] = pd.to_numeric(cso_activity['Quantity'], errors='coerce').fillna(0)
        indi_activity['Quantity'] = pd.to_numeric(indi_activity['Quantity'], errors='coerce').fillna(0)

        cso_act_summary = cso_activity.groupby('Activity', as_index=False).sum()
        indi_act_summary = indi_activity.groupby('Activity', as_index=False).sum()

        act_comparison = pd.merge(cso_act_summary, indi_act_summary, on='Activity', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
        act_comparison['Difference'] = act_comparison['Quantity_Individual'] - act_comparison['Quantity_CSO']

        act_total = pd.DataFrame([{
            'Activity': 'TOTAL Hours',
            'Quantity_CSO': act_comparison['Quantity_CSO'].sum(),
            'Quantity_Individual': act_comparison['Quantity_Individual'].sum(),
            'Difference': act_comparison['Difference'].sum()
        }])
        act_comparison = pd.concat([act_comparison, act_total], ignore_index=True)

        st.subheader("⏱️ Activity Hours Comparison")
        st.dataframe(act_comparison)
    except Exception as e:
        st.error(f"Error processing activity data: {e}")



