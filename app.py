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

    # Get column names based on Excel-style references
    ind_type_col = ind_df.columns[22]  # W
    ind_qty_col = ind_df.columns[23]  # X
    cso_type_col = cso_df.columns[11]  # L
    cso_qty_col = cso_df.columns[12]  # M

    ind_plants = parse_plant_types(ind_df, ind_type_col, ind_qty_col)
    cso_plants = parse_plant_types(cso_df, cso_type_col, cso_qty_col)
    plant_comparison = compare_series(ind_plants, cso_plants)
    total_diff_plants = plant_comparison["Difference"].sum()

    # Activity Hours Columns
    ind_act_col = ind_df.columns[41]  # AP
    ind_act_qty = ind_df.columns[42]  # AQ
    cso_act_col = cso_df.columns[23]  # X
    cso_act_qty = cso_df.columns[24]  # Y

    ind_hours = parse_activity_hours(ind_df, ind_act_col, ind_act_qty)
    cso_hours = parse_activity_hours(cso_df, cso_act_col, cso_act_qty)
    hour_comparison = compare_series(ind_hours, cso_hours)
    total_diff_hours = hour_comparison["Difference"].sum()

    st.subheader("🪴 Plant Type Comparison")
    st.dataframe(plant_comparison)
    st.markdown(f"**Total Plant Difference: {total_diff_plants}**")

    st.subheader("⏱️ Activity Hours Comparison")
    st.dataframe(hour_comparison)
    st.markdown(f"**Total Hour Difference: {total_diff_hours:.2f}**")

