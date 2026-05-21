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

COMPLIANCE_PERIODS = ["2025-29", "2030-34", "2035-39", "2040-44", "2045-49", "2050+"]

ACP_RATE = 234  # USD per metric ton CO2e over the limit

# ---------------------------------------------------------------------------
# Fuel type groupings for breakdown chart
# ---------------------------------------------------------------------------
FUEL_EMISSION_COLS = {
    "Electricity": [
        "Electricity Emissions (kgCO2e)",
    ],
    "Steam / District": [
        "District Steam Emissions (kgCO2e)",
        "District Hot Water Emissions (kgCO2e)",
        "District Chilled Water Emissions (kgCO2e)",
    ],
    "Natural Gas": [
        "Natural Gas Emissions (kgCO2e)",
    ],
    "Fossil Fuels": [
        "Fuel Oil 1 Emissions (kgCO2e)",
        "Fuel Oil 2 Emissions (kgCO2e)",
        "Fuel Oil 4 Emissions (kgCO2e)",
        "Fuel Oil 5 and 6 Emissions (kgCO2e)",
        "Propane Emissions (kgCO2e)",
        "Diesel Emissions (kgCO2e)",
        "Kerosene Emissions (kgCO2e)",
    ],
}

FUEL_COLORS = {
    "Electricity":      "#3266ad",
    "Steam / District": "#7F77DD",
    "Natural Gas":      "#BA7517",
    "Fossil Fuels":     "#D85A30",
}

# Electricity emissions reduction factors per compliance period
# relative to 2025 baseline -- derived from BERDO Projected Grid Emissions
# Factors (Boston APCC Policies & Procedures, Appendix B, 2025).
# Formula: kgCO2e = kWh x (1 - RPS_Class_I) x grid_factor
# 100,000 kWh example: 2025=18,177 / 2030=12,780 / 2035=9,790 /
#                       2040=7,100  / 2045=4,815  / 2050=2,840
ELECTRICITY_REDUCTION_FACTORS = [1.000, 0.703, 0.539, 0.391, 0.265, 0.156]

# ---------------------------------------------------------------------------
# Mapping from Energy Star Portfolio Manager property types to BERDO categories
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
# Fuel breakdown chart
# ---------------------------------------------------------------------------
def render_fuel_breakdown_chart(row, sqft):
    group_emissions = {}
    for group, cols in FUEL_EMISSION_COLS.items():
        total = sum(
            pd.to_numeric(row.get(col, 0), errors="coerce") or 0
            for col in cols
        )
        group_emissions[group] = total

    total_emissions = sum(group_emissions.values())
    if total_emissions == 0 or sqft <= 0:
        st.caption(
            "Fuel type breakdown not available -- "
            "individual emissions columns missing or zero."
        )
        return

    group_intensity = {k: v / sqft for k, v in group_emissions.items()}

    st.subheader("Energy Type Breakdown")

    fig1 = go.Figure()
    for group, intensity in group_intensity.items():
        if intensity > 0:
            pct = intensity / sum(group_intensity.values()) * 100
            fig1.add_trace(go.Bar(
                name=group,
                x=[round(intensity, 4)],
                y=["Current emissions"],
                orientation="h",
                marker_color=FUEL_COLORS[group],
                text=f"{pct:.0f}%",
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate=(
                    f"<b>{group}</b><br>"
                    f"{intensity:.3f} kg CO2e/sf<br>"
                    f"{pct:.1f}% of total<extra></extra>"
                ),
            ))

    fig1.update_layout(
        barmode="stack",
        height=110,
        margin=dict(t=8, b=32, l=10, r=10),
        xaxis_title="kg CO2e / sf / yr",
        yaxis=dict(showticklabels=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="left", x=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig1.update_xaxes(showgrid=False)
    st.plotly_chart(fig1, use_container_width=True, key=f"fuel_mix_{id(row)}")

    elec_base = group_intensity.get("Electricity", 0)
    non_elec  = {k: v for k, v in group_intensity.items() if k != "Electricity"}

    fig2 = go.Figure()

    for group, intensity in non_elec.items():
        if intensity > 0:
            fig2.add_trace(go.Bar(
                name=group,
                x=COMPLIANCE_PERIODS,
                y=[round(intensity, 4)] * len(COMPLIANCE_PERIODS),
                marker_color=FUEL_COLORS[group],
            ))

    elec_projected = [round(elec_base * f, 4) for f in ELECTRICITY_REDUCTION_FACTORS]
    fig2.add_trace(go.Bar(
        name="Electricity (grid decarbonisation applied)",
        x=COMPLIANCE_PERIODS,
        y=elec_projected,
        marker_color=FUEL_COLORS["Electricity"],
    ))

    raw_type = row.get("Property Type") or row.get("property_type")
    berdo_category = map_property_type(raw_type)
    if berdo_category and berdo_category in BERDO_STANDARDS:
        fig2.add_trace(go.Scatter(
            x=COMPLIANCE_PERIODS,
            y=BERDO_STANDARDS[berdo_category],
            name="BERDO limit",
            mode="lines+markers",
            line=dict(color="#E24B4A", width=2, dash="dash"),
            marker=dict(size=6),
        ))

    fig2.update_layout(
        barmode="stack",
        xaxis_title="Compliance period",
        yaxis_title="kg CO2e / sf / yr",
        height=340,
        margin=dict(t=40, b=40, l=60, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        bargap=0.35,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig2.update_xaxes(showgrid=False)
    fig2.update_yaxes(gridcolor="rgba(128,128,128,0.12)")
    st.plotly_chart(fig2, use_container_width=True, key=f"fuel_projected_{id(row)}")

    elec_pct = (elec_base / sum(group_intensity.values()) * 100) if total_emissions > 0 else 0
    non_elec_total = sum(non_elec.values())
    st.caption(
        f"{elec_pct:.0f}% of emissions come from electricity and will decline "
        f"automatically as the ISO-NE grid decarbonises (RPS Class I: 27% to 60% by 2050). "
        f"The remaining {100 - elec_pct:.0f}% "
        f"({non_elec_total:.3f} kg CO2e/sf/yr) requires active fuel switching or "
        f"efficiency improvements. "
        f"Source: BERDO Projected Grid Emissions Factors, "
        f"Boston APCC Policies & Procedures, Appendix B (2025)."
    )


# ---------------------------------------------------------------------------
# Compliance gap display
# ---------------------------------------------------------------------------
def render_compliance_section(row, prior_year_ghg_intensity=None, prior_year_label=None):
    ghg_intensity  = row.get("GHG Intensity (kgCO2e/sqft)")
    sqft           = row.get("Gross Floor Area")
    raw_type       = row.get("Property Type")
    berdo_category = map_property_type(raw_type)

    st.subheader("Compliance Gap Analysis")

    if pd.isna(ghg_intensity) or ghg_intensity == 0:
        st.warning(
            "GHG intensity is missing or zero for this building -- "
            "cannot calculate compliance gap."
        )
        return

    if pd.isna(sqft) or sqft <= 0:
        st.warning("Floor area is missing -- cannot calculate fine exposure.")
        return

    if berdo_category is None:
        st.warning(
            f"Property type {raw_type} could not be mapped to a BERDO "
            "emissions category."
        )
        return

    gaps = calculate_compliance_gap(ghg_intensity, sqft, berdo_category)

    st.caption(
        f"Current intensity: {ghg_intensity:.3f} kg CO2e/sf/yr  "
        f"Floor area: {int(sqft):,} sq ft  "
        f"BERDO category: {berdo_category}"
    )

    st.markdown("---")
    render_fuel_breakdown_chart(row, sqft)
    st.markdown("---")

    cols = st.columns(3)
    period_labels = ["2025-2029", "2030-2034", "2035-2039"]
    for i, col in enumerate(cols):
        g = gaps[i]
        with col:
            status   = "Compliant" if g["compliant"] else "Non-compliant"
            fine_str = "$0" if g["compliant"] else f"${g['annual_fine_usd']:,.0f}/yr"
            gap_delta = (
                f"-{abs(g['gap']):.2f} kg under limit"
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
                    f"Limit: {g['limit']} kg  "
                    f"{g['excess_metric_tons']:,.0f} excess metric tons"
                )

    st.markdown("---")

    limits = [g["limit"] for g in gaps]
    fines  = [g["annual_fine_usd"] for g in gaps]

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

    if prior_year_ghg_intensity is not None and not pd.isna(prior_year_ghg_intensity):
        fig.add_trace(go.Scatter(
            x=COMPLIANCE_PERIODS,
            y=[prior_year_ghg_intensity] * len(COMPLIANCE_PERIODS),
            name=f"{prior_year_label} intensity",
            mode="lines",
            line=dict(color="#9B59B6", width=1.5, dash="dot"),
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
        yaxis=dict(title="kg CO2e / sf / yr", range=[0, y_max]),
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
            f"${total_5yr_fine:,.0f} in cumulative ACP payments across "
            f"{len(non_compliant_periods)} non-compliant period(s) "
            f"(calculated as annual fine x 5 years per period)."
        )

    st.caption(
        "ACP = Alternative Compliance Payment at $234/metric ton CO2e over limit. "
        "Compliance gap calculated using current reported GHG intensity held constant -- "
        "does not project future grid decarbonisation. This represents a conservative "
        "baseline assuming no operational changes. "
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
- **Missing property type** (2 points): The building's use category is not recorded.
- **Missing or above-median Site EUI** (2 points): The building's energy use intensity is missing or higher than the dataset median.
- **Large floor area** (1 point): Buildings over 100,000 sq ft have greater emissions impact.

Scores of 6 or above are flagged as High priority. Scores of 3-5 are Moderate. Below 3 is Low.

**How is the compliance gap calculated?**

The tool compares each building's reported GHG intensity (kg CO2e per square foot per year)
against the BERDO 2.0 emissions limits for its property type. If the building exceeds the limit,
the tool estimates the annual Alternative Compliance Payment (ACP) at $234 per excess metric
ton of CO2e. GHG intensity is held constant at the current reported value.

**How is the fuel breakdown calculated?**

Individual fuel emissions columns from the BERDO dataset are grouped into four categories:
Electricity, Steam/District, Natural Gas, and Fossil Fuels. The projected chart applies
BERDO's official grid decarbonisation factors (Boston APCC Policies and Procedures,
Appendix B, 2025) to the electricity component only.

Source: BERDO 2.0 Draft Phase 1 Regulations (Boston APCC, 2021).
Not an official City of Boston compliance determination.
""")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
COLUMN_RENAME_MAP = {
    "Largest Property Type":                        "property_type",
    "Reported Gross Floor Area (Sq Ft)":            "gross_floor_area",
    "Site EUI (Energy Use Intensity kBtu/ft2)":     "site_eui",
    "Site EUI (Energy Use Intensity kBtu/ft\u00b2)": "site_eui",
    "Estimated Total GHG Emissions (kgCO2e)":       "ghg_emissions",
    "Estimated Total GHG Emissions e(kgCO2e)":      "ghg_emissions",
    "Total GHG Emissions - Estimated (kgCO2e)":     "ghg_emissions",
    "Reporting Compliance Status":                  "compliance_status",
    "Compliance Status":                            "compliance_status",
    "First Emissions Compliance Year (Projected)":  "compliance_year",
}

REQUIRED_COLUMNS = [
    "Building Address", "Property Owner Name", "property_type",
    "gross_floor_area", "site_eui", "ghg_emissions",
]


@st.cache_data
def _load_single_csv(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df.columns = df.columns.astype(str).str.strip()
    df = df.rename(columns=COLUMN_RENAME_MAP)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns in {file_path.name}: {missing}. "
            f"Available: {list(df.columns)}"
        )

    df["gross_floor_area"] = pd.to_numeric(df["gross_floor_area"], errors="coerce")
    df["site_eui"]         = pd.to_numeric(df["site_eui"],         errors="coerce")
    df["ghg_emissions"]    = pd.to_numeric(df["ghg_emissions"],    errors="coerce")

    all_fuel_cols = [col for cols in FUEL_EMISSION_COLS.values() for col in cols]
    for col in all_fuel_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0.0

    valid = (
        df["ghg_emissions"].notna() &
        df["gross_floor_area"].notna() &
        (df["gross_floor_area"] > 0)
    )
    df["ghg_intensity_kgco2e_sqft"] = pd.NA
    df.loc[valid, "ghg_intensity_kgco2e_sqft"] = (
        df.loc[valid, "ghg_emissions"] / df.loc[valid, "gross_floor_area"]
    )

    # defensive compliance_status handling
    if "compliance_status" in list(df.columns):
        df["compliance_status"] = (
            df["compliance_status"].astype(str).str.lower().str.strip()
        )
    elif "Compliance Status" in list(df.columns):
        df["compliance_status"] = (
            df["Compliance Status"].astype(str).str.lower().str.strip()
        )
    elif "Reporting Compliance Status" in list(df.columns):
        df["compliance_status"] = (
            df["Reporting Compliance Status"].astype(str).str.lower().str.strip()
        )
    else:
        import sys
        print("compliance_status not found. Available columns:", list(df.columns), file=sys.stderr)
        df["compliance_status"] = "unknown"

    if "compliance_year" not in df.columns:
        df["compliance_year"] = pd.NA

    return df


@st.cache_data
def load_all_years() -> dict[int, pd.DataFrame]:
    data_dir   = Path("data")
    year_files = sorted(data_dir.glob("berdo_*.csv"))

    year_map: dict[int, pd.DataFrame] = {}
    for fp in year_files:
        stem = fp.stem
        try:
            year = int(stem.split("_")[1])
        except (IndexError, ValueError):
            continue
        year_map[year] = _load_single_csv(fp)

    if not year_map:
        legacy = data_dir / "berdo.csv"
        if not legacy.exists():
            raise FileNotFoundError(
                "Dataset not found. Place a CSV at data/berdo.csv, "
                "or use per-year files named data/berdo_<year>.csv "
                "(e.g. data/berdo_2023.csv)."
            )
        year_map[0] = _load_single_csv(legacy)

    return year_map


# ---------------------------------------------------------------------------
# Priority scoring
# ---------------------------------------------------------------------------
def assign_priority(row, median_eui):
    score   = 0
    reasons = []

    if str(row.get("compliance_status", "")).lower() == "not submitted":
        score += 3
        reasons.append("Building is marked as not submitted")

    if pd.isna(row.get("property_type")):
        score += 2
        reasons.append("Property type is missing")

    site_eui = row.get("site_eui")
    if pd.isna(site_eui):
        score += 2
        reasons.append("Site EUI is missing")
    elif site_eui >= median_eui:
        score += 2
        reasons.append("Site EUI is above the dataset median")

    gfa = row.get("gross_floor_area")
    if pd.notna(gfa) and gfa >= 100000:
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
    address_clean = re.split(r",", address)[0].strip()
    matches = df[
        df["Building Address"].astype(str).str.contains(
            address_clean, case=False, na=False
        )
    ]
    if matches.empty:
        return None

    median_eui = df["site_eui"].median()
    results    = []
    fuel_cols  = [col for cols in FUEL_EMISSION_COLS.values() for col in cols]

    for _, row in matches.iterrows():
        priority, score, reasons = assign_priority(row, median_eui)
        fuel_data = {col: row.get(col, 0) for col in fuel_cols}
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
            **fuel_data,
        })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Year-over-year trend chart
# ---------------------------------------------------------------------------
def render_yoy_trend(address, all_years: dict[int, pd.DataFrame]):
    years_sorted = sorted(y for y in all_years if y != 0)
    if len(years_sorted) < 2:
        return None, None

    import re
    address_clean = re.split(r",", address)[0].strip()

    records = []
    for yr in years_sorted:
        df      = all_years[yr]
        matches = df[
            df["Building Address"].astype(str).str.contains(
                address_clean, case=False, na=False
            )
        ]
        if matches.empty:
            continue
        row = matches.iloc[0]
        ghg = pd.to_numeric(row.get("ghg_intensity_kgco2e_sqft"), errors="coerce")
        eui = pd.to_numeric(row.get("site_eui"), errors="coerce")
        records.append({"year": yr, "ghg_intensity": ghg, "site_eui": eui})

    if len(records) < 2:
        return None, None

    trend_df = pd.DataFrame(records)

    st.subheader("Year-over-Year Trend")

    latest = trend_df.iloc[-1]
    prior  = trend_df.iloc[-2]

    ghg_delta = latest["ghg_intensity"] - prior["ghg_intensity"]
    eui_delta = latest["site_eui"]      - prior["site_eui"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label=f"GHG Intensity {int(latest['year'])} (kg CO2e/sf/yr)",
            value=f"{latest['ghg_intensity']:.3f}" if pd.notna(latest["ghg_intensity"]) else "N/A",
            delta=f"{ghg_delta:+.3f} vs {int(prior['year'])}" if pd.notna(ghg_delta) else None,
            delta_color="inverse",
        )
    with col2:
        st.metric(
            label=f"Site EUI {int(latest['year'])} (kBtu/sf/yr)",
            value=f"{latest['site_eui']:.1f}" if pd.notna(latest["site_eui"]) else "N/A",
            delta=f"{eui_delta:+.1f} vs {int(prior['year'])}" if pd.notna(eui_delta) else None,
            delta_color="inverse",
        )
    with col3:
        n_ghg       = trend_df["ghg_intensity"].notna().sum()
        missing_ghg = trend_df.loc[trend_df["ghg_intensity"].isna(), "year"].astype(int).tolist()
        st.metric(label="Years of GHG data", value=int(n_ghg))
        if missing_ghg:
            st.caption(f"No data: {', '.join(str(y) for y in missing_ghg)}")
        else:
            st.caption("All years present")
    with col4:
        n_eui       = trend_df["site_eui"].notna().sum()
        missing_eui = trend_df.loc[trend_df["site_eui"].isna(), "year"].astype(int).tolist()
        st.metric(label="Years of EUI data", value=int(n_eui))
        if missing_eui:
            st.caption(f"No data: {', '.join(str(y) for y in missing_eui)}")
        else:
            st.caption("All years present")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=trend_df["year"].astype(str),
        y=trend_df["ghg_intensity"],
        name="GHG Intensity (kg CO2e/sf/yr)",
        mode="lines+markers",
        line=dict(color="#E24B4A", width=2),
        marker=dict(size=8),
        connectgaps=True,
    ))

    fig.add_trace(go.Bar(
        x=trend_df["year"].astype(str),
        y=trend_df["site_eui"],
        name="Site EUI (kBtu/sf/yr)",
        marker_color="#3266ad",
        opacity=0.45,
        yaxis="y2",
    ))

    fig.update_layout(
        xaxis_title="Reporting year",
        xaxis_type="category",
        yaxis=dict(title="GHG Intensity (kg CO2e/sf/yr)", side="left"),
        yaxis2=dict(
            title="Site EUI (kBtu/sf/yr)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=320,
        margin=dict(t=40, b=40, l=60, r=60),
        bargap=0.4,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.12)")

    st.plotly_chart(fig, use_container_width=True, key="yoy_trend_chart")

    if 2022 in [r["year"] for r in records] and \
       trend_df.loc[trend_df["year"] == 2022, "ghg_intensity"].isna().all():
        st.caption(
            "2022 GHG intensity is not shown -- the City of Boston did not publish "
            "GHG emissions totals in that year's dataset."
        )

    prior_ghg   = prior["ghg_intensity"] if pd.notna(prior["ghg_intensity"]) else None
    prior_label = str(int(prior["year"]))
    return prior_ghg, prior_label


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------
all_years       = load_all_years()
years_sorted    = sorted(y for y in all_years if y != 0)
multi_year_mode = len(years_sorted) >= 2

if multi_year_mode:
    st.sidebar.header("Data year")
    selected_year = st.sidebar.radio(
        "Select reporting year to screen:",
        options=years_sorted,
        index=len(years_sorted) - 1,
        format_func=str,
        horizontal=False,
    )
    df_full  = all_years[selected_year]
    show_yoy = st.sidebar.toggle("Show year-over-year comparison", value=True)
else:
    selected_year = years_sorted[0] if years_sorted else 0
    df_full       = all_years[selected_year]
    show_yoy      = False

st.title("BERDO Building Priority Screening Tool")
st.write(
    "Enter a Boston building address to see its priority level for BERDO "
    "reporting support, outreach, or retrofit planning -- and to estimate "
    "fine exposure under the 2025, 2030, and 2035 emissions standards."
)

if multi_year_mode:
    year_range_str = f"{years_sorted[0]}-{years_sorted[-1]}"
    st.info(
        f"Showing data for {selected_year}. "
        f"Multi-year data loaded: {year_range_str}. "
        "Use the sidebar to switch years or toggle the trend view."
    )
else:
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

        top    = result.iloc[0]
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
- **Not submitted**: No data was reported. Buildings required to report under BERDO face fines of $300/day for missing the May 15 annual deadline.

**Site EUI (Energy Use Intensity)**
- Measures how much energy a building uses per square foot per year (kBtu/sq ft/yr).

**GHG Intensity (kg CO2e/sq ft/yr)**
- The building's greenhouse gas emissions per square foot per year, compared against BERDO emissions limits to determine compliance.

**Priority Score**
- A screening score (0-8) used to flag buildings that may need outreach, reporting support, or retrofit planning.
""")

        st.markdown("---")

        prior_ghg, prior_label = None, None
        if show_yoy and multi_year_mode:
            prior_ghg, prior_label = render_yoy_trend(address_input, all_years)
            st.markdown("---")

        render_compliance_section(
            top,
            prior_year_ghg_intensity=prior_ghg,
            prior_year_label=prior_label,
        )
