# BERDO Analysis

Identifying Reporting Gaps, Energy Performance Risks, and Emissions Reduction Opportunities in Boston Buildings

## Introduction

Boston’s Building Emissions Reduction and Disclosure Ordinance (BERDO) requires large buildings to report energy use, emissions, and reduce operational carbon over time. This project analyzes Boston’s 2025 reported energy and water metrics dataset to evaluate compliance patterns, building performance, and opportunities for targeted intervention. The goal is not only to identify high-energy buildings, but to understand which buildings require reporting support versus deeper decarbonization planning.

## Interactive Tool

This project also includes a Streamlit-based BERDO Building Priority Screening Tool. The calculator allows a user to enter a Boston building address and receive a screening-based priority level for reporting support, outreach, or retrofit planning.

The tool uses indicators such as compliance status, missing property type, missing Site EUI, building size, and energy performance flags to classify buildings as low, moderate, or high priority. The tool also displays greenhouse gas emissions intensity to provide BERDO-relevant emissions context.

Update (05/11) — BERDO Compliance Gap Calculator

I've added a compliance gap calculator to my BERDO building screening tool.

The new features include:

- A BERDO 2.0 emissions standards table covering all 13 large property types, sourced from the Boston APCC Phase 1 Regulations.

- A mapping layer that translates Energy Star Portfolio Manager property type names to BERDO categories.

- A gap calculation function that uses each building's reported GHG intensity and floor area to compute excess metric tons and projected fine exposure.

- A display section with metric cards and a Plotly chart showing a building's current emissions intensity against the declining 2025, 2030, and 2035 targets.

Search a Boston address and the tool now tells you not just priority level, but exactly how far the building is from each compliance threshold — and what the Alternative Compliance Payment would be if nothing changes.

Output: 

![BERDO Building Priority Screening Tool](images/BERDO%20Building%20Priority%20Screening%20Tool.png)

## Key Takeaway

BERDO compliance is not only an energy performance challenge. It is also a data visibility, reporting capacity, and ownership coordination issue. The buildings most in need of support are not limited to those with high Site EUI; they also include buildings missing basic reporting information, especially property type and energy use data. Considering missing data as an early warning signal can help identify where outreach, technical assistance, and retrofit planning should be prioritized.


## Dataset

**Source**

2025 Reported Energy and Water Metrics
City of Boston BERDO Public Reporting Data

File Location:
data/2025-reported-energy-and-water-metrics.xlsx

Key Variables Analyzed

- Compliance Status

- Property Type

- Site Energy Use Intensity (EUI)

- Total Site Energy Usage

- GHG Emissions

- Gross Floor Area

- Building Location

- Inferred Ownership Category

These variables help evaluate how buildings are performing under BERDO requirements and where intervention may be most effective.

## Methods
The analysis was conducted using Python and followed a structured workflow:

**Data Preparation**

- Standardized column names

- Renamed variables for clarity

- Created separate datasets for complete performance records and missing-data analysis

- Consolidated compliance labels

- Cleaned reporting inconsistencies


**Method Note**

Site EUI is used as a screening metric in this project. Official BERDO emissions compliance is based on greenhouse gas emissions intensity, not Site EUI alone.


**Analysis Performed**

- Compliance distribution analysis

- Property type frequency analysis

- Average EUI by compliance status

- High-priority building identification

- Correlation analysis between building size and energy intensity

- Missing data pattern analysis

Here's a revised version polished for a GitHub README:


## Priority Calculator Methodology
 
The BERDO Building Priority Calculator uses a point-based screening system to classify buildings as **Low**, **Moderate**, or **High** priority for outreach or retrofit planning.
 
---
 
### How the Priority Score Works
 
Each building is scored across four indicators:
 
| Indicator | Points | Rationale |
|---|---|---|
| Not submitted | 3 | Building did not report data to the City of Boston by the May 15 deadline |
| Missing property type | 2 | Use category is unrecorded, preventing accurate emissions benchmarking |
| Missing or above-median Site EUI | 2 | Energy use intensity is absent or exceeds the dataset median, suggesting potential inefficiency |
| Large floor area (100,000+ sq ft) | 1 | Greater floor area correlates with larger emissions impact |
 
**Priority tiers:**
 
| Score | Priority Level |
|---|---|
| 0–2 | 🟢 Low |
| 3–5 | 🟡 Moderate |
| 6+ | 🔴 High |
 
---
 
### How the Compliance Gap Is Calculated
 
The tool compares each building's reported GHG intensity (kg CO₂e per sq ft per year) against the BERDO 2.0 emissions limits for its property type. Buildings that exceed their limit receive an estimated annual **Alternative Compliance Payment (ACP)**, calculated at **$234 per excess metric ton of CO₂e**.
 
> **Source:** BERDO 2.0 Draft Phase 1 Regulations (Boston APCC, 2021).
> This tool is intended for planning and outreach purposes only — it does not constitute an official City of Boston compliance determination.


## Key Findings

- 3,569 buildings are listed as “In Compliance” in the reporting status field

- 223 buildings remain in pending revisions

- 116 buildings are under the State Pathway

- Multifamily Housing represents the largest building category, with more than 2,000 buildings

- Buildings with higher Site EUI may require deeper performance review, while buildings with missing data may require reporting support

- Natural gas usage appears across many submitted records, suggesting potential opportunities for electrification planning

- Preliminary location patterns suggest that some areas may have higher concentrations of non-submitted buildings, which may point to reporting gaps and capacity barriers

## Why This Matters

BERDO is one of Boston’s most important climate policies for reducing building emissions.

Understanding compliance patterns helps answer:
Which buildings need reporting support? vs. Which buildings need deeper retrofit planning?

This helps stakeholders:

- Prioritize technical assistance

- Improve compliance rates

- Target financing programs

- Reduce emissions more effectively

- Support equitable decarbonization

This project supports data-driven decision-making for climate policy and building performance strategy.

## Tools Used

- Python

- pandas

- NumPy

- matplotlib
 
- Streamlit

- openpyxl

- Jupyter Notebook

- Excel

## How to Run the Analysis Notebook

1. Clone the repository

```bash
git clone https://github.com/ryankellyongh/BERDO-Analysis.git
cd BERDO-Analysis
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Download the data

Download the 2025 Reported Energy and Water Metrics dataset from the City of Boston BERDO Public Reporting Data and save it to:

```text
data/2025-reported-energy-and-water-metrics.xlsx
```

4. Run the notebook

```bash
jupyter notebook "analysis/BERDO Analysis.ipynb"
```

Run all cells from top to bottom. All outputs and visualizations will generate automatically.

## How to Run the BERDO Building Priority Screening Tool

1. Make sure the required packages are installed.

```bash
pip install -r requirements.txt
```

2. Navigate to the project folder and run the Streamlit app.

```
cd "BERDO Analysis"
streamlit run app.py
```

3. Enter building address in the search box

Example:
```
 1047 Commonwealth
```

The app will return the building’s priority level, score, and explanation.

**Important Note:** The BERDO Building Priority Screening Tool is for analytical screening purposes only. It is not an official City of Boston BERDO compliance determination.


## Author

Ryan Kelly

Data Analytics Student | Northeastern University

Focused on sustainability analytics, building performance, and using data to support climate policy and operational decision-making.
