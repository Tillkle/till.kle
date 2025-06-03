import streamlit as st
import pandas as pd
import re

st.title("CSO vs Individual Comparison")

st.markdown("Upload the **CSO** and **Individual** CSV files below:")

cso_file = st.file_uploader("Upload CSO CSV", type="csv")
indi_file = st.file_uploader("Upload Individual CSV", type="csv")

def normalize_name(name):
    if pd.isna(name):
        return ''
    name = str(name).lower()
    name = re.sub(r"^[a-z]\)\s*", "", name)       # remove prefixes like "a) "
    name = re.sub(r"\(.*?\)", "", name)           # remove anything in parentheses
    name = re.sub(r"[^a-z0-9<>\s]", "", name)     # remove special characters
    name = name.replace("individual", "")         # remove word "individual"
    name = name.strip()
    name = re.sub(r"\s+", " ", name)              # collapse multiple spaces
    return name

if cso_file and indi_file:
    # Load files
    cso_df = pd.read_csv(cso_file)
    indi_df = pd.read_csv(indi_file)

    # --- Plant Comparison ---
    cso_plants = cso_df.iloc[:, [11, 12]].dropna()
    indi_plants = indi_df.iloc[:, [22, 23]].dropna()

    cso_plants.columns = ['Type', 'Quantity']
    indi_plants.columns = ['Type', 'Quantity']

    cso_plants['Quantity'] = cso_plants['Quantity'].astype(str).str.replace(",", "", regex=False).str.strip().astype(float)
    indi_plants['Quantity'] = indi_plants['Quantity'].astype(str).str.replace(",", "", regex=False).str.strip().astype(float)

    cso_plants['NormType'] = cso_plants['Type'].apply(normalize_name)
    indi_plants['NormType'] = indi_plants['Type'].apply(normalize_name)

    cso_summary = cso_plants.groupby('NormType', as_index=False).agg({'Quantity': 'sum'})
    indi_summary = indi_plants.groupby('NormType', as_index=False).agg({'Quantity': 'sum'})

    plant_comparison = pd.merge(cso_summary, indi_summary, on='NormType', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
    plant_comparison['Difference'] = plant_comparison['Quantity_Individual'] - plant_comparison['Quantity_CSO']
    plant_comparison = plant_comparison.rename(columns={'NormType': 'Type'})

    total_row = pd.DataFrame([{
        'Type': 'TOTAL Plants',
        'Quantity_CSO': plant_comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': plant_comparison['Quantity_Individual'].sum(),
        'Difference': plant_comparison['Difference'].sum()
    }])
    plant_result = pd.concat([plant_comparison, total_row], ignore_index=True)

    st.markdown("### 🌱 Plant Comparison")
    st.dataframe(plant_result)

    # --- Activity Comparison ---
    cso_activities = cso_df.iloc[:, [23, 24]].dropna()
    indi_activities = indi_df.iloc[:, [41, 42]].dropna()

    cso_activities.columns = ['Activity', 'Quantity']
    indi_activities.columns = ['Activity', 'Quantity']

    cso_activities['Quantity'] = pd.to_numeric(cso_activities['Quantity'], errors='coerce').fillna(0)
    indi_activities['Quantity'] = pd.to_numeric(indi_activities['Quantity'], errors='coerce').fillna(0)

    cso_activities['NormActivity'] = cso_activities['Activity'].apply(normalize_name)
    indi_activities['NormActivity'] = indi_activities['Activity'].apply(normalize_name)

    cso_act_summary = cso_activities.groupby('NormActivity', as_index=False).agg({'Quantity': 'sum'})
    indi_act_summary = indi_activities.groupby('NormActivity', as_index=False).agg({'Quantity': 'sum'})

    act_comparison = pd.merge(cso_act_summary, indi_act_summary, on='NormActivity', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
    act_comparison['Difference'] = act_comparison['Quantity_Individual'] - act_comparison['Quantity_CSO']
    act_comparison = act_comparison.rename(columns={'NormActivity': 'Activity'})

    act_total = pd.DataFrame([{
        'Activity': 'TOTAL Hours',
        'Quantity_CSO': act_comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': act_comparison['Quantity_Individual'].sum(),
        'Difference': act_comparison['Difference'].sum()
    }])
    act_result = pd.concat([act_comparison, act_total], ignore_index=True)

    st.markdown("### ⏱️ Activity Hours Comparison")
    st.dataframe(act_result)

    # --- Non-Planting Items Comparison ---
    cso_nonplant = cso_df.iloc[:, [36, 37]].dropna()
    indi_nonplant = indi_df.iloc[:, [19, 20]].dropna()

    cso_nonplant.columns = ['Item', 'Quantity']
    indi_nonplant.columns = ['Item', 'Quantity']

    cso_nonplant['Quantity'] = pd.to_numeric(cso_nonplant['Quantity'], errors='coerce').fillna(0)
    indi_nonplant['Quantity'] = pd.to_numeric(indi_nonplant['Quantity'], errors='coerce').fillna(0)

    cso_nonplant['NormItem'] = cso_nonplant['Item'].apply(normalize_name)
    indi_nonplant['NormItem'] = indi_nonplant['Item'].apply(normalize_name)

    cso_np_summary = cso_nonplant.groupby('NormItem', as_index=False).agg({'Quantity': 'sum'})
    indi_np_summary = indi_nonplant.groupby('NormItem', as_index=False).agg({'Quantity': 'sum'})

    np_comparison = pd.merge(cso_np_summary, indi_np_summary, on='NormItem', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
    np_comparison['Difference'] = np_comparison['Quantity_Individual'] - np_comparison['Quantity_CSO']
    np_comparison = np_comparison.rename(columns={'NormItem': 'Item'})

    total_np_row = pd.DataFrame([{
        'Item': 'TOTAL Non-Planting Items',
        'Quantity_CSO': np_comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': np_comparison['Quantity_Individual'].sum(),
        'Difference': np_comparison['Difference'].sum()
    }])
    nonplant_result = pd.concat([np_comparison, total_np_row], ignore_index=True)

    st.markdown("### 🛠️ Non-Planting Items Comparison")
    st.dataframe(nonplant_result)

