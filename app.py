import streamlit as st
import pandas as pd

def clean_and_format(df):
    df.columns = df.columns.str.strip()
    return df

def parse_plant_types(df, type_col, qty_col):
    plant_data = df[[type_col, qty_col]].dropna()
    plant_data[qty_col] = pd.to_numeric(plant_data[qty_col], errors='coerce').fillna(0)
    return plant_data.groupby(type_col)[qty_col].sum().astype(int)

def parse_activity_hours(df, activity_col, qty_col):
    activity_data = df[[activity_col, qty_col]].dropna()
    activity_data[qty_col] = pd.to_numeric(activity_data[qty_col], errors='coerce').fillna(0)
    return activity_data.groupby(activity_col)[qty_col].sum()

def compare_series(individual, cso):
    all_keys = set(individual.index).union(cso.index)
    data = []
    for key in sorted(all_keys):
        ind_val = individual.get(key, 0)
        cso_val = cso.get(key, 0)
        diff = ind_val - cso_val
        data.append((key, ind_val, cso_val, diff))
    return pd.DataFrame(data, columns=["Type", "Individual", "CSO", "Difference"])

st.title("🌱 CSO vs Individual Planting Comparison Tool")

individual_file = st.file_uploader("Upload Individual CSV", type=["csv"])
cso_file = st.file_uploader("Upload CSO CSV", type=["csv"])

if individual_file and cso_file:
    ind_df = clean_and_format(pd.read_csv(individual_file))
    cso_df = clean_and_format(pd.read_csv(cso_file))

    # Plant Types
    ind_plants = parse_plant_types(ind_df, "W", "X")
    cso_plants = parse_plant_types(cso_df, "L", "M")
    plant_comparison = compare_series(ind_plants, cso_plants)
    total_diff_plants = plant_comparison["Difference"].sum()

    # Activity Hours
    ind_hours = parse_activity_hours(ind_df, "AP", "AQ")
    cso_hours = parse_activity_hours(cso_df, "X", "Y")
    hour_comparison = compare_series(ind_hours, cso_hours)
    total_diff_hours = hour_comparison["Difference"].sum()

    st.subheader("🪴 Plant Type Comparison")
    st.dataframe(plant_comparison)
    st.markdown(f"**Total Plant Difference: {total_diff_plants}**")

    st.subheader("⏱️ Activity Hours Comparison")
    st.dataframe(hour_comparison)
    st.markdown(f"**Total Hour Difference: {total_diff_hours:.2f}**")

