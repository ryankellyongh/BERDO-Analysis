import pandas as pd
import streamlit as st
from pathlib import Path

#Page setup
st.set_page_config(
    page_title="BERDO Priority Calculator",
    layout="wide"
)

#Load dataset
@st.cache_data
def load_data():
    file_path = Path.home() / "Documents" / "BERDO Analysis" / "2025-reported-energy-and-water-metrics.xlsx"

    df = pd.read_excel(file_path, header=0)

    df = df.rename(columns={
        "Largest Property Type": "property_type",
        "Reported Gross Floor Area (Sq Ft)": "gross_floor_area",
        "Site EUI (Energy Use Intensity kBtu/ft²)": "site_eui",
        "Estimated Total GHG Emissions (kgCO2e)": "ghg_emissions",
        "Reporting Compliance Status": "compliance_status",
        "First Emissions Compliance Year (Projected)": "compliance_year"
    })

    df["compliance_status"] = (
        df["compliance_status"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    return df

df_full = load_data()

#Priority function
def assign_priority(row, median_eui):
    score = 0
    reasons = []

    if row["compliance_status"] == "not submitted":
        score += 3
        reasons.append("Building is marked as not submitted")

    if pd.isna(row["property_type"]):
        score += 2
        reasons.append("Property type is missing")

    if pd.isna(row["site_eui"]):
        score += 2
        reasons.append("Site EUI is missing")
    elif row["site_eui"] >= median_eui:
        score += 2
        reasons.append("Site EUI is above the dataset median")

    if pd.notna(row["gross_floor_area"]) and row["gross_floor_area"] >= 100000:
        score += 1
        reasons.append("Building has a large reported floor area")

    if score >= 6:
        priority = "High"
    elif score >= 3:
        priority = "Moderate"
    else:
        priority = "Low"

    return priority, score, reasons

#Address lookup function
def lookup_building_priority(df, address):
    matches = df[
        df["Building Address"]
        .astype(str)
        .str.contains(address, case=False, na=False)
    ]

    if matches.empty:
        return None

    median_eui = df["site_eui"].median()
    results = []

    for _, row in matches.iterrows():
        priority, score, reasons = assign_priority(row, median_eui)

        results.append({
            "Building Address": row.get("Building Address"),
            "Property Owner Name": row.get("Property Owner Name"),
            "Property Type": row.get("property_type"),
            "Site EUI": row.get("site_eui"),
            "Compliance Status": row.get("compliance_status"),
            "Priority Level": priority,
            "Priority Score": score,
            "Reasons": "; ".join(reasons)
        })

    return pd.DataFrame(results)

#App layout
st.title("BERDO Building Priority Calculator")

st.write(
    "Enter a Boston building address to estimate its priority level for BERDO reporting support, outreach, or retrofit planning."
)

st.info(
    "This is a screening tool for analysis purposes. It is not an official City of Boston BERDO compliance determination."
)

address_input = st.text_input("Enter building address", placeholder="Example: 1047 Commonwealth")

if address_input:
    result = lookup_building_priority(df_full, address_input)

    if result is None:
        st.warning("No matching address found in the dataset.")
    else:
        st.subheader("Priority Result")
        st.dataframe(result, use_container_width=True)

        top_result = result.iloc[0]

        st.metric("Priority Level", top_result["Priority Level"])
        st.metric("Priority Score", int(top_result["Priority Score"]))

        st.write("### Explanation")
        st.write(top_result["Reasons"])