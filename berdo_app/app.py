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
# Projected ISO New England grid emissions factors by year
# Source: BERDO Emissions Factors List, Appendix B (updated May 5, 2026)
# Units: kg CO2e / MWh
# ---------------------------------------------------------------------------
PROJECTED_GRID_EF = {
    2022: 270, 2023: 263, 2024: 256, 2025: 249, 2026: 242,
    2027: 265, 2028: 265, 2029: 264, 2030: 259, 2031: 254,
    2032: 249, 2033: 243, 2034: 237, 2035: 231, 2036: 224,
    2037: 217, 2038: 211, 2039: 204, 2040: 198, 2041: 192,
    2042: 187, 2043: 182, 2044: 177, 2045: 173, 2046: 168,
    2047: 163, 2048: 159, 2049: 155, 2050: 150,
}

# Representative year for each compliance period (midpoint, or period start for 2050+)
PERIOD_REPRESENTATIVE_YEARS = [2027, 2032, 2037, 2042, 2047, 2050]

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
# Grid decarbonization projection
# ---------------------------------------------------------------------------
def project_ghg_intensities(ghg_intensity, elec_share, base_year):
    """
    Project GHG intensity for each compliance period assuming:
      - Electricity component shrinks as the grid decarbonizes
        (using Appendix B projected grid EFs)
      - Fossil fuel component stays constant (no operational changes)

    Returns a list of 6 projected intensities, one per COMPLIANCE_PERIODS entry.
    Falls back to the base_year EF if base_year is not in PROJECTED_GRID_EF.
    """
    base_ef = PROJECTED_GRID_EF.get(base_year, PROJECTED_GRID_EF[2025])
    if base_ef == 0:
        return [ghg_intensity] * len(COMPLIANCE_PERIODS)

    elec_intensity   = ghg_intensity * elec_share
    fossil_intensity = ghg_intensity * (1.0 - elec_share)

    projected = []
    for yr in PERIOD_REPRESENTATIVE_YEARS:
        future_ef = PROJECTED_GRID_EF.get(yr, base_ef)
        future_elec = elec_intensity * (future_ef / base_ef)
        projected.append(round(fossil_intensity + future_elec, 3))
    return projected


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
def render_compliance_section(
    row,
    prior_year_ghg_intensity=None,
    prior_year_label=None,
    projected_intensities=None,
    base_year=2025,
):
    """
    projected_intensities: list of 6 floats (one per compliance period) from
    project_ghg_intensities(), or None to skip the grid decarb overlay.
    """
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

    # Projected gaps (for grid decarb scenario metric cards)
    if projected_intensities is not None:
        proj_gaps = [
            calculate_compliance_gap(pi, sqft, berdo_category)
            for pi in projected_intensities
        ]
        # proj_gaps[i] is a list of 6 period gaps for the projected intensity at period i
        # We only need the gap for each period against its own limit, i.e. proj_gaps[i][i]
        proj_gap_for_period = [proj_gaps[i][i] for i in range(len(COMPLIANCE_PERIODS))]
    else:
        proj_gap_for_period = None

    st.caption(
        f"Current intensity: **{ghg_intensity:.3f} kg CO₂e/sf/yr** · "
        f"Floor area: **{int(sqft):,} sq ft** · "
        f"BERDO category: **{berdo_category}**"
    )

    # --- Metric cards (first 3 periods) ---
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
                # Show projected outcome if available
                if proj_gap_for_period is not None:
                    pg = proj_gap_for_period[i]
                    if pg["compliant"]:
                        st.caption("🌱 Grid scenario: compliant")
                    else:
                        st.caption(
                            f"🌱 Grid scenario: +{pg['gap']:.2f} kg over limit "
                            f"(${pg['annual_fine_usd']:,.0f}/yr)"
                        )

    st.markdown("---")

    # --- Chart ---
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
        name="Conservative (no change)",
        mode="lines",
        line=dict(color="#E24B4A", width=2, dash="dash"),
    ))

    # Grid decarbonization scenario overlay
    if projected_intensities is not None:
        fig.add_trace(go.Scatter(
            x=COMPLIANCE_PERIODS,
            y=projected_intensities,
            name="Grid decarbonization scenario",
            mode="lines+markers",
            line=dict(color="#2ECC71", width=2),
            marker=dict(size=7, symbol="diamond"),
        ))

    # Optional prior-year intensity overlay
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
        name="Annual ACP fine — conservative (USD)",
        mode="lines+markers",
        yaxis="y2",
        line=dict(color="#BA7517", width=1.5, dash="dot"),
        marker=dict(size=6),
        visible="legendonly",
    ))

    if projected_intensities is not None:
        proj_fines = [
            calculate_compliance_gap(pi, sqft, berdo_category)[i]["annual_fine_usd"]
            for i, pi in enumerate(projected_intensities)
        ]
        fig.add_trace(go.Scatter(
            x=COMPLIANCE_PERIODS,
            y=proj_fines,
            name="Annual ACP fine — grid scenario (USD)",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#27AE60", width=1.5, dash="dot"),
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
        height=400,
        margin=dict(t=40, b=40, l=60, r=60),
        bargap=0.35,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.12)")

    st.plotly_chart(fig, use_container_width=True, key=f"compliance_chart_{id(row)}")

    # --- Fine exposure summary ---
    non_compliant_periods = [g for g in gaps if not g["compliant"]]
    if non_compliant_periods:
        total_5yr_fine = sum(g["annual_fine_usd"] * 5 for g in non_compliant_periods)
        msg = (
            f"**Conservative scenario:** if no emissions reductions are made, this building "
            f"faces an estimated **${total_5yr_fine:,.0f}** in cumulative ACP payments across "
            f"{len(non_compliant_periods)} non-compliant period(s) "
            f"(annual fine × 5 years per period)."
        )
        if projected_intensities is not None:
            proj_non_compliant = [
                proj_gap_for_period[i]
                for i in range(len(COMPLIANCE_PERIODS))
                if not proj_gap_for_period[i]["compliant"]
            ]
            total_proj_fine = sum(g["annual_fine_usd"] * 5 for g in proj_non_compliant)
            if proj_non_compliant:
                msg += (
                    f"\n\n**Grid decarbonization scenario:** estimated **${total_proj_fine:,.0f}** "
                    f"across {len(proj_non_compliant)} non-compliant period(s)."
                )
            else:
                msg += "\n\n**Grid decarbonization scenario:** building achieves compliance in all periods from grid cleaning alone."
        st.info(msg)

    # --- Caption ---
    base_ef = PROJECTED_GRID_EF.get(base_year, PROJECTED_GRID_EF[2025])
    caption = (
        "ACP = Alternative Compliance Payment at $234/metric ton CO₂e over limit. "
        "**Conservative line:** current GHG intensity held flat — no operational changes, "
        "no grid improvement. "
    )
    if projected_intensities is not None:
        caption += (
            f"**Grid decarbonization line:** electricity component scaled by ISO-NE projected "
            f"grid EFs (Appendix B, base year {base_year} = {base_ef} kg/MWh); "
            "fossil fuel use held constant. "
        )
    caption += (
        "Source: BERDO 2.0 Draft Phase 1 Regulations (Boston APCC, 2021); "
        "BERDO Emissions Factors List (City of Boston, May 2026). "
        "Not an official City of Boston compliance determination."
    )
    st.caption(caption)

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

**What is the grid decarbonization scenario?**

The ISO New England electric grid is projected to become cleaner over time as renewable energy
grows. This scenario holds fossil fuel use constant but scales down the electricity-attributed
emissions using the City of Boston's official projected grid emissions factors (Appendix B of the
BERDO Emissions Factors List). Use the sidebar slider to set the share of the building's
emissions that come from electricity. If unknown, 50% is a reasonable starting point for a
mixed-use or office building; electricity-heavy buildings (all-electric, data centers) should
use a higher value.

Source: BERDO 2.0 Draft Phase 1 Regulations (Boston APCC, 2021);
BERDO Emissions Factors List (City of Boston, updated May 5, 2026).
Not an official City of Boston compliance determination.
""")


# ---------------------------------------------------------------------------
# Data loading — supports single file (berdo.csv) or multi-year files
# (berdo_2022.csv, berdo_2023.csv, …) in the data/ folder.
# ---------------------------------------------------------------------------
COLUMN_RENAME_MAP = {
    "Largest Property Type": "property_type",
    "Reported Gross Floor Area (Sq Ft)": "gross_floor_area",
    "Site EUI (Energy Use Intensity kBtu/ft²)": "site_eui",
    "Estimated Total GHG Emissions (kgCO2e)": "ghg_emissions",
    "Estimated Total GHG Emissions e(kgCO2e)": "ghg_emissions",
    "Reporting Compliance Status": "compliance_status",
    "First Emissions Compliance Year (Projected)": "compliance_year",
}

REQUIRED_COLUMNS = [
    "Building Address", "Property Owner Name", "property_type",
    "gross_floor_area", "site_eui", "ghg_emissions",
    "compliance_status", "compliance_year",
]


@st.cache_data
def _load_single_csv(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df.columns = df.columns.astype(str).str.strip()
    df = df.rename(columns=COLUMN_RENAME_MAP)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"Missing required columns in {file_path.name}:")
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


@st.cache_data
def load_all_years() -> dict[int, pd.DataFrame]:
    """
    Returns a dict mapping year (int) → DataFrame.

    Discovery rules (in priority order):
      1. berdo_<year>.csv files  →  multi-year mode
      2. berdo.csv               →  single-year fallback (keyed as year 0)
    """
    data_dir = Path("data")
    year_files = sorted(data_dir.glob("berdo_*.csv"))

    year_map: dict[int, pd.DataFrame] = {}
    for fp in year_files:
        stem = fp.stem  # e.g. "berdo_2023"
        try:
            year = int(stem.split("_")[1])
        except (IndexError, ValueError):
            continue
        year_map[year] = _load_single_csv(fp)

    if not year_map:
        # Fallback: single legacy file
        legacy = data_dir / "berdo.csv"
        if not legacy.exists():
            st.error(
                "Dataset not found. Place a CSV at data/berdo.csv, "
                "or use per-year files named data/berdo_<year>.csv "
                "(e.g. data/berdo_2023.csv)."
            )
            st.stop()
        year_map[0] = _load_single_csv(legacy)

    return year_map


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
# Year-over-year trend chart
# ---------------------------------------------------------------------------
def render_yoy_trend(address, all_years: dict[int, pd.DataFrame]):
    """
    Searches every loaded year for the given address and renders a
    year-over-year trend chart for GHG intensity and Site EUI.
    Returns the prior-year GHG intensity (float | None) for use in the
    compliance chart overlay, and the prior-year label string.
    """
    years_sorted = sorted(y for y in all_years if y != 0)
    if len(years_sorted) < 2:
        return None, None  # Nothing to compare

    import re
    address_clean = re.split(r',', address)[0].strip()

    records = []
    for yr in years_sorted:
        df = all_years[yr]
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

    # --- Delta metrics row ---
    latest = trend_df.iloc[-1]
    prior  = trend_df.iloc[-2]

    ghg_delta  = latest["ghg_intensity"] - prior["ghg_intensity"]
    eui_delta  = latest["site_eui"]      - prior["site_eui"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label=f"GHG Intensity {int(latest['year'])} (kg CO₂e/sf/yr)",
            value=f"{latest['ghg_intensity']:.3f}" if pd.notna(latest["ghg_intensity"]) else "N/A",
            delta=f"{ghg_delta:+.3f} vs {int(prior['year'])}" if pd.notna(ghg_delta) else None,
            delta_color="inverse",   # lower is better
        )
    with col2:
        st.metric(
            label=f"Site EUI {int(latest['year'])} (kBtu/sf/yr)",
            value=f"{latest['site_eui']:.1f}" if pd.notna(latest["site_eui"]) else "N/A",
            delta=f"{eui_delta:+.1f} vs {int(prior['year'])}" if pd.notna(eui_delta) else None,
            delta_color="inverse",
        )
    with col3:
        n_ghg = trend_df["ghg_intensity"].notna().sum()
        missing_ghg = trend_df.loc[trend_df["ghg_intensity"].isna(), "year"].astype(int).tolist()
        st.metric(label="Years of GHG data", value=int(n_ghg))
        if missing_ghg:
            st.caption(f"No data: {', '.join(str(y) for y in missing_ghg)}")
        else:
            st.caption("All years present")
    with col4:
        n_eui = trend_df["site_eui"].notna().sum()
        missing_eui = trend_df.loc[trend_df["site_eui"].isna(), "year"].astype(int).tolist()
        st.metric(label="Years of EUI data", value=int(n_eui))
        if missing_eui:
            st.caption(f"No data: {', '.join(str(y) for y in missing_eui)}")
        else:
            st.caption("All years present")

    # --- Trend chart ---
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=trend_df["year"].astype(str),
        y=trend_df["ghg_intensity"],
        name="GHG Intensity (kg CO₂e/sf/yr)",
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
        yaxis=dict(title="GHG Intensity (kg CO₂e/sf/yr)", side="left"),
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

    if 2022 in [r["year"] for r in records] and trend_df.loc[trend_df["year"] == 2022, "ghg_intensity"].isna().all():
        st.caption(
            "⚠️ 2022 GHG intensity is not shown — the City of Boston did not publish "
            "GHG emissions totals in that year's dataset."
        )

    prior_ghg   = prior["ghg_intensity"] if pd.notna(prior["ghg_intensity"]) else None
    prior_label = str(int(prior["year"]))
    return prior_ghg, prior_label


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------
all_years = load_all_years()
years_sorted = sorted(y for y in all_years if y != 0)
multi_year_mode = len(years_sorted) >= 2

# --- Sidebar: year selector ---
if multi_year_mode:
    st.sidebar.header("Data year")
    selected_year = st.sidebar.radio(
        "Select reporting year to screen:",
        options=years_sorted,
        index=len(years_sorted) - 1,
        format_func=str,
        horizontal=False,
    )
    df_full = all_years[selected_year]
    show_yoy = st.sidebar.toggle("Show year-over-year comparison", value=True)
else:
    selected_year = years_sorted[0] if years_sorted else 0
    df_full = all_years[selected_year]
    show_yoy = False

# --- Sidebar: grid decarbonization scenario ---
st.sidebar.header("Grid decarbonization scenario")
show_grid_decarb = st.sidebar.toggle(
    "Show grid decarbonization scenario",
    value=False,
    help=(
        "Projects future GHG intensity assuming the ISO-NE grid cleans up "
        "per the City of Boston's official projected emissions factors "
        "(Appendix B, BERDO Emissions Factors List, May 2026). "
        "Fossil fuel use is held constant."
    ),
)
if show_grid_decarb:
    elec_share_pct = st.sidebar.slider(
        "Electricity share of GHG emissions (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        help=(
            "Estimated percentage of this building's total GHG emissions "
            "that come from grid electricity (vs. fossil fuels such as "
            "natural gas). Check the building's energy breakdown in ESPM "
            "or use 50% as a starting estimate for a typical office/mixed-use building."
        ),
    )
    elec_share = elec_share_pct / 100.0
    base_ef = PROJECTED_GRID_EF.get(selected_year, PROJECTED_GRID_EF[2025])
    st.sidebar.caption(
        f"Base year grid EF ({selected_year}): **{base_ef} kg/MWh** "
        f"(Appendix B). Projected EF at 2050: **{PROJECTED_GRID_EF[2050]} kg/MWh** "
        f"({round((1 - PROJECTED_GRID_EF[2050] / base_ef) * 100)}% cleaner)."
    )
else:
    elec_share = None

# --- Page header ---
st.title("BERDO Building Priority Screening Tool")
st.write(
    "Enter a Boston building address to see its priority level for BERDO "
    "reporting support, outreach, or retrofit planning — and to estimate "
    "fine exposure under the 2025, 2030, and 2035 emissions standards."
)

if multi_year_mode:
    year_range_str = f"{years_sorted[0]}–{years_sorted[-1]}"
    st.info(
        f"Showing data for **{selected_year}**. "
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
        st.dataframe(result[display_cols], use_container_width=True, hide_index=True)

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

        # --- Year-over-year trend (multi-year mode only) ---
        prior_ghg, prior_label = None, None
        if show_yoy and multi_year_mode:
            prior_ghg, prior_label = render_yoy_trend(address_input, all_years)
            st.markdown("---")

        # --- Grid decarbonization projection ---
        projected_intensities = None
        if show_grid_decarb and elec_share is not None:
            ghg_val = top.get("GHG Intensity (kgCO2e/sqft)")
            if pd.notna(ghg_val) and ghg_val > 0:
                projected_intensities = project_ghg_intensities(
                    ghg_intensity=float(ghg_val),
                    elec_share=elec_share,
                    base_year=selected_year if selected_year in PROJECTED_GRID_EF else 2025,
                )

        render_compliance_section(
            top,
            prior_year_ghg_intensity=prior_ghg,
            prior_year_label=prior_label,
            projected_intensities=projected_intensities,
            base_year=selected_year if selected_year in PROJECTED_GRID_EF else 2025,
        )
