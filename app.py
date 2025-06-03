import streamlit as st
import pandas as pd

st.set_page_config(page_title="Planting Data Comparison", layout="wide")
st.title("🌱 Planting Data Comparison Tool")

uploaded_cso = st.file_uploader("Upload CSO CSV File", type=["csv"])
uploaded_individual = st.file_uploader("Upload Individual CSV File", type=["csv"])

if uploaded_cso and uploaded_individual:
    cso_df = pd.read_csv(uploaded_cso)
    indi_df = pd.read_csv(uploaded_individual)

    # --- Clean column names ---
    cso_df.columns = cso_df.columns.str.strip()
    indi_df.columns = indi_df.columns.str.strip()

    # --- Define planting types ---
    planting_types = [
        'a) Viro', 'b) NT', 'c) 200cc', 'd) 600cc', 'e) Hiko',
        'f) 1L', 'g) 2L', 'h) 5L', 'i) 10L', 'j) 20L',
        'k) 25L', 'l) 35L', 'm) 45L', 'n) 100L', 'o) 150L',
        'p) 200L', 'q) 300L', 'r) 500L', 's) 400L'
    ]

    # --- Extract Planting Data ---
    cso_plants = cso_df[['Type', 'Quantity']].dropna()
    indi_plants = indi_df[['Type', 'Quantity']].dropna()

    cso_plants = cso_plants[cso_plants['Type'].isin(planting_types)].copy()
    indi_plants = indi_plants[indi_plants['Type'].isin(planting_types)].copy()

    for df in [cso_plants, indi_plants]:
        df['Quantity'] = df['Quantity'].astype(str).str.replace(",", "", regex=False).str.strip()
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)

    cso_summary = cso_plants.groupby('Type', as_index=False).sum()
    indi_summary = indi_plants.groupby('Type', as_index=False).sum()

    plant_comparison = pd.merge(
        cso_summary, indi_summary,
        on='Type', how='outer', suffixes=('_CSO', '_Individual')
    ).fillna(0)

    plant_comparison['Difference'] = (
        plant_comparison['Quantity_Individual'] - plant_comparison['Quantity_CSO']
    )

    total_row = pd.DataFrame([{
        'Type': 'TOTAL',
        'Quantity_CSO': plant_comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': plant_comparison['Quantity_Individual'].sum(),
        'Difference': plant_comparison['Difference'].sum()
    }])

    plant_result = pd.concat([plant_comparison, total_row], ignore_index=True)

    st.markdown("### 🌱 Plant Comparison")
    st.dataframe(plant_result)

    # --- Extract Non-Planting Data ---
    try:
        nonplant_types = [
            'a) Jute (manual/folds)', 'b) Jute (manual/no folds)', 'c) Jute (cobber/folds)',
            'd) Jute (cobber/no folds)', 'e) Tie (indiv.)', 'f) Stake (indiv.) less than 2m',
            'g) Stake (indiv.) more than 2m', 'h) Guard (1x HW/Corflute)', 'i) Guard (3x HW/Corflute)',
            'j) Guard (3x bamboo/plastic)', 'k) Guard (2x bamboo/plastic)',
            'l) Bamboo stake marker (indiv.)', 'm) Hardwood stake marker (indiv.)'
        ]

        cso_nonplants = cso_df.iloc[:, [19, 20]].dropna()
        indi_nonplants = indi_df.iloc[:, [36, 37]].dropna()

        cso_nonplants.columns = ['Item', 'Quantity']
        indi_nonplants.columns = ['Item', 'Quantity']

        cso_nonplants = cso_nonplants[cso_nonplants['Item'].isin(nonplant_types)]
        indi_nonplants = indi_nonplants[indi_nonplants['Item'].isin(nonplant_types)]

        for df in [cso_nonplants, indi_nonplants]:
            df['Quantity'] = df['Quantity'].astype(str).str.replace(",", "", regex=False).str.strip()
            df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)

        cso_np_summary = cso_nonplants.groupby('Item', as_index=False).sum()
        indi_np_summary = indi_nonplants.groupby('Item', as_index=False).sum()

        np_comparison = pd.merge(
            cso_np_summary, indi_np_summary,
            on='Item', how='outer', suffixes=('_CSO', '_Individual')
        ).fillna(0)

        np_comparison['Difference'] = (
            np_comparison['Quantity_Individual'] - np_comparison['Quantity_CSO']
        )

        total_np_row = pd.DataFrame([{
            'Item': 'TOTAL Non-Planting Items',
            'Quantity_CSO': np_comparison['Quantity_CSO'].sum(),
            'Quantity_Individual': np_comparison['Quantity_Individual'].sum(),
            'Difference': np_comparison['Difference'].sum()
        }])

        nonplant_result = pd.concat([np_comparison, total_np_row], ignore_index=True)

        st.markdown("### 🛠️ Non-Planting Items Comparison")
        st.dataframe(nonplant_result)

    except Exception as e:
        st.warning(f"⚠️ Could not process non-planting data: {e}")

    # --- Activity Comparison ---
    if cso_df.shape[1] > 42 and indi_df.shape[1] > 42:
        try:
            cso_activities = cso_df.iloc[:, [41, 42]].dropna()
            indi_activities = indi_df.iloc[:, [41, 42]].dropna()

            cso_activities.columns = ['Activity', 'Quantity']
            indi_activities.columns = ['Activity', 'Quantity']

            for df in [cso_activities, indi_activities]:
                df['Quantity'] = df['Quantity'].astype(str).str.replace(",", "", regex=False).str.strip()
                df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)

            cso_act_summary = cso_activities.groupby('Activity', as_index=False).sum()
            indi_act_summary = indi_activities.groupby('Activity', as_index=False).sum()

            act_comparison = pd.merge(
                cso_act_summary, indi_act_summary, on='Activity', how='outer',
                suffixes=('_CSO', '_Individual')
            ).fillna(0)

            act_comparison['Difference'] = (
                act_comparison['Quantity_Individual'] - act_comparison['Quantity_CSO']
            )

            act_total = pd.DataFrame([{
                'Activity': 'TOTAL Hours',
                'Quantity_CSO': act_comparison['Quantity_CSO'].sum(),
                'Quantity_Individual': act_comparison['Quantity_Individual'].sum(),
                'Difference': act_comparison['Difference'].sum()
            }])

            act_result = pd.concat([act_comparison, act_total], ignore_index=True)

            st.markdown("### ⏱️ Activity Hours Comparison")
            st.dataframe(act_result)

        except Exception as e:
            st.warning(f"⚠️ Could not process activity data: {e}")

    else:
        st.warning("⚠️ Not enough columns in one of the files to compare activity hours (needs at least 43 columns).")
