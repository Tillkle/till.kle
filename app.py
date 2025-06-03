import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSO vs Individual Comparison", layout="wide")
st.title("🌱 CSO vs Individual Comparison Tool")

cso_file = st.file_uploader("Upload CSO CSV", type="csv")
indi_file = st.file_uploader("Upload Individual CSV", type="csv")

if cso_file and indi_file:
    cso_df = pd.read_csv(cso_file)
    indi_df = pd.read_csv(indi_file)

    # --- Planting Comparison ---
    cso_plants = cso_df.iloc[:, [19, 20]].dropna()
    cso_plants.columns = ['Type', 'Quantity']

    indi_plants = indi_df.iloc[:, [19, 20]].dropna()
    indi_plants.columns = ['Type', 'Quantity']

    # Clean quantities (remove commas, convert to int)
    cso_plants['Quantity'] = cso_plants['Quantity'].replace({',': ''}, regex=True).astype(int)
    indi_plants['Quantity'] = indi_plants['Quantity'].replace({',': ''}, regex=True).astype(int)

    # Group and compare
    cso_summary = cso_plants.groupby('Type').sum().rename(columns={'Quantity': 'Quantity_CSO'})
    indi_summary = indi_plants.groupby('Type').sum().rename(columns={'Quantity': 'Quantity_Individual'})

    plant_comparison = pd.merge(cso_summary, indi_summary, how='outer', left_index=True, right_index=True).fillna(0)
    plant_comparison['Difference'] = plant_comparison['Quantity_Individual'] - plant_comparison['Quantity_CSO']
    plant_result = plant_comparison.reset_index().sort_values(by='Type')

    st.markdown("### 🌱 Planting Comparison")
    st.dataframe(plant_result)

    # --- Non-Planting Comparison ---
    non_planting_labels = {
        "Tie": "e) Tie (indiv.)",
        "Stake <2m": "f) Stake (indiv.) less than 2m",
        "Stake >2m": "g) Stake (indiv.) more than 2m",
        "Guard 1x": "h) Guard (1x HW/Corflute)",
        "Guard 3x": "i) Guard (3x HW/Corflute)",
        "Marker Bamboo": "l) Bamboo stake marker (indiv.)",
        "Marker Hardwood": "m) Hardwood stake marker (indiv.)"
    }

    indi_np = indi_df.iloc[:, [19, 20]].dropna()
    indi_np.columns = ['Type', 'Quantity']
    indi_np['Quantity'] = indi_np['Quantity'].replace({',': ''}, regex=True).astype(int)
    indi_np['Type'] = indi_np['Type'].replace(non_planting_labels)
    indi_np_summary = indi_np.groupby('Type').sum().rename(columns={'Quantity': 'Quantity_Individual'})

    cso_np = cso_df.iloc[:, [36, 37]].dropna()
    cso_np.columns = ['Type', 'Quantity']
    cso_np['Quantity'] = cso_np['Quantity'].replace({',': ''}, regex=True).astype(int)
    cso_np_summary = cso_np.groupby('Type').sum().rename(columns={'Quantity': 'Quantity_CSO'})

    np_comparison = pd.merge(cso_np_summary, indi_np_summary, how='outer', left_index=True, right_index=True).fillna(0)
    np_comparison['Difference'] = np_comparison['Quantity_Individual'] - np_comparison['Quantity_CSO']
    np_result = np_comparison.reset_index().sort_values(by='Type')

    st.markdown("### 🛠️ Non-Planting Items Comparison")
    st.dataframe(np_result)

    # --- Activity Hours Comparison ---
    cso_act = cso_df.iloc[:, [41, 42]].dropna()
    cso_act.columns = ['Type', 'Hours']
    cso_act['Hours'] = cso_act['Hours'].replace({',': ''}, regex=True).astype(float)
    cso_act_summary = cso_act.groupby('Type').sum().rename(columns={'Hours': 'Hours_CSO'})

    indi_act = indi_df.iloc[:, [41, 42]].dropna()
    indi_act.columns = ['Type', 'Hours']
    indi_act['Hours'] = indi_act['Hours'].replace({',': ''}, regex=True).astype(float)
    indi_act_summary = indi_act.groupby('Type').sum().rename(columns={'Hours': 'Hours_Individual'})

    act_comparison = pd.merge(cso_act_summary, indi_act_summary, how='outer', left_index=True, right_index=True).fillna(0)
    act_comparison['Difference'] = act_comparison['Hours_Individual'] - act_comparison['Hours_CSO']
    act_result = act_comparison.reset_index().sort_values(by='Type')

    st.markdown("### ⏱️ Activity Hours Comparison")
    st.dataframe(act_result)
else:
    st.info("Please upload both the CSO and Individual CSV files to begin.")

