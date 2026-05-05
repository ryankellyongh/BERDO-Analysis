# BERDO Analysis

Identifying High-Impact Emissions Reduction Opportunities in Boston Buildings.

## Introduction
Boston’s Building Emissions Reduction and Disclosure Ordinance (BERDO) requires large buildings to report energy use, emissions, and reduce operational carbon over time. This project analyzes Boston’s 2025 reported energy and water metrics dataset to evaluate compliance patterns, building performance, and opportunities for targeted intervention. The goal is not only to identify high-energy buildings, but to understand which buildings require reporting support versus deeper decarbonization planning.

## Key Takeaway

BERDO compliance is not only an energy performance challenge. It is also a data visibility, reporting capacity, and ownership coordination issue. The buildings most in need of support are not limited to those with high Site EUI; they also include buildings missing basic reporting information, especially property type and energy use data. Considering missing data as an early warning signal can help identify where outreach, technical assistance, and retrofit planning should be prioritized.


## Dataset

**Source**

2025 Reported Energy and Water Metrics
City of Boston BERDO Public Reporting Data

File Location:
data/2025-reported-energy-and-water-metrics.xlsx

Key Variables Analyzed

• Compliance Status

• Property Type

• Site Energy Use Intensity (EUI)

• Total Site Energy Usage

• GHG Emissions

• Gross Floor Area

• Building Location

• Ownership Type

These variables help evaluate how buildings are performing under BERDO requirements and where intervention may be most effective.

## Methods
The analysis was conducted using Python and followed a structured workflow:

**Data Preparation**

• Standardized column names

• Renamed variables for clarity

• Removed missing values in critical fields

• Consolidated compliance labels

• Cleaned reporting inconsistencies


**Analysis Performed**

• Compliance distribution analysis

• Property type frequency analysis

• Average EUI by compliance status

• High-priority building identification

• Correlation analysis between building size and energy intensity

• Missing data pattern analysis

## Key Findings

• 3,569 buildings are currently in compliance

• 223 buildings remain in pending revisions

• 116 buildings are under the State Pathway

• Multifamily Housing represents the largest building category, with more than 2,000 buildings

• Buildings with higher EUI consistently face greater compliance challenges

• Fossil fuel dependence remains common, indicating significant electrification opportunities

• Some neighborhoods show higher concentrations of non-submitted buildings, suggesting reporting gaps and capacity barriers

## Why This Matters

BERDO is one of Boston’s most important climate policies for reducing building emissions.

Understanding compliance patterns helps answer:
Which buildings need reporting support? vs. Which buildings need deeper retrofit planning?

This helps stakeholders:

• Prioritize technical assistance

• Improve compliance rates

• Target financing programs

• Reduce emissions more effectively

• Support equitable decarbonization

This project supports data-driven decision-making for climate policy and building performance strategy.

## Tools Used

• Python

• pandas

• NumPy

• matplotlib

• Jupyter Notebook

• Excel


## How to Run

1. Clone the repository
bashgit clone https://github.com/ryankellyongh/berdo-energy-analysis.git
cd berdo-energy-analysis

3. Install dependencies
bashpip install -r requirements.txt

5. Download the data
Download the 2025 Reported Energy and Water Metrics dataset from the City of Boston BERDO Public Reporting Data and save it to:
data/2025-reported-energy-and-water-metrics.xlsx

7. Run the notebook
bashjupyter notebook analysis/berdo-analysis.ipynb
Run all cells top to bottom. All outputs and visualizations will generate automatically.


**Author**

Ryan Kelly

Data Analytics Student | Northeastern University

Focused on sustainability analytics, building performance, and using data to support climate policy and operational decision-making.
