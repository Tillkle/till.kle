import streamlit as st
import pandas as pd

st.title("CSO vs Individual Comparison App")

st.markdown("Upload the CSO and Individual CSV files to compare:")

cso_file = st.file_uploader("Upload CSO CSV", type=["csv"])
indi_file = st.file_uploader("Upload Individual CSV", type=["csv"])

if cso_file and indi_file:
    cso_df = pd.read_csv(cso_file)
    indi_df = pd.read_csv(indi_file)

    # Clean column names
    cso_df.columns = cso_df.columns.str.strip()
    indi_df.columns = indi_df.columns.str.strip()

    # Extract relevant columns
    cso_plants = cso_df.iloc[:, [11, 12]].dropna()  # Columns L and M
    indi_plants = indi_df.iloc[:, [22, 23]].dropna()  # Columns W and X
    cso_plants.columns = ['Type', 'Quantity']
    indi_plants.columns = ['Type', 'Quantity']

    # Convert quantities to numeric
    cso_plants['Quantity'] = pd.to_numeric(cso_plants['Quantity'], errors='coerce').fillna(0)
    indi_plants['Quantity'] = pd.to_numeric(indi_plants['Quantity'], errors='coerce').fillna(0)

    # Group and summarize
    cso_summary = cso_plants.groupby('Type', as_index=False).sum()
    indi_summary = indi_plants.groupby('Type', as_index=False).sum()

    # Merge for comparison
    comparison = pd.merge(cso_summary, indi_summary, on='Type', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
    comparison['Difference'] = comparison['Quantity_Individual'] - comparison['Quantity_CSO']

    # Total row
    total_row = pd.DataFrame([{
        'Type': 'TOTAL Plants',
        'Quantity_CSO': comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': comparison['Quantity_Individual'].sum(),
        'Difference': comparison['Difference'].sum()
    }])

    final_comparison = pd.concat([comparison, total_row], ignore_index=True)

    st.markdown("### Plant Type Comparison")
    st.dataframe(final_comparison)

    # Extract activity data (Columns X and Y from CSO, Columns AP and AQ from Individual)
    cso_activity = cso_df.iloc[:, [23, 24]].dropna()
    indi_activity = indi_df.iloc[:, [41, 42]].dropna()
    cso_activity.columns = ['Activity', 'Quantity']
    indi_activity.columns = ['Activity', 'Quantity']

    # Convert quantities to numeric
    cso_activity['Quantity'] = pd.to_numeric(cso_activity['Quantity'], errors='coerce').fillna(0)
    indi_activity['Quantity'] = pd.to_numeric(indi_activity['Quantity'], errors='coerce').fillna(0)

    # Group and summarize
    act_cso_summary = cso_activity.groupby('Activity', as_index=False).sum()
    act_indi_summary = indi_activity.groupby('Activity', as_index=False).sum()

    # Merge for comparison
    act_comparison = pd.merge(act_cso_summary, act_indi_summary, on='Activity', how='outer', suffixes=('_CSO', '_Individual')).fillna(0)
    act_comparison['Difference'] = act_comparison['Quantity_Individual'] - act_comparison['Quantity_CSO']

    # Total row
    act_total_row = pd.DataFrame([{
        'Activity': 'TOTAL Hours',
        'Quantity_CSO': act_comparison['Quantity_CSO'].sum(),
        'Quantity_Individual': act_comparison['Quantity_Individual'].sum(),
        'Difference': act_comparison['Difference'].sum()
    }])

    final_act_comparison = pd.concat([act_comparison, act_total_row], ignore_index=True)

    st.markdown("### Activity Hours Comparison")
    st.dataframe(final_act_comparison)


