# BERDO Analysis

Identifying Reporting Gaps, Energy Performance Risks, and Emissions Reduction Opportunities in Boston Buildings

## Introduction

Boston’s Building Emissions Reduction and Disclosure Ordinance (BERDO) requires large buildings to report energy use, emissions, and reduce operational carbon over time. This project analyzes Boston’s 2025 reported energy and water metrics dataset to evaluate compliance patterns, building performance, and opportunities for targeted intervention. The goal is not only to identify high-energy buildings, but to understand which buildings require reporting support versus deeper decarbonization planning.

## Interactive Tool

This project also includes a Streamlit-based BERDO Building Priority Screening Tool. The calculator allows a user to enter a Boston building address and receive a screening-based priority level for reporting support, outreach, or retrofit planning.

The tool uses indicators such as compliance status, missing property type, missing Site EUI, building size, and energy performance flags to classify buildings as low, moderate, or high priority. The tool also displays greenhouse gas emissions intensity to provide BERDO-relevant emissions context.

![images/BERDO Building Priority Screening Tool.jpg]


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

**Priority Calculator Method**

The BERDO Building Priority Calculator uses a point-based screening system to estimate whether a building should be considered low, moderate, or high priority for outreach or planning.

| Indicator | Reason |
|---|---|
| Not submitted status | Suggests the building may need reporting support |
| Missing property type | Limits building classification and comparison |
| Missing Site EUI | Prevents basic energy performance screening |
| Above-median Site EUI | Suggests possible need for retrofit planning |
| Large reported floor area | Indicates greater potential scale of impact |

| Score Range | Priority Level |
|---|---|
| 0–2 | Low |
| 3–5 | Moderate |
| 6+ | High |

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

2. Run the Streamlit app

```
streamlit run "berdo building priority screening tool/app.py"
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
