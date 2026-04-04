# BERDO Compliance Analysis

## Introduction
This project analyzes BERDO (Building Emissions Reduction and Disclosure Ordinance) data for Boston buildings using the 2025 reported energy and water metrics dataset.

This analysis evaluates patterns in compliance, energy performance, and building characteristics to identify gaps and opportunities for targeted intervention.

---

## Key Insight

Buildings with higher energy use intensity (EUI) tend to fall into more complex compliance pathways, indicating that energy-intensive buildings represent the greatest opportunity for targeted emissions reduction.

Buildings under the state have an average site eui of 92 compared to 76 for compliant buildings.

---

## Data

This project uses the:

**2025 Reported Energy and Water Metrics (BERDO dataset)**

Location:
data/2025-reported-energy-and-water-metrics.xlsx

The dataset contains building-level information including:
- Compliance status (in compliance, not submitted, pending revisions)
- Property type (office, multifamily, laboratory, etc.)
- Energy Use Intensity (EUI)
- Fuel classification (fossil vs electric/possibly clean)
- Building size (square footage)
- Neighborhood and location

This data is used to evaluate how buildings are performing under BERDO requirements.

---

## Approach

The analysis was conducted using Python and follows a structured workflow:

- Data loading and cleaning
- Standardizing variables and formats
- Exploring compliance distribution
- Analyzing energy performance (EUI)
- Comparing building types and fuel classifications
- Identifying patterns across neighborhoods

---

## Key Findings

- Most buildings are in compliance, but a meaningful number remain not submitted or pending revisions
- Multifamily and office buildings make up a large share of the dataset
- Buildings with higher Energy Use Intensity (EUI) tend to face greater compliance challenges
- Fossil fuel-based buildings remain common, indicating opportunities for electrification
- Some neighborhoods show higher concentrations of non-submitted buildings, suggesting gaps in reporting or support

---

## Approach

The analysis was conducted using Python and follows a structured workflow:

- Data loading and cleaning
- Standardizing variables and formats
- Exploring compliance distribution
- Analyzing energy performance (EUI)
- Comparing building types and fuel classifications
- Identifying patterns across neighborhoods

---

## Key Findings



- 3,412 buildings are in compliance, compared to 150 pending revisions and 34 state pathways
- Multifamily and office buildings make up a large share of the dataset, acounting for 2000 plus buildings.
- Buildings with higher Energy Use Intensity (EUI) tend to face greater compliance challenges
- Fossil fuel-based buildings remain common, indicating opportunities for electrification
- Some neighborhoods show higher concentrations of non-submitted buildings, suggesting gaps in reporting or support


---

## Tools Used

- Python
- Pandas
- NumPy
- Matplotlib
- Jupyter Notebook

---

## Why This Matters

BERDO is a key policy driving building decarbonization in Boston. Understanding compliance patterns helps identify:

- Which buildings may struggle to meet future targets
- Where technical or financial support is needed
- Opportunities for emissions reduction through electrification and efficiency improvements

This analysis supports data-driven decision making for climate policy and building performance.

---

## Author

Ryan Kelly  
Data Analytics Student, Northeastern University  
Experience in building performance analysis, energy data, and applied analytics
