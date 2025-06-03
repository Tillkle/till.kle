import streamlit as st
import pandas as pd

st.title("CSO vs Individual Comparison")

st.markdown("Upload the **CSO** and **Individual** CSV files below:")

cso_file = st.file_uploader("Upload CSO CSV", type="csv")
indi_file = st.file_uploader("Upload Individual CSV", type="csv")

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
    indi_plants['Quantity'] = (
        indi_plants['Quantity']
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .astype(float)
    )

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

    # --- Normalize helper ---
    def normalize_name(name):
        return str(name).split(") ")[-1].strip().lower()

    # --- Activity Comparison ---
    cso_activities = cso_df.iloc[:, [23, 24]].dropna()
    indi_activities = indi_df.iloc[:, [41, 42]].dropna()

    cso_activities.columns = ['Activity', 'Quantity']
    indi_activities.columns = ['Activity', 'Quantity']

    cso_activities['Quantity'] = pd.to_numeric(cso_activities['Quantity'], errors='coerce').fillna(0)
    indi_activities['Quantity'] = pd.to_numeric(indi_activities['Quantity'], errors='coerce').fillna(0)

    cso_activities['MatchKey'] = cso_activities['Activity'].apply(normalize_name)
    indi_activities['MatchKey'] = indi_activities['Activity'].apply(normalize_name)

    cso_act_summary = cso_activities.groupby('MatchKey', as_index=False)['Quantity'].sum().rename(columns={'Quantity': 'Quantity_CSO'})
    indi_act_summary = indi_activities.groupby('MatchKey', as_index=False)['Quantity'].sum().rename(columns={'Quantity': 'Quantity_Individual'})

    act_comparison = pd.merge(cso_act_summary, indi_act_summary, on='MatchKey', how='outer').fillna(0)
    act_comparison['Difference'] = act_comparison['Quantity_Individual'] - act_comparison['Quantity_CSO']
    act_comparison['Activity'] = act_comparison['MatchKey'].str.title()

    act_total = pd.DataFrame([{
        'Activity': 'TOTAL Hours',
        'Quantity_CSO': act_comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': act_comparison['Quantity_Individual'].sum(),
        'Difference': act_comparison['Difference'].sum(),
        'MatchKey': ''
    }])
    act_result = pd.concat([act_comparison, act_total], ignore_index=True)[['Activity', 'Quantity_CSO', 'Quantity_Individual', 'Difference']]

    st.markdown("### ⏱️ Activity Hours Comparison")
    st.dataframe(act_result)

    # --- Non-Planting Items Comparison ---
    # Individual: Column AK (index 36) = Type, AL (index 37) = Quantity
    # CSO: Column T (index 19) = Type, U (index 20) = Quantity

    indi_nonplant = indi_df.iloc[:, [36, 37]].dropna()
    cso_nonplant = cso_df.iloc[:, [19, 20]].dropna()

    indi_nonplant.columns = ['Item', 'Quantity']
    cso_nonplant.columns = ['Item', 'Quantity']

    indi_nonplant['Quantity'] = pd.to_numeric(indi_nonplant['Quantity'], errors='coerce').fillna(0)
    cso_nonplant['Quantity'] = pd.to_numeric(cso_nonplant['Quantity'], errors='coerce').fillna(0)

    indi_nonplant['MatchKey'] = indi_nonplant['Item'].apply(normalize_name)
    cso_nonplant['MatchKey'] = cso_nonplant['Item'].apply(normalize_name)

    indi_np_summary = indi_nonplant.groupby('MatchKey', as_index=False)['Quantity'].sum().rename(columns={'Quantity': 'Quantity_Individual'})
    cso_np_summary = cso_nonplant.groupby('MatchKey', as_index=False)['Quantity'].sum().rename(columns={'Quantity': 'Quantity_CSO'})

    np_comparison = pd.merge(cso_np_summary, indi_np_summary, on='MatchKey', how='outer').fillna(0)
    np_comparison['Difference'] = np_comparison['Quantity_Individual'] - np_comparison['Quantity_CSO']
    np_comparison['Item'] = np_comparison['MatchKey'].str.title()

    total_np_row = pd.DataFrame([{
        'Item': 'TOTAL Non-Planting Items',
        'Quantity_CSO': np_comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': np_comparison['Quantity_Individual'].sum(),
        'Difference': np_comparison['Difference'].sum(),
        'MatchKey': ''
    }])
    nonplant_result = pd.concat([np_comparison, total_np_row], ignore_index=True)[['Item', 'Quantity_CSO', 'Quantity_Individual', 'Difference']]

    st.markdown("### 🛠️ Non-Planting Items Comparison")
    st.dataframe(nonplant_result)
