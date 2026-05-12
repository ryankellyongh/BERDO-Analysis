import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="BERDO Building Priority Screening Tool",
    layout="wide"
)

# ---------------------------------------------------------------------------
# BERDO 2.0 emissions standards
# Source: BERDO 2.0 Draft Phase 1 Regulations (Boston APCC, 2021)
# Units: kg CO2e / sq ft / year
# Periods: 2025-29, 2030-34, 2035-39, 2040-44, 2045-49, 2050+
# ---------------------------------------------------------------------------
BERDO_STANDARDS = {
    "Assembly":                [7.8,  4.6,  3.3,  2.1, 1.1, 0.0],
    "College/University":      [10.2, 5.3,  3.8,  2.5, 1.2, 0.0],
    "Education":               [3.9,  2.4,  1.8,  1.2, 0.6, 0.0],
    "Food Sales & Service":    [17.4, 10.9, 8.0,  5.4, 2.7, 0.0],
    "Healthcare":              [15.4, 10.0, 7.4,  4.9, 2.4, 0.0],
    "Lodging":                 [5.8,  3.7,  2.7,  1.8, 0.9, 0.0],
    "Manufacturing/Industrial":[23.9, 15.3, 10.9, 6.7, 3.2, 0.0],
    "Multifamily Housing":     [4.1,  2.4,  1.8,  1.1, 0.6, 0.0],
    "Office":                  [5.3,  3.2,  2.4,  1.6, 0.8, 0.0],
    "Retail":                  [7.1,  3.4,  2.4,  1.5, 0.7, 0.0],
    "Services":                [7.5,  4.5,  3.3,  2.2, 1.1, 0.0],
    "Storage":                 [5.4,  2.8,  1.8,  1.0, 0.4, 0.0],
    "Technology/Science":      [19.2, 11.1, 7.8,  5.1, 2.5, 0.0],
}

COMPLIANCE_PERIODS = ["2025–29", "2030–34", "2035–39", "2040–44", "2045–49", "2050+"]

ACP_RATE = 234  # USD per metric ton CO2e over the limit

# ---------------------------------------------------------------------------
# Mapping from Energy Star Portfolio Manager property types → BERDO categories
# ---------------------------------------------------------------------------
PROPERTY_TYPE_MAP = {
    "office": "Office",
    "financial office": "Office",
    "courthouse": "Office",
    "government office": "Office",
    "multifamily housing": "Multifamily Housing",
    "residential": "Multifamily Housing",
    "senior living community": "Multifamily Housing",
    "affordable housing": "Multifamily Housing",
    "residence hall / dormitory": "Multifamily Housing",
    "residence hall/dormitory": "Multifamily Housing",
    "retail store": "Retail",
    "strip mall": "Retail",
    "enclosed mall": "Retail",
    "retail": "Retail",
    "supermarket/grocery store": "Food Sales & Service",
    "wholesale club/supercenter": "Retail",
    "hotel": "Lodging",
    "lodging/residential": "Lodging",
    "motel or inn": "Lodging",
    "hospital (general medical & surgical)": "Healthcare",
    "medical office": "Healthcare",
    "outpatient rehabilitation/physical therapy": "Healthcare",
    "urgent care/clinic/other outpatient": "Healthcare",
    "ambulatory surgical center": "Healthcare",
    "nursing home": "Healthcare",
    "health center/public health clinic": "Healthcare",
    "k-12 school": "Education",
    "pre-school/daycare": "Education",
    "adult education": "Education",
    "vocational school": "Education",
    "college/university": "College/University",
    "college / university": "College/University",
    "food service": "Food Sales & Service",
    "restaurant or bar": "Food Sales & Service",
    "fast food restaurant": "Food Sales & Service",
    "convenience store without gas station": "Food Sales & Service",
    "convenience store with gas station": "Food Sales & Service",
    "bar/nightclub": "Food Sales & Service",
    "worship facility": "Assembly",
    "museum": "Assembly",
    "performing arts": "Assembly",
    "sports arena": "Assembly",
    "fitness center/health club/gym": "Assembly",
    "recreation": "Assembly",
    "social/meeting hall": "Assembly",
    "entertainment/public assembly": "Assembly",
    "library": "Assembly",
    "movie theater": "Assembly",
    "convention center": "Assembly",
    "indoor arena": "Assembly",
    "personal services (health/beauty, dry cleaning, etc.)": "Services",
    "salon": "Services",
    "bank branch": "Services",
    "repair services": "Services",
    "laboratory": "Technology/Science",
    "data center": "Technology/Science",
    "research and development": "Technology/Science",
    "manufacturing/industrial plant": "Manufacturing/Industrial",
    "distribution center": "Manufacturing/Industrial",
    "non-refrigerated warehouse": "Storage",
    "refrigerated warehouse": "Storage",
    "self-storage facility": "Storage",
    "warehouse and storage": "Storage",
    "parking": "Services",
    "mixed use property": "Office",
}


def map_property_type(raw_type):
    if pd.isna(raw_type) or not isinstance(raw_type, str):
        return None
    key = raw_type.strip().lower()
    return PROPERTY_TYPE_MAP.get(key)


# ---------------------------------------------------------------------------
# Compliance gap calculation
# ---------------------------------------------------------------------------
def calculate_compliance_gap(ghg_intensity, sqft, berdo_category):
    limits = BERDO_STANDARDS.get(berdo_category)
    if limits is None:
        return []

    results = []
    for i, period in enumerate(COMPLIANCE_PERIODS):
        limit = limits[i]
        gap = round(ghg_intensity - limit, 3)
        compliant = gap <= 0
        excess_tons = 0.0 if compliant else round(gap * sqft / 1000, 1)
        fine = 0.0 if compliant else round(excess_tons * ACP_RATE, 0)
        results.append({
            "period": period,
            "limit": limit,
            "gap": gap,
            "compliant": compliant,
            "excess_metric_tons": excess_tons,
            "annual_fine_usd": fine,
        })
    return results


# ---------------------------------------------------------------------------
# Compliance gap display
# ---------------------------------------------------------------------------
def render_compliance_section(row):
    ghg_intensity = row.get("GHG Intensity (kgCO2e/sqft)")
    sqft = row.get("Gross Floor Area")
    raw_type = row.get("Property Type")
    berdo_category = map_property_type(raw_type)

    st.subheader("Compliance Gap Analysis")

    if pd.isna(ghg_intensity) or ghg_intensity == 0:
        st.warning(
            "GHG intensity is missing or zero for this building — "
            "cannot calculate compliance gap. Check that GHG emissions "
            "and floor area are reported in the dataset."
        )
        return

    if pd.isna(sqft) or sqft <= 0:
        st.warning("Floor area is missing — cannot calculate fine exposure.")
        return

    if berdo_category is None:
        st.warning(
            f"Property type **{raw_type}** could not be mapped to a BERDO "
            "emissions category. Add it to the PROPERTY_TYPE_MAP to enable "
            "gap calculations."
        )
        return

    gaps = calculate_compliance_gap(ghg_intensity, sqft, berdo_category)

    st.caption(
        f"Current intensity: **{ghg_intensity:.3f} kg CO₂e/sf/yr** · "
        f"Floor area: **{int(sqft):,} sq ft** · "
        f"BERDO category: **{berdo_category}**"
    )

    cols = st.columns(3)
    period_labels = ["2025–2029", "2030–2034", "2035–2039"]
    for i, col in enumerate(cols):
        g = gaps[i]
        with col:
            status = "✅ Compliant" if g["compliant"] else "⚠️ Non-compliant"
            fine_str = (
                "$0"
                if g["compliant"]
                else f"${g['annual_fine_usd']:,.0f}/yr"
            )
            gap_delta = (
                f"−{abs(g['gap']):.2f} kg under limit"
                if g["compliant"]
                else f"+{g['gap']:.2f} kg over limit"
            )
            st.metric(
                label=f"{period_labels[i]}  |  {status}",
                value=fine_str,
                delta=gap_delta,
                delta_color="normal" if g["compliant"] else "inverse",
            )
            if not g["compliant"]:
                st.caption(
                    f"Limit: {g['limit']} kg · "
                    f"{g['excess_metric_tons']:,.0f} excess metric tons"
                )

    st.markdown("---")
    limits = [g["limit"] for g in gaps]
    fines = [g["annual_fine_usd"] for g in gaps]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=COMPLIANCE_PERIODS,
        y=limits,
        name="BERDO limit",
        marker_color="#3266ad",
        text=[f"{v} kg" for v in limits],
        textposition="outside",
        textfont=dict(size=11),
    ))

    fig.add_trace(go.Scatter(
        x=COMPLIANCE_PERIODS,
        y=[ghg_intensity] * len(COMPLIANCE_PERIODS),
        name="Current intensity",
        mode="lines",
        line=dict(color="#E24B4A", width=2, dash="dash"),
    ))

    fig.add_trace(go.Scatter(
        x=COMPLIANCE_PERIODS,
        y=fines,
        name="Annual ACP fine (USD)",
        mode="lines+markers",
        yaxis="y2",
        line=dict(color="#BA7517", width=1.5, dash="dot"),
        marker=dict(size=6),
        visible="legendonly",
    ))

    y_max = max(max(limits), ghg_intensity) * 1.25

    fig.update_layout(
        xaxis_title="Compliance period",
        yaxis=dict(title="kg CO₂e / sf / yr", range=[0, y_max]),
        yaxis2=dict(
            title="Annual ACP fine (USD)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=380,
        margin=dict(t=40, b=40, l=60, r=60),
        bargap=0.35,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.12)")

    st.plotly_chart(fig, use_container_width=True, key=f"compliance_chart_{id(row)}")

    non_compliant_periods = [g for g in gaps if not g["compliant"]]
    if non_compliant_periods:
        total_5yr_fine = sum(g["annual_fine_usd"] * 5 for g in non_compliant_periods)
        st.info(
            f"If no emissions reductions are made, this building faces an estimated "
            f"**${total_5yr_fine:,.0f}** in cumulative ACP payments across "
            f"{len(non_compliant_periods)} non-compliant period(s) "
            f"(calculated as annual fine × 5 years per period)."
        )

    st.caption(
        "ACP = Alternative Compliance Payment at $234/metric ton CO₂e over limit. "
        "Source: BERDO 2.0 Draft Phase 1 Regulations (Boston APCC, 2021). "
        "Not an official City of Boston compliance determination."
    )

    with st.expander("About this tool"):
        st.markdown("""
**What is BERDO?**

The Building Emissions Reduction and Disclosure Ordinance (BERDO) requires large buildings
in Boston to reduce greenhouse gas emissions on a mandatory schedule toward net-zero by 2050.
Buildings over 35,000 sq ft or with 35+ residential units must meet emissions limits starting
in 2025. Smaller buildings between 20,000 and 35,000 sq ft begin compliance in 2030.

**How is the priority score calculated?**

Each building is scored on four factors:
- **Not submitted** (3 points): The building did not report data to the City of Boston by the May 15 deadline.
- **Missing property type** (2 points): The building's use category is not recorded, which prevents accurate emissions benchmarking.
- **Missing or above-median Site EUI** (2 points): The building's energy use intensity is missing or higher than the dataset median, indicating potential inefficiency.
- **Large floor area** (1 point): Buildings over 100,000 sq ft have greater emissions impact.

Scores of 6 or above are flagged as High priority. Scores of 3–5 are Moderate. Below 3 is Low.

**How is the compliance gap calculated?**

The tool compares each building's reported GHG intensity (kg CO₂e per square foot per year)
against the BERDO 2.0 emissions limits for its property type. If the building exceeds the limit,
the tool estimates the annual Alternative Compliance Payment (ACP) at $234 per excess metric
ton of CO₂e.

Source: BERDO 2.0 Draft Phase 1 Regulations (Boston APCC, 2021).
Not an official City of Boston compliance determination.
""")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    file_path = Path(__file__).parent.parent / "data" / "berdo.csv"
    if not file_path.exists():
        st.error(
            "Dataset not found. Make sure the CSV file is located at: "
            "data/berdo.csv"
        )
        st.stop()
    df = pd.read_csv(file_path)
    df.columns = df.columns.astype(str).str.strip()

    column_rename_map = {
        "Largest Property Type": "property_type",
        "Reported Gross Floor Area (Sq Ft)": "gross_floor_area",
        "Site EUI (Energy Use Intensity kBtu/ft²)": "site_eui",
        "Estimated Total GHG Emissions (kgCO2e)": "ghg_emissions",
        "Estimated Total GHG Emissions e(kgCO2e)": "ghg_emissions",
        "Reporting Compliance Status": "compliance_status",
        "First Emissions Compliance Year (Projected)": "compliance_year",
    }
    df = df.rename(columns=column_rename_map)

    required_columns = [
        "Building Address", "Property Owner Name", "property_type",
        "gross_floor_area", "site_eui", "ghg_emissions",
        "compliance_status", "compliance_year",
    ]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        st.error("Missing required columns in the dataset:")
        st.write(missing)
        st.write("Available columns:", list(df.columns))
        st.stop()

    df["gross_floor_area"] = pd.to_numeric(df["gross_floor_area"], errors="coerce")
    df["site_eui"]         = pd.to_numeric(df["site_eui"],         errors="coerce")
    df["ghg_emissions"]    = pd.to_numeric(df["ghg_emissions"],    errors="coerce")

    valid = (
        df["ghg_emissions"].notna() &
        df["gross_floor_area"].notna() &
        (df["gross_floor_area"] > 0)
    )
    df["ghg_intensity_kgco2e_sqft"] = pd.NA
    df.loc[valid, "ghg_intensity_kgco2e_sqft"] = (
        df.loc[valid, "ghg_emissions"] / df.loc[valid, "gross_floor_area"]
    )

    df["compliance_status"] = (
        df["compliance_status"].astype(str).str.lower().str.strip()
    )
    return df


# ---------------------------------------------------------------------------
# Priority scoring
# ---------------------------------------------------------------------------
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


def lookup_building_priority(df, address):
    import re
    address_clean = re.split(r',', address)[0].strip()
    matches = df[
        df["Building Address"].astype(str).str.contains(address_clean, case=False, na=False)
    ]
    if matches.empty:
        return None

    median_eui = df["site_eui"].median()
    results = []

    for _, row in matches.iterrows():
        priority, score, reasons = assign_priority(row, median_eui)
        results.append({
            "Building Address":            row.get("Building Address"),
            "Property Owner Name":         row.get("Property Owner Name"),
            "Property Type":               row.get("property_type"),
            "Gross Floor Area":            row.get("gross_floor_area"),
            "Site EUI":                    row.get("site_eui"),
            "GHG Intensity (kgCO2e/sqft)": row.get("ghg_intensity_kgco2e_sqft"),
            "Compliance Status":           row.get("compliance_status"),
            "Priority Level":              priority,
            "Priority Score":              score,
            "Reasons":                     "; ".join(reasons),
        })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------
df_full = load_data()

st.title("BERDO Building Priority Screening Tool")
st.write(
    "Enter a Boston building address to see its priority level for BERDO "
    "reporting support, outreach, or retrofit planning — and to estimate "
    "fine exposure under the 2025, 2030, and 2035 emissions standards."
)
st.info(
    "This is a screening tool for analysis purposes. "
    "It is not an official City of Boston BERDO compliance determination."
)

address_input = st.text_input(
    "Enter building address",
    placeholder="Example: 1047 Commonwealth Ave"
)

if address_input:
    result = lookup_building_priority(df_full, address_input)

    if result is None:
        st.warning("No matching address found in the dataset.")
    else:
        result["Site EUI"] = result["Site EUI"].round(1)
        result["GHG Intensity (kgCO2e/sqft)"] = (
            pd.to_numeric(result["GHG Intensity (kgCO2e/sqft)"], errors="coerce")
            .round(3)
        )

        st.subheader("Priority Result")

        display_cols = [
            "Building Address", "Property Owner Name", "Property Type",
            "Site EUI", "GHG Intensity (kgCO2e/sqft)",
            "Compliance Status", "Priority Level", "Priority Score", "Reasons",
        ]
        st.dataframe(result[display_cols], use_container_width=True)

        top = result.iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Priority Level", top["Priority Level"])
        with col2:
            st.metric("Priority Score", int(top["Priority Score"]))

        st.write("**Reasons:**", top["Reasons"])

        with st.expander("What do these fields mean?"):
            st.markdown("""
**Compliance Status**
- **Submitted**: The building owner reported energy and emissions data to the City of Boston for the previous calendar year.
- **Not submitted**: No data was reported. Buildings required to report under BERDO face fines of $300/day (buildings over 35,000 sq ft) for missing the May 15 annual deadline.

**Site EUI (Energy Use Intensity)**
- Measures how much energy a building uses per square foot per year (kBtu/sq ft/yr). A higher EUI means the building uses more energy relative to its size. Missing EUI typically means the building did not submit complete energy data.

**GHG Intensity (kg CO₂e/sq ft/yr)**
- The building's greenhouse gas emissions per square foot per year, calculated from reported fuel and electricity use. This is the value compared against BERDO emissions limits to determine compliance.

**Priority Score**
- A screening score (0–8) used to flag buildings that may need outreach, reporting support, or retrofit planning. Higher scores indicate more urgent attention.
""")

        st.markdown("---")

        render_compliance_section(top)
