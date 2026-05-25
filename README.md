# BERDO Analysis

*Identifying Reporting Gaps, Energy Performance Risks, and Emissions Reduction Opportunities in Boston Buildings*

Boston's Building Emissions Reduction and Disclosure Ordinance (BERDO 2.0) sets declining greenhouse gas emissions limits for large buildings through 2050 — but compliance is not just an energy performance challenge. It is also a data visibility, reporting capacity, and ownership coordination problem. The buildings most in need of support are often not the highest energy users; they are the ones with missing property types, unreported energy data, or no record of submission at all.

This project analyzes Boston's BERDO public reporting data to evaluate compliance patterns, building performance, and opportunities for targeted intervention — and includes a live screening tool that helps identify which buildings need attention first.

---

## Interactive Tool

The BERDO Building Priority Screening Tool is a Streamlit app that lets anyone look up a Boston building by address and receive an immediate, multi-dimensional assessment of its compliance status and emissions trajectory.

**Live app:** https://berdo-building-priority-screening-tool.streamlit.app

![BERDO Building Priority Screening Tool](images/BERDO%20Building%20Priority%20Screening%20Tool.png)

Enter an address and the tool returns:

- A **priority classification** (Low / Moderate / High) with a numeric score and plain-language explanation
- A **compliance gap estimate** showing how far the building is from the 2025, 2030, and 2035 BERDO emissions limits, and what the Alternative Compliance Payment (ACP) exposure would be if nothing changes
- A **year-over-year trend view** tracking GHG intensity and Site EUI from 2021 through 2025, with delta metrics versus the prior year and a dual-axis chart across all available reporting years
- A **grid decarbonization scenario** that projects how a cleaner electricity grid affects a building's compliance position through 2050

A sidebar year selector lets users switch between reporting years (2021–2025). The prior-year intensity overlay on the compliance gap chart shows whether a building is moving toward or away from the tightening emissions limits.

![Year Selector Sidebar](images/Year%20selector.png)
![Year-over-Year Trend](images/Year%20trend%20section.png)

### Who it's for

City sustainability staff, outreach coordinators, community organizations, and retrofit planners who need to triage a large portfolio of buildings and focus limited resources where they matter most.

This tool is designed for screening and prioritization — not official compliance determination. Results are intended to guide outreach, technical assistance, and retrofit planning conversations.

### Why it exists

The City of Boston's official BERDO Emissions Calculator projects compliance for a single building given specific retrofit interventions. It is a depth tool. This is a breadth tool, built to answer a different question: *which buildings should we focus on first?*

No publicly available City tool currently provides priority scoring, multi-year trend analysis, or outreach triage across the full BERDO portfolio.

### Priority score methodology

The calculator uses a point-based screening system to classify buildings as Low, Moderate, or High priority.

| Indicator | Points | Rationale |
|---|---|---|
| Not submitted | 3 | Building did not report data by the May 15 deadline |
| Missing property type | 2 | Use category is unrecorded, preventing accurate emissions benchmarking |
| Missing or above-median Site EUI | 2 | Energy use intensity is absent or exceeds the dataset median |
| Large floor area (100,000+ sq ft) | 1 | Greater floor area correlates with larger emissions impact |

**Priority tiers:**

| Score | Priority Level |
|---|---|
| 0–2 | 🟢 Low |
| 3–5 | 🟡 Moderate |
| 6+ | 🔴 High |

> **Method note:** Site EUI is used as a screening metric. Official BERDO compliance is determined by greenhouse gas emissions intensity, not Site EUI alone.

### Compliance gap methodology

The tool compares each building's reported GHG intensity (kg CO₂e per sq ft per year) against the BERDO 2.0 emissions limits for its property type, covering all 13 large property type categories sourced from the Boston APCC Phase 1 Regulations. A mapping layer translates Energy Star Portfolio Manager property type names to BERDO categories. Buildings exceeding their limit receive an estimated ACP at **$234 per excess metric ton of CO₂e**.

This tool is intended for planning and outreach purposes only. It does not constitute an official City of Boston compliance determination.

---

## Key Takeaway

BERDO compliance is not only an energy performance challenge. It is also a data visibility, reporting capacity, and ownership coordination issue. The buildings most in need of support are not limited to those with high Site EUI — they also include buildings missing basic reporting information, especially property type and energy use data. Treating missing data as an early warning signal, rather than a data quality problem, is what distinguishes a triage tool from a compliance tracker.

---

## Key Findings

- **3,569 buildings** are listed as in compliance in the 2025 reporting dataset
- **223 buildings** remain in pending revisions; **116** are under the State Pathway
- **Multifamily housing** is the largest building category, with more than 2,000 buildings
- Buildings with high Site EUI likely require deeper performance review; buildings with missing data likely require reporting support — these are distinct intervention types
- Natural gas usage appears across many submitted records, suggesting broad potential for electrification planning
- Preliminary location patterns suggest some neighborhoods have higher concentrations of non-submitted buildings, pointing to reporting gaps that may reflect capacity barriers rather than indifference

---

## Dataset

**Source:** 2025 Reported Energy and Water Metrics — City of Boston BERDO Public Reporting Data  
`data/2025-reported-energy-and-water-metrics.xlsx`

The multi-year trend view draws on five normalized CSVs covering 2021–2025, standardized from the city's annual public releases. Each year required custom column mapping and unit handling — notably, 2021 GHG emissions were published in MTCO2e and converted to kgCO2e, and 2022 did not include a GHG emissions column.

**Key variables:** Compliance status · Property type · Site EUI · Total site energy use · GHG emissions · Gross floor area · Building location · Inferred ownership category

---

## Methods

Analysis was conducted in Python following a structured workflow.

**Data preparation:** Standardized column names, consolidated compliance labels, created separate datasets for complete performance records and missing-data analysis, cleaned reporting inconsistencies

**Analysis performed:** Compliance distribution · Property type frequency · Average EUI by compliance status · High-priority building identification · Correlation analysis between building size and energy intensity · Missing data pattern analysis

---

## Why This Matters

BERDO is one of Boston's most important climate policies for reducing building emissions. Understanding compliance patterns helps distinguish which buildings need reporting support from which need deeper retrofit planning — a distinction that matters for how limited technical assistance, financing, and city outreach capacity gets allocated.

This project supports data-driven decision-making for climate policy and building performance strategy.

---

## Tools Used

Python · pandas · NumPy · matplotlib · Streamlit · Plotly · openpyxl · Jupyter Notebook

---

## Setup

### Analysis notebook

```bash
git clone https://github.com/ryankellyongh/BERDO-Analysis.git
cd BERDO-Analysis
pip install -r requirements.txt
```

Download the 2025 dataset from the City of Boston BERDO Public Reporting Data and save to:
```
data/2025-reported-energy-and-water-metrics.xlsx
```

Then run:
```bash
jupyter notebook "analysis/BERDO Analysis.ipynb"
```

Run all cells from top to bottom. All outputs and visualizations will generate automatically.

### Screening tool

```bash
pip install -r requirements.txt
cd "BERDO Analysis"
streamlit run app.py
```

Enter any Boston address — for example, `1047 Commonwealth` — to return the building's priority level, score, and explanation.

---

## Author

**Ryan Kelly**  
Data Analytics Student — Northeastern University

Focused on sustainability analytics, building performance, and using data to support climate policy and operational decision-making.

[GitHub](https://github.com/ryankellyongh) · [LinkedIn]
