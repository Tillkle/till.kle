import streamlit as st
import pandas as pd

st.title("🌱 Planting & Non-Planting Comparison Tool")

# Upload files
cso_file = st.file_uploader("Upload CSO File", type="csv")
indi_file = st.file_uploader("Upload Individual File", type="csv")

if cso_file and indi_file:
    cso_df = pd.read_csv(cso_file)
    indi_df = pd.read_csv(indi_file)

    # --- PLANTING COMPARISON ---
    try:
        planting_cols = ['Strata', 'Type', 'Quantity']

        cso_plants = cso_df[planting_cols].groupby(['Strata', 'Type']).sum().reset_index()
        indi_plants = indi_df[planting_cols].groupby(['Strata', 'Type']).sum().reset_index()

        plant_result = pd.merge(cso_plants, indi_plants, on=['Strata', 'Type'], how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
        plant_result['Difference'] = plant_result['Quantity_CSO'] - plant_result['Quantity_Individual']

        st.markdown("### 🌿 Planting Comparison")
        st.dataframe(plant_result)
    except Exception as e:
        st.error(f"Planting comparison failed: {e}")

    # --- NON-PLANTING ITEMS COMPARISON ---
    try:
        non_planting_types = [
            "a) Jute (manual/folds)", "b) Jute (manual/no folds)",
            "c) Jute (cobber/folds)", "d) Jute (cobber/no folds)",
            "e) Tie (indiv.)", "f) Stake (indiv.) less than 2m",
            "g) Stake (indiv.) more than 2m", "h) Guard (1x HW/Corflute)",
            "i) Guard (3x HW/Corflute)", "j) Guard (3x bamboo/plastic)",
            "k) Guard (2x bamboo/plastic)", "l) Bamboo stake marker (indiv.)",
            "m) Hardwood stake marker (indiv.)"
        ]

        # CSO: Type in Column AK (36), Quantity in Column AL (37)
        cso_np = cso_df.iloc[:, [36, 37]].dropna()
        cso_np.columns = ['Type', 'Quantity']
        cso_np = cso_np[cso_np['Type'].isin(non_planting_types)]
        cso_np['Quantity'] = pd.to_numeric(cso_np['Quantity'].astype(str).str.replace(',', ''), errors='coerce')

        # IND: Type in Column T (19), Quantity in Column U (20)
        indi_np = indi_df.iloc[:, [19, 20]].dropna()
        indi_np.columns = ['Type', 'Quantity']
        indi_np = indi_np[indi_np['Type'].isin(non_planting_types)]
        indi_np['Quantity'] = pd.to_numeric(indi_np['Quantity'].astype(str).str.replace(',', ''), errors='coerce')

        cso_np_group = cso_np.groupby('Type').sum().reset_index()
        indi_np_group = indi_np.groupby('Type').sum().reset_index()

        np_result = pd.merge(cso_np_group, indi_np_group, on='Type', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
        np_result['Difference'] = np_result['Quantity_CSO'] - np_result['Quantity_Individual']

        st.markdown("### 🧰 Non-Planting Items Comparison")
        st.dataframe(np_result)

    except Exception as e:
        st.error(f"Non-planting comparison failed: {e}")

    except Exception as e:
        st.error(f"Activity hours comparison failed: {e}")

