import streamlit as st
import pandas as pd

st.title("🌱 Planting Data Comparison Tool")

# Upload files
cso_file = st.file_uploader("Upload CSO File", type="csv")
indi_file = st.file_uploader("Upload Individual File", type="csv")

if cso_file and indi_file:
    cso_df = pd.read_csv(cso_file)
    indi_df = pd.read_csv(indi_file)

    # --- Clean up comma-strings and convert columns to numeric where needed
    for col in ['Quantity']:
        for df in [cso_df, indi_df]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').astype(float)

    # --------------------------
    # 1. Planting Comparison
    # --------------------------
    planting_cols = ['Strata', 'Type', 'Quantity']
    if all(col in cso_df.columns for col in planting_cols) and all(col in indi_df.columns for col in planting_cols):
        cso_plants = cso_df[planting_cols].groupby(['Strata', 'Type']).sum().reset_index()
        indi_plants = indi_df[planting_cols].groupby(['Strata', 'Type']).sum().reset_index()

        merged_plants = pd.merge(cso_plants, indi_plants, on=['Strata', 'Type'], how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
        merged_plants['Difference'] = merged_plants['Quantity_CSO'] - merged_plants['Quantity_Individual']

        st.subheader("🌿 Planting Comparison")
        st.dataframe(merged_plants)

    else:
        st.warning("Missing required columns for planting data.")

    # --------------------------
    # 2. Non-Planting Items Comparison
    # --------------------------
    np_items = [
        "a) Jute (manual/folds)",
        "b) Jute (manual/no folds)",
        "c) Jute (cobber/folds)",
        "d) Jute (cobber/no folds)",
        "e) Tie (indiv.)",
        "f) Stake (indiv.) less than 2m",
        "g) Stake (indiv.) more than 2m",
        "h) Guard (1x HW/Corflute)",
        "i) Guard (3x HW/Corflute)",
        "j) Guard (3x bamboo/plastic)",
        "k) Guard (2x bamboo/plastic)",
        "l) Bamboo stake marker (indiv.)",
        "m) Hardwood stake marker (indiv.)"
    ]

    # CSO: Column AK (36), AL (37)
    # IND: Column T (19), U (20)
    try:
        cso_np = cso_df.iloc[:, [36, 37]].dropna()
        indi_np = indi_df.iloc[:, [19, 20]].dropna()

        cso_np.columns = ['Item', 'Quantity']
        indi_np.columns = ['Item', 'Quantity']

        # Clean commas and convert to numeric
        cso_np['Quantity'] = cso_np['Quantity'].astype(str).str.replace(',', '').astype(float)
        indi_np['Quantity'] = indi_np['Quantity'].astype(str).str.replace(',', '').astype(float)

        # Filter for relevant items
        cso_np = cso_np[cso_np['Item'].isin(np_items)]
        indi_np = indi_np[indi_np['Item'].isin(np_items)]

        cso_grouped = cso_np.groupby('Item').sum().reset_index()
        indi_grouped = indi_np.groupby('Item').sum().reset_index()

        np_comparison = pd.merge(cso_grouped, indi_grouped, on='Item', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
        np_comparison['Difference'] = np_comparison['Quantity_CSO'] - np_comparison['Quantity_Individual']

        st.subheader("🔧 Non-Planting Items Comparison")
        st.dataframe(np_comparison)

    except Exception as e:
        st.error(f"Non-planting item comparison failed: {e}")

    # --------------------------
    # 3. Activity Hours Comparison
    # --------------------------
    try:
        # CSO: Column AP (41), AQ (42)
        # IND: Column AP (41), AQ (42)
        cso_activities = cso_df.iloc[:, [41, 42]].dropna()
        indi_activities = indi_df.iloc[:, [41, 42]].dropna()

        cso_activities.columns = ['Activity', 'Hours']
        indi_activities.columns = ['Activity', 'Hours']

        cso_activities['Hours'] = cso_activities['Hours'].astype(str).str.replace(',', '').astype(float)
        indi_activities['Hours'] = indi_activities['Hours'].astype(str).str.replace(',', '').astype(float)

        cso_agg = cso_activities.groupby('Activity').sum().reset_index()
        indi_agg = indi_activities.groupby('Activity').sum().reset_index()

        activity_comparison = pd.merge(cso_agg, indi_agg, on='Activity', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
        activity_comparison['Difference'] = activity_comparison['Hours_CSO'] - activity_comparison['Hours_Individual']

        st.subheader("⏱️ Activity Hours Comparison")
        st.dataframe(activity_comparison)

    except Exception as e:
        st.error(f"Activity hours comparison failed: {e}")

