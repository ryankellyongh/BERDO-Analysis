#!/usr/bin/env python
# coding: utf-8

# # BERDO Compliance Analysis
# 
# **Identifying High-Impact Energy Reduction Opportunities in Boston Buildings**
# 
# **Executive Summary**
# 
# 
# This report analyzes Boston’s 2025 BERDO building dataset to identify where compliance challenges and energy reduction opportunities are most concentrated. The analysis finds that BERDO compliance is shaped by two distinct challenges: reporting failure and operational performance.
# The strongest finding is that missing property type data is not randomly distributed. Buildings with missing classification are heavily concentrated in noncompliant reporting categories, indicating that missing data functions as a structural signal of compliance risk rather than a simple data quality issue.
# 
# A second finding is that high Site Energy Use Intensity is concentrated in buildings with greater operational complexity, including manufacturing, laboratory, and other specialized uses. These buildings may be in compliance administratively while still facing significant long-term retrofit difficulty.
# 
# These findings suggest that BERDO implementation should not rely on a single intervention strategy. Buildings with missing reporting data require outreach, technical assistance, and ownership coordination support, while high-EUI buildings require deeper retrofit planning, financing pathways, and engineering support.
# 
# 
# ## Tools Used
# - Python  
# - pandas  
# - matplotlib
# - Excel
# 
# 
# 
# 
# ## Introduction
# 
# Boston’s Building Emissions Reduction and Disclosure Ordinance (BERDO) requires large buildings to report emissions and reduce operational carbon over time. This project analyzes 2025 BERDO-reported building energy and water metrics to identify which buildings may face the greatest compliance challenges and where targeted intervention could create the highest impact.
# 
# Using Python and pandas, I evaluated compliance status, Site Energy Use Intensity (EUI), property type complexity, ownership patterns, and reporting gaps across Boston’s building stock. The analysis focused on identifying buildings that combine high emissions pressure with high implementation difficulty, especially multifamily and mixed-use properties that often lack institutional capital planning capacity.
# 
# The results show that buildings with missing property type information are strongly concentrated in noncompliant reporting categories, creating a clear link between data completeness and compliance risk. In addition, higher-EUI buildings tend to appear more frequently in more complex compliance pathways, suggesting that operational intensity and implementation difficulty are closely connected.
# 
# This project reframes missing data as a strategic signal rather than simply a limitation and supports more targeted policy recommendations for BERDO compliance, retrofit planning, and equitable decarbonization.
# 
# 
# ## Project Objestive
# 
# This project analyzes BERDO compliance data for Boston buildings to evaluate how energy performance, ownership structure, and building characteristics relate to compliance outcomes.
# 
# The goal is to identify where emissions reduction efforts can create the greatest practical impact by distinguishing between buildings that need reporting support and buildings that require deeper retrofit intervention.
# 
# Rather than treating all buildings equally, this analysis prioritizes buildings based on energy intensity, operational complexity, and likelihood of compliance barriers.
# 
# 
# ## Key Insight
# 
# **Missing Data as a Signal of Compliance Gaps**
# 
# After standardizing compliance labels, 1,672 buildings fall into the “Not Submitted” category. Buildings with missing property type are overwhelmingly concentrated within this group, showing that incomplete reporting and missing classification data occur together rather than independently.
# 
# ## Interpretation
# 
# Missing property type is not simply a data quality issue. It is a measurable indicator of compliance risk.
# 
# Buildings that fail to submit required BERDO reporting are also the same buildings missing core classification fields, suggesting that incomplete reporting and missing data occur together rather than independently.
# 
# This indicates that data gaps are concentrated in specific compliance pathways rather than occurring randomly across the dataset.
# 
# ## Stakeholder Alignment
# 
# This pattern aligns with stakeholder interviews conducted during the Massachusetts Building Congress clean energy policy internship.
# 
# Common barriers included:
# • difficulty identifying responsible building owners
# • limited technical capacity among smaller and fragmented ownership groups
# • complex and time-intensive reporting processes
# • limited access to engineering expertise and retrofit planning support
# 
# These factors help explain why some buildings submit incomplete data or fail to report entirely.
# 
# ## Why This Matters
# 
# This finding reframes missing data from a limitation into a diagnostic tool.
# Missing property type can serve as an early warning signal for buildings at greater risk of noncompliance.
# 
# This creates an opportunity to:
# • target outreach and technical assistance more effectively
# • prioritize buildings with the highest likelihood of reporting gaps
# • improve compliance through proactive intervention rather than reactive enforcement
# 
# ## Final Takeaway
# 
# Data completeness and compliance are deeply connected.
# In this dataset, missing information is not noise, it is a clear and measurable signal of where the system is breaking down.
# 
# There are two different intervention groups:
# 
# **Group 1: Not Submitted → needs outreach + reporting support**
# 
# **Group 2: High EUI → needs retrofit + energy reduction**
# 
# ### Methodology
# 
# #### Data Preparation
# 
# The analysis uses the 2025 BERDO-reported Energy and Water Metrics dataset for Boston buildings.
# 
# Data was imported and cleaned using Python and pandas to improve consistency and analytical usability. Key preprocessing steps included:
# 
# • standardizing column names for easier querying and analysis
# • renaming major variables such as property type, Site EUI, emissions, and compliance status for clarity
# • removing records with missing Site EUI values when energy performance comparisons required valid observations
# • preserving the full dataset separately for reporting gap and missing data analysis
# 
# This allowed the project to distinguish between operational performance analysis and reporting completeness analysis.
# 
# 
# #### Core Variables
# 
# The analysis focused on variables most directly connected to BERDO compliance and emissions performance:
# 
# • property type
# • Site Energy Use Intensity (Site EUI)
# • total site energy usage
# • greenhouse gas emissions
# • compliance status
# • building size (gross floor area)
# • ownership patterns inferred from owner name classification
# 
# These variables were selected to evaluate both energy performance and implementation difficulty.
# 
# ## Analytical Framework
# 
# The project combines descriptive analysis, comparative metrics, and rule-based prioritization to identify high-impact intervention groups.
# 
# Key methods included:
# • compliance distribution analysis across the full dataset
# • property type and ownership gap analysis for missing records
# • grouped comparison of average Site EUI across compliance categories
# • correlation analysis between building size and energy intensity
# • complexity classification based on likely retrofit and ownership challenges
# • priority segmentation using both energy intensity and implementation complexity
# 
# This framework supports a more practical interpretation of BERDO compliance by connecting emissions performance to real implementation barriers.

# ## Libraries

# In[22]:


#Load libraries
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

file_path = Path.home() / "Documents" / "BERDO Analysis" / "2025-reported-energy-and-water-metrics.xlsx"

#Check if the file exists
if not os.path.exists(file_path):
    raise FileNotFoundError("Dataset not found. Please check the file path.")


# ## Column Cleaning

# In[25]:


#Clean column names
def load_dataset(filepath: Path) -> pd.DataFrame:
    """
    Load BERDO dataset with error handling.
    
    Parameters:
    -----------
    file_path : Path
        Path to the Excel file
        
    Returns:
    --------
    pd.DataFrame
        Loaded dataset
        
    Raises:
    -------
    FileNotFoundError
        If file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {file_path}. Please check the file path."
        )
    
    try:
        #**Fixed: header=1 skips the first row**
        df = pd.read_excel(file_path, header = 0)
        print(f"✓ Dataset loaded successfully: {df.shape[0]:,} rows, {df.shape[1]} columns")
        return df
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")


# In[29]:


#Initial Data Inspection

#Create df before using it
df = load_dataset(file_path)

#Clean column names before renaming them
df.columns = (
    df.columns.str.strip()
    .str.replace("\n", " ", regex=False)
)

#Get dataset dimensions
rows, columns = df.shape

#Dataset overview table
initial_table = pd.DataFrame({
    "Dataset Metric": [
        "Total Records",
        "Total Variables",
        "Missing Values Present"
    ],
    "Result": [
        f"{rows:,}",
        columns,
        "Yes" if df.isnull().sum().sum() > 0 else "No"
    ]
})

display(
    initial_table.style
    .hide(axis="index")
    .set_caption("Dataset Overview")
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)

#Preview first 5 rows
display(
    df.head().style
    .hide(axis="index")
    .set_caption("Preview of Raw BERDO Dataset")
    .set_properties(**{
        "text-align": "center",
        "padding": "10px",
        "font-size": "13px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)

#Column reference table
column_reference = pd.DataFrame({
    "Column Number": range(1, len(df.columns) + 1),
    "Original Column Name": df.columns.tolist()
})

display(
    column_reference.style
    .hide(axis="index")
    .set_caption("Column Name Reference Guide")
    .set_properties(**{
        "text-align": "left",
        "padding": "10px",
        "font-size": "13px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# ## Rename columns

# In[32]:


#Rename Columns and Data Cleaning

#Rename important columns for easier analysis
df = df.rename(columns={
    "Largest Property Type": "property_type",
    "Reported Gross Floor Area_(sq_ft)": "gross_floor_area",
    "Site EUI (Energy Use Intensity kBtu/ft²)": "site_eui",
    "Total Site Energy Usage_(kBtu)": "total_site_energy",
    "Estimated Total GHG Emissions_(kgCO2e)": "ghg_emissions",
    "Natural Gas Usage (kBtu)": "natural_gas_usage",
    "Electricity Usage_(kWh)": "electricity_usage",
    "Reporting Compliance Status": "compliance_status",
    "First Emissions Compliance Year (Projected)": "compliance_year"
})

#Create the full dataset before filtering
df_full = df.copy()

#Filter dataset for valid Site EUI values only
initial_row_count = df_full.shape[0]
df_clean = df_full.dropna(subset=["site_eui"]).copy()
final_row_count = df_clean.shape[0]

#Calculate removed records
rows_removed = initial_row_count - final_row_count
missing_pct = (rows_removed / initial_row_count) * 100

#Create data quality summary table
quality_summary = pd.DataFrame({
    "Data Quality Metric": [
        "Initial Records",
        "Records with Valid Site EUI",
        "Records Removed",
        "Percent Removed"
    ],
    "Result": [
        f"{initial_row_count:,}",
        f"{final_row_count:,}",
        f"{rows_removed:,}",
        f"{missing_pct:.1f}%"
    ]
})

display(
    quality_summary.style
    .hide(axis="index")
    .set_caption("Data Quality Summary")
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)

#Preview cleaned dataset
display(
    df_clean[[
        "property_type",
        "site_eui",
        "compliance_status"
    ]].head().style
    .hide(axis="index")
    .set_caption("Preview of Cleaned Analysis Dataset")
    .set_properties(**{
        "text-align": "center",
        "padding": "10px",
        "font-size": "13px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# ### Observation
# 
# After cleaning the dataset, the total number of records decreased from 5,580 buildings to 3,678 buildings with valid Site EUI values, meaning 1,902 records (34.1%) were removed due to missing energy intensity data.
# 
# This is important because Site EUI serves as one of the strongest indicators of operational energy performance and potential emissions reduction opportunity. Removing records with missing Site EUI improves the reliability of energy performance comparisons by ensuring that grouped analysis is based only on valid observations.
# 
# At the same time, preserving the full dataset separately allows reporting gaps and missing-data patterns to be analyzed independently, preventing compliance failures from being hidden during cleaning. This distinction strengthens the overall analysis by separating operational performance problems from reporting completeness problems.

# ## Analysis

# ## Features Used
# The analysis focuses on variables directly related to compliance and energy performance:
# - Property type
# - Site Energy Use Intensity (EUI)
# - Total energy usage
# - Greenhouse gas (GHG) emissions
# - Compliance status

# In[34]:


#Compliance Distribution

#Create compliance distribution table
compliance_table = (
    df_full["compliance_status"]
    .replace(r"^\s*$", pd.NA, regex=True)
    .fillna("Not Submitted")
    .value_counts(dropna=False)
    .rename_axis("Compliance Status")
    .reset_index(name="Building Count")
)

#Calculate percentage distribution
compliance_table["Percent of Buildings"] = (
    compliance_table["Building Count"] /
    compliance_table["Building Count"].sum()
)

#Display styled table
display(
    compliance_table.style
    .hide(axis="index")
    .set_caption("BERDO Compliance Distribution (2025)")
    .format({
        "Building Count": "{:,}",
        "Percent of Buildings": "{:.1%}"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# ### Observation
# 
# The dataset is heavily concentrated in the in compliance category, with 3,569 buildings (64.0%) meeting BERDO reporting requirements. After standardizing duplicated labels such as “not submitted” and “Not Submitted,” a total of 1,672 buildings fall into the non-submitted category, representing a significant portion of Boston’s building stock. Smaller groups include pending revisions (223 buildings, 4.0%) and state pathway compliance (116 buildings, 2.1%).
# 
# This distribution shows that while most buildings successfully meet reporting requirements, a substantial group still faces reporting and compliance barriers. These challenges are often concentrated in buildings with fragmented ownership structures, limited technical capacity, or weaker access to engineering and reporting support, particularly among smaller condominium associations, LLC-managed properties, and under-resourced ownership groups.
# 
# Rather than representing isolated exceptions, these noncompliant buildings may represent the highest-impact intervention group because they combine both reporting failure and likely future retrofit difficulty. This supports the need for targeted outreach, technical assistance, and proactive compliance support rather than relying only on reactive enforcement.

# In[39]:


#Property Type Reporting Gaps

#Count all buildings by property type
total_counts = (
    df_full["property_type"]
    .fillna("No Property Type")
    .value_counts()
)

#Identify buildings missing Site EUI
no_energy = df_full[df_full["site_eui"].isna()]

#Count missing Site EUI records by property type
ns_counts = (
    no_energy["property_type"]
    .fillna("No Property Type")
    .value_counts()
)

#Combine counts into one table
full_table = pd.DataFrame({
    "Total Buildings": total_counts,
    "Not Submitted": ns_counts
}).fillna(0)

#Convert to integer
full_table["Not Submitted"] = full_table["Not Submitted"].astype(int)

#Calculate percent not submitted
full_table["Percent Not Submitted"] = (
    full_table["Not Submitted"] / full_table["Total Buildings"] * 100
).round(1)

#Keep top 10 property types by total building count
top10 = full_table.sort_values("Total Buildings", ascending=False).head(10)

#Group remaining property types into Other
other_counts = full_table.drop(top10.index)[["Total Buildings", "Not Submitted"]].sum()

other_percent = (
    other_counts["Not Submitted"] / other_counts["Total Buildings"] * 100
    if other_counts["Total Buildings"] > 0 else 0
)

other_row = pd.Series({
    "Total Buildings": other_counts["Total Buildings"],
    "Not Submitted": other_counts["Not Submitted"],
    "Percent Not Submitted": round(other_percent, 1)
})

#Create final table
property_table = pd.concat([top10, pd.DataFrame(other_row).T])
property_table.index = list(top10.index) + ["Other"]

property_table = (
    property_table
    .reset_index()
    .rename(columns={"index": "Property Type"})
)

#Display styled table
display(
    property_table.style
    .hide(axis="index")
    .set_caption("Property Types with Highest Reporting Gaps")
    .format({
        "Total Buildings": "{:,}",
        "Not Submitted": "{:,}",
        "Percent Not Submitted": "{:.1f}%"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# In[91]:


#Property Type Reporting Gaps Visualization

#Create normalized values for color intensity
values = property_table["Percent Not Submitted"]
normalized = values / values.max()

#Use Reds colormap for reporting risk intensity
colors = plt.cm.Reds(normalized)

#Create bar chart
plt.figure(figsize=(12, 6))

plt.bar(
    property_table["Property Type"],
    property_table["Percent Not Submitted"],
    color=colors
)

plt.title(
    "Property Types with Highest Reporting Risk",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel(
    "Property Type",
    fontsize=12
)

plt.ylabel(
    "Percent Not Submitted (%)",
    fontsize=12
)

plt.xticks(
    rotation=45,
    ha="right"
)

#Add percentage labels above bars
for i, value in enumerate(property_table["Percent Not Submitted"]):
    plt.text(
        i,
        value + 0.8,
        f"{value:.1f}%",
        ha="center",
        fontsize=10
    )

plt.tight_layout()
plt.show()


# **Observation**
# 
# Buildings with missing property type are highly concentrated in noncompliant reporting categories. The No Property Type category contains 1,653 total buildings, with 1,652 classified as not submitted, resulting in a 99.9% non-submission rate. By comparison, Multifamily Housing, despite being the largest building category with 2,104 buildings, shows only 52 not submitted cases (2.5%).
# 
# 
# This creates a near-perfect relationship between missing property classification and compliance failure. Missing property type is therefore not simply a data quality issue, but a strong indicator of operational and reporting barriers.
# 
# 
# This suggests that buildings missing core classification fields are often the same buildings struggling to complete BERDO reporting requirements, making missing data a practical early warning signal for compliance risk.

# In[81]:


#Buildings Missing Property Type

#Filter buildings with missing property type
missing_property = df_full[df_full["property_type"].isna()].copy()

#Preview key fields for buildings missing property type
display(
    missing_property[[
        "property_type",
        "Reported Gross Floor Area (Sq Ft)",
        "Building Address",
        "Property Owner Name",
        "site_eui",
        "compliance_status"
    ]]
    .head(20)
    .style
    .hide(axis="index")
    .set_caption("Buildings with Missing Property Type")
    .set_properties(**{
        "text-align": "center",
        "padding": "10px",
        "font-size": "13px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# In[47]:


#Missing EUI by Property Type Availability

#Create indicator for whether property type is missing
df_full["missing_property_type"] = df_full["property_type"].isna()

#Compare missing Site EUI rates by property type availability
result = (
    df_full
    .groupby("missing_property_type")["site_eui"]
    .apply(lambda x: x.isna().mean() * 100)
    .rename("Percent Missing Site EUI")
    .reset_index()
)

#Rename labels for readability
result["missing_property_type"] = result["missing_property_type"].replace({
    False: "Property Type Present",
    True: "Property Type Missing"
})

result = result.rename(columns={
    "missing_property_type": "Property Type Status"
})

#Display formatted table
display(
    result.style
    .hide(axis="index")
    .set_caption("Missing Site EUI by Property Type Availability")
    .format({
        "Percent Missing Site EUI": "{:.1f}%"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# **Observation** 
# 
# Approximately 29.6% of buildings in the dataset lack an assigned property type. Within this group, nearly 100% are also missing energy use data. This indicates that data incompleteness is not randomly distributed, but instead concentrated within a large subset of buildings that are not fully classified. As a result, improving property type classification could significantly increase overall data coverage and reporting completeness.

# Question: What buildings are in the "Other?"

# In[49]:


#Classify Ownership Type for Buildings Missing Property Type

owner_col = "Property Owner Name"

#Fill missing owner names to avoid string errors
owner_series = missing_property[owner_col].fillna("").astype(str)

conditions = [

    #1 Property Name or Address-like
    owner_series.str.contains(
        r"^\d+\s+.*\b(?:STREET|ST|AVENUE|AVE|ROAD|RD|BLVD|LANE|LN|DRIVE|DR|COURT|CT|PLACE|PL)\b",
        case=False, na=False
    ),

    #2 Education
    owner_series.str.contains(
        r"SCHOOL|CHARTER|ACADEMY|COLLEGE|UNIVERSITY|EDUCATION",
        case=False, na=False
    ),

    #3 Public Safety
    owner_series.str.contains(
        r"POLICE|FIRE|EMS|PUBLIC SAFETY|PATROLMEN|DEPARTMENT",
        case=False, na=False
    ),

    #4 Condominium
    owner_series.str.contains(
        r"CONDO|CONDOMINIUM",
        case=False, na=False
    ),

    #5 Public Sector
    owner_series.str.contains(
        r"\bCITY\b|\bMASS\b|\bAUTHORITY\b|\bREDEVELOPMENT\b|\bMBTA\b|PUBLIC HEALTH|\bCOMM\b",
        case=False, na=False
    ),

    #6 Trust
    owner_series.str.contains(
        r"TRUST|TRST|\bTS\b",
        case=False, na=False
    ),

    #7 Association
    owner_series.str.contains(
        r"ASSOC|ASSOCIATION",
        case=False, na=False
    ),

    #8 Nonprofit or Religious
    owner_series.str.contains(
        r"CHURCH|FOUNDATION|SOCIETY|COMMUNITY|DIOCESE|METHODIST|BUDDHIST|CATHOLIC|FRIARS|SISTERS|HOLY|PARISH|ARCH|WORSHIP|WRSHP|TEMPLE|MINISTRY",
        case=False, na=False
    ),

    #9 Partnership
    owner_series.str.contains(
        r"\bLLP\b|\bLP\b|\bLPS\b|\bLIMITED PARTNERSHIP\b|\bPARTNERSHIP\b",
        case=False, na=False
    ),

    #10 LLC
    owner_series.str.contains(
        r"\bLLC\b",
        case=False, na=False
    ),

    #11 Corporate
    owner_series.str.contains(
        r"INC|CORP|COMPANY|HOLDINGS|REALTY|PROPERTIES",
        case=False, na=False
    ),

    #12 Business Venture
    owner_series.str.contains(
        r"\bGROUP\b|\bMGMT\b|\bMANAGEMENT\b|\bVENTURES\b|\bCAPITAL\b",
        case=False, na=False
    ),

    #13 Individual
    owner_series.str.contains(
        r"^[A-Za-z]+(?:\s+[A-Za-z\.]+){1,3}$",
        na=False
    )
]

choices = [
    "Property Name",
    "Education",
    "Public Safety",
    "Condominium",
    "Public Sector",
    "Trust",
    "Association",
    "Nonprofit",
    "Partnership",
    "LLC",
    "Corporate",
    "Business Venture",
    "Individual"
]

missing_property["ownership_type"] = np.select(
    conditions,
    choices,
    default="Other"
)


# In[51]:


#Ownership Type Summary

#Count ownership type classifications
ownership_counts = (
    missing_property["ownership_type"]
    .fillna("Unclassified")
    .value_counts()
)

#Calculate percentage distribution
ownership_percent = (
    missing_property["ownership_type"]
    .fillna("Unclassified")
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

#Create summary table
ownership_summary = pd.DataFrame({
    "Ownership Type": ownership_counts.index,
    "Count": ownership_counts.values,
    "Percent (%)": ownership_percent.values
})

#Display styled table
display(
    ownership_summary.style
    .hide(axis="index")
    .set_caption("Ownership Type Distribution for Buildings Missing Property Type")
    .format({
        "Count": "{:,}",
        "Percent (%)": "{:.2f}%"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# Observation: Missing property type information is concentrated among LLC-owned (23.29%), public sector (18.94%), and condominium (18.39%) buildings, which together account for nearly 60% of cases. These ownership structures often involve shared governance, institutional management, or fragmented legal entities, which may contribute to reporting inconsistencies.
# While expanded classification reduced the unclassified share, 18.27% of buildings remain categorized as “Other,” reflecting limitations in ownership name standardization and highlighting the challenges of relying on free-text fields for structured analysis.

# In[52]:


#Compliance Status by Ownership Type

#Summarize compliance status within each ownership type
compliance_counts = (
    missing_property
    .assign(ownership_type=missing_property["ownership_type"].fillna("Unclassified"))
    .groupby(["ownership_type", "compliance_status"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

#Display styled table
display(
    compliance_counts.style
    .hide(axis="index")
    .set_caption("Compliance Status by Ownership Type for Buildings Missing Property Type")
    .format(precision=0)
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# In[53]:


#Overall Compliance Summary for Buildings Missing Property Type

#Calculate total records across all compliance categories
total = compliance_counts.drop(columns=["ownership_type"]).sum().sum()

#Summarize total counts by compliance category
summary = (
    compliance_counts
    .drop(columns=["ownership_type"])
    .sum(axis=0)
)

#Calculate percentage distribution
percent = (
    summary / total * 100
).round(2)

#Create final summary table
compliance_summary = pd.DataFrame({
    "Compliance Status": summary.index,
    "Count": summary.values,
    "Percent (%)": percent.values
})

#Display styled table
display(
    compliance_summary.style
    .hide(axis="index")
    .set_caption("Overall Compliance Summary for Buildings Missing Property Type")
    .format({
        "Count": "{:,}",
        "Percent (%)": "{:.2f}%"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# None of the buildings with missing property type are classified as “In Compliance.”
# Instead, the majority fall under “Not Submitted,” with smaller portions in “Pending Revisions” and the “State” pathway.
# This suggests that missing property classification is strongly associated with reporting gaps and potential non-compliance, highlighting a key data quality and enforcement issue.

# In[54]:


#Property Type Distribution Comparison

#Overall dataset distribution
overall_percent = (
    df_clean["property_type"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

#Missing-property subset ownership distribution
missing_percent = (
    missing_property["ownership_type"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

#Create side-by-side comparison table
comparison = pd.concat(
    [overall_percent, missing_percent],
    axis=1
)

comparison.columns = [
    "All Buildings (%)",
    "Missing Property Type (%)"
]

comparison = (
    comparison
    .fillna(0)
    .reset_index()
    .rename(columns={"index": "Category"})
)

#Display styled table
display(
    comparison.style
    .hide(axis="index")
    .set_caption("Comparison of Overall Property Types vs Missing Property Type Ownership Patterns")
    .format({
        "All Buildings (%)": "{:.2f}%",
        "Missing Property Type (%)": "{:.2f}%"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# In[60]:


#Ownership Type Distribution Visualization

#Calculate ownership type percentage distribution
ownership_counts = (
    missing_property["ownership_type"]
    .fillna("Unclassified")
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

#Create intensity-based colors using normalized values
values = ownership_counts.values
normalized = values / values.max()

#Use matplotlib Blues colormap for intensity shading
colors = plt.cm.Blues(normalized)

#Create bar chart
plt.figure(figsize=(12, 6))

plt.bar(
    ownership_counts.index,
    ownership_counts.values,
    color=colors
)

plt.title(
    "Ownership Type Distribution for Buildings Missing Property Type",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel(
    "Ownership Type",
    fontsize=12
)

plt.ylabel(
    "Percent of Buildings (%)",
    fontsize=12
)

plt.xticks(
    rotation=45,
    ha="right"
)

#Add percentage labels above bars
for i, value in enumerate(ownership_counts.values):
    plt.text(
        i,
        value + 0.2,
        f"{value:.1f}%",
        ha="center",
        fontsize=10
    )

plt.tight_layout()
plt.show()


# ### Observation
# 
# While large property types such as multifamily housing and office buildings make up the majority of the building stock and show relatively strong reporting rates, the overall data gap is driven primarily by the “Other” category, which accounts for over 40% of buildings and exhibits a disproportionately high rate of missing energy data. This suggests that BERDO compliance challenges are concentrated among smaller, more heterogeneous, and less standardized building types, highlighting the need for targeted outreach and support strategies beyond major building sectors.
# 

# ## Average EUI by Compliance

# Research Question: Among buildings that did report energy data, do performance patterns differ by compliance status?

# In[65]:


#Energy Performance by Compliance Status

#Create cleaned dataset using only buildings with valid Site EUI
df_clean = (
    df_full
    .dropna(subset=["site_eui"])
    .copy()
)

#Calculate average Site EUI by compliance status
eui_by_compliance = (
    df_clean
    .groupby("compliance_status")["site_eui"]
    .mean()
    .rename("Average Site EUI")
    .reset_index()
    .sort_values(
        by="Average Site EUI",
        ascending=False
    )
    .reset_index(drop=True)
)

#Rename column for presentation
eui_by_compliance = eui_by_compliance.rename(columns={
    "compliance_status": "Compliance Status"
})

#Display styled table
display(
    eui_by_compliance.style
    .hide(axis="index")
    .set_caption("Average Site EUI by Compliance Status")
    .format({
        "Average Site EUI": "{:.2f}"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# In[66]:


#Energy Performance by Property Type

#Calculate average Site EUI by property type
eui_by_type = (
    df_clean
    .groupby("property_type")["site_eui"]
    .mean()
    .rename("Average Site EUI")
    .reset_index()
    .sort_values(
        by="Average Site EUI",
        ascending=False
    )
    .reset_index(drop=True)
)

#Rename column for presentation
eui_by_type = eui_by_type.rename(columns={
    "property_type": "Property Type"
})

#Display styled table
display(
    eui_by_type.style
    .hide(axis="index")
    .set_caption("Average Site EUI by Property Type")
    .format({
        "Average Site EUI": "{:.2f}"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# ### Observation
# 
# Energy use intensity varies significantly across building types, with laboratories exhibiting substantially higher energy use than all other categories. Institutional buildings such as colleges and universities also show elevated energy intensity, while more common building types like offices and multifamily housing fall closer to the middle of the distribution. This indicates that building function plays a primary role in determining energy performance, with certain specialized uses driving disproportionately high energy demand.

# In[67]:


#Correlation Analysis: Building Size vs Energy Intensity

#Calculate correlation between building size and Site EUI
corr = (
    df_clean[[
        "Reported Gross Floor Area (Sq Ft)",
        "site_eui"
    ]]
    .corr()
    .round(3)
)

#Display styled correlation matrix
display(
    corr.style
    .set_caption("Correlation Matrix: Gross Floor Area vs Site EUI")
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# In[68]:


#Average Site EUI by Property Type and Compliance Status

import matplotlib.pyplot as plt

#Remove rows with missing values needed for comparison
df_plot = (
    df_clean
    .dropna(subset=[
        "property_type",
        "compliance_status",
        "site_eui"
    ])
    .copy()
)

#Focus on the top 5 most common property types
top_types = (
    df_plot["property_type"]
    .value_counts()
    .head(5)
    .index
)

df_plot = (
    df_plot[
        df_plot["property_type"].isin(top_types)
    ]
)

#Calculate average Site EUI by property type and compliance status
grouped = (
    df_plot
    .groupby([
        "property_type",
        "compliance_status"
    ])["site_eui"]
    .mean()
    .reset_index()
)

#Create pivot table for grouped bar chart
pivot = grouped.pivot(
    index="property_type",
    columns="compliance_status",
    values="site_eui"
)

#Keep only rows with complete comparisons
pivot = pivot.dropna()

#Sort by highest average EUI using first compliance column
pivot = pivot.sort_values(
    by=pivot.columns[0],
    ascending=False
)

#Create grouped bar chart
ax = pivot.plot(
    kind="bar",
    figsize=(12, 7)
)

plt.title(
    "Average Site EUI by Property Type and Compliance Status",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel(
    "Property Type",
    fontsize=12
)

plt.ylabel(
    "Average Site EUI (kBtu/ft²)",
    fontsize=12
)

plt.xticks(
    rotation=30,
    ha="right"
)

plt.legend(
    title="Compliance Status",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.tight_layout()
plt.show()


# In[70]:


#Property Type Complexity Classification

#Classify property types into BERDO compliance complexity groups
def classify_complexity(property_type):
    if pd.isna(property_type):
        return "Unknown"

    property_type = property_type.lower()

    #High complexity:
    #Often multifamily or mixed-use buildings with split ownership,
    #limited capital planning, and more difficult retrofit coordination
    if any(x in property_type for x in [
        "multifamily",
        "residential",
        "mixed"
    ]):
        return "High Complexity"

    #Moderate complexity:
    #Common commercial buildings with clearer ownership structure
    #but still meaningful retrofit and compliance challenges
    if any(x in property_type for x in [
        "office",
        "retail",
        "hotel"
    ]):
        return "Moderate Complexity"

    #Low complexity:
    #Large institutional buildings often have stronger capital access,
    #dedicated facilities teams, and structured energy management
    if any(x in property_type for x in [
        "university",
        "hospital",
        "laboratory"
    ]):
        return "Low Complexity"

    #Default classification
    return "Moderate Complexity"

#Apply classification
df_clean["complexity"] = (
    df_clean["property_type"]
    .apply(classify_complexity)
)


# In[71]:


#Energy Intensity Classification

#Use median Site EUI as threshold for classification
eui_threshold = df_clean["site_eui"].median()

#Classify buildings into High EUI vs Low EUI
df_clean["eui_category"] = (
    df_clean["site_eui"]
    .apply(
        lambda x:
        "High EUI" if x > eui_threshold
        else "Low EUI"
    )
)

#Display threshold value
threshold_table = pd.DataFrame({
    "Metric": ["Median Site EUI Threshold"],
    "Value": [round(eui_threshold, 2)]
})

display(
    threshold_table.style
    .hide(axis="index")
    .set_caption("Site EUI Classification Threshold")
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# In[72]:


#Building Segmentation by Energy Intensity and Complexity

#Create combined building segment using
#energy intensity category and property complexity

df_clean["segment"] = (
    df_clean["eui_category"]
    + " + "
    + df_clean["complexity"]
)

#Preview segment distribution
segment_preview = (
    df_clean["segment"]
    .value_counts()
    .reset_index()
)

segment_preview.columns = [
    "Building Segment",
    "Count"
]

display(
    segment_preview.style
    .hide(axis="index")
    .set_caption("Building Segment Distribution")
    .format({
        "Count": "{:,}"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# In[73]:


#Numerical Complexity Scoring

#Convert complexity categories into numeric scores
#for comparison and correlation analysis

df_clean["complexity_num"] = (
    df_clean["complexity"]
    .map({
        "Low Complexity": 1,
        "Moderate Complexity": 2,
        "High Complexity": 3
    })
)

#Preview complexity score distribution
complexity_score_summary = (
    df_clean[[
        "complexity",
        "complexity_num"
    ]]
    .drop_duplicates()
    .sort_values("complexity_num")
    .reset_index(drop=True)
)

complexity_score_summary.columns = [
    "Complexity Category",
    "Complexity Score"
]

display(
    complexity_score_summary.style
    .hide(axis="index")
    .set_caption("Complexity Category Scoring System")
    .format({
        "Complexity Score": "{:.0f}"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# In[74]:


#Priority Matrix

#Check that required columns exist
print(df_clean[["site_eui", "complexity"]].head())

#Create priority column
conditions = [
    (df_clean["site_eui"] >= eui_threshold) & (df_clean["complexity"] == "High Complexity"),
    (df_clean["site_eui"] >= eui_threshold) & (df_clean["complexity"] == "Moderate Complexity"),
    (df_clean["site_eui"] < eui_threshold) & (df_clean["complexity"] == "Low Complexity")
]

choices = [
    "High Priority",
    "Medium Priority",
    "Low Priority"
]

df_clean["priority"] = np.select(
    conditions,
    choices,
    default="Medium Priority"
)

#Numeric mapping for plotting
complexity_map = {
    "Low Complexity": 1,
    "Moderate Complexity": 2,
    "High Complexity": 3
}

#Color mapping
color_map = {
    "High Priority": "red",
    "Medium Priority": "orange",
    "Low Priority": "green"
}

#Create scatter plot
plt.figure(figsize=(10, 6))

for level in ["Low Priority", "Medium Priority", "High Priority"]:
    subset = df_clean[df_clean["priority"] == level]

    plt.scatter(
        subset["site_eui"],
        subset["complexity"].map(complexity_map),
        label=level,
        color=color_map[level],
        alpha=0.6
    )

#Add EUI threshold line
plt.axvline(
    eui_threshold,
    linestyle="--",
    color="black",
    label=f"Median EUI Threshold = {eui_threshold:.2f}"
)

#Axis labels and title
plt.yticks(
    [1, 2, 3],
    ["Low Complexity", "Moderate Complexity", "High Complexity"]
)

plt.xlabel("Site EUI", fontsize=12)
plt.ylabel("Complexity", fontsize=12)
plt.title("Priority Matrix for BERDO Building Segments", fontsize=14, fontweight="bold")
plt.legend()
plt.tight_layout()
plt.show()


# **Observation**
# 
# The average Site EUI across the dataset is substantially lower than the highest-performing outliers, making buildings above 150 strong candidates for priority review. Buildings above 300 represent extreme operational intensity, while values above 500 are likely driven by specialized industrial use or potential reporting anomalies. This supports using tiered thresholds rather than a single fixed cutoff when identifying BERDO compliance priorities.

# In[76]:


#High Priority Building Summary

#Count buildings classified as High Priority
high_priority_count = (
    df_clean[
        (df_clean["site_eui"] > eui_threshold) &
        (df_clean["complexity"] == "High Complexity")
    ]
    .shape[0]
)

#Total number of buildings in cleaned dataset
total_buildings = df_clean.shape[0]

#Calculate percentage of total dataset
percent = round(
    high_priority_count / total_buildings * 100,
    2
)

#Create summary table
priority_summary = pd.DataFrame({
    "Metric": [
        "High Priority Buildings",
        "Total Buildings Analyzed",
        "Percent of Dataset"
    ],
    "Value": [
        f"{high_priority_count:,}",
        f"{total_buildings:,}",
        f"{percent:.2f}%"
    ]
})

display(
    priority_summary.style
    .hide(axis="index")
    .set_caption("High Priority Building Summary")
)


# In[77]:


#Compliance Status of High Priority Buildings

#Filter high priority buildings
high_priority_buildings = (
    df_clean[
        (df_clean["site_eui"] > eui_threshold) &
        (df_clean["complexity"] == "High Complexity")
    ]
    .copy()
)

#Count compliance status distribution
high_priority_compliance = (
    high_priority_buildings["compliance_status"]
    .value_counts()
    .reset_index()
)

high_priority_compliance.columns = [
    "Compliance Status",
    "Building Count"
]

#Calculate percentage distribution
high_priority_compliance["Percent (%)"] = (
    high_priority_compliance["Building Count"] /
    high_priority_compliance["Building Count"].sum() * 100
).round(2)

#Display styled table
display(
    high_priority_compliance.style
    .hide(axis="index")
    .set_caption("Compliance Status Distribution of High Priority Buildings")
    .format({
        "Building Count": "{:,}",
        "Percent (%)": "{:.2f}%"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "12px",
        "font-size": "14px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# In[90]:


#Outlier Buildings with Very High Energy Use

#Identify buildings with extremely high Site EUI
#Threshold used: Site EUI > 200

outliers_table = (
    df_clean[
        df_clean["site_eui"] > 200
    ][[
        "Building Address",
        "property_type",
        "Reported Gross Floor Area (Sq Ft)",
        "site_eui",
        "compliance_status"
    ]]
    .sort_values(
        by="site_eui",
        ascending=False
    )
    .reset_index(drop=True)
)

#Rename columns for cleaner presentation
outliers_table = (
    outliers_table.rename(columns={
        "Building Address": "Address",
        "property_type": "Property Type",
        "Reported Gross Floor Area (Sq Ft)": "Gross Floor Area",
        "site_eui": "Site EUI",
        "compliance_status": "Compliance Status"
    })
)

#Display top 20 highest EUI buildings
display(
    outliers_table
    .head(20)
    .style
    .hide(axis="index")
    .set_caption("High-Priority Buildings Requiring Further Review")
    .format({
        "Gross Floor Area": "{:,.0f}",
        "Site EUI": "{:.2f}"
    })
    .set_properties(**{
        "text-align": "center",
        "padding": "10px",
        "font-size": "13px",
        "border": "1px solid #DADADA"
    })
    .set_table_styles([
        {
            "selector": "caption",
            "props": [
                ("caption-side", "top"),
                ("font-size", "18px"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]
        },
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("font-weight", "bold"),
                ("padding", "10px"),
                ("border", "1px solid #DADADA")
            ]
        }
    ])
)


# Most of the highest EUI buildings exhibit extremely high energy use intensity (EUI > 200), yet are still classified as “In Compliance,” indicating that compliance status is not solely determined by energy intensity. Notably, some of these outliers are relatively small buildings, suggesting potential data anomalies or atypical usage patterns. 
# 
# The presence of high-energy outliers within the “Other” category reinforces the complexity and heterogeneity of this group, which may obscure important variations in building performance.

# ## Conclusion
# 
# This analysis reveals that BERDO compliance is shaped by two distinct but connected challenges: reporting failure and building performance.
# 
# The first challenge is data completeness. A significant portion of buildings fail to submit required information entirely, and this is strongly associated with missing property classification. Buildings without an assigned property type are not randomly distributed across the dataset—they are overwhelmingly concentrated in noncompliant reporting categories, particularly “Not Submitted.” This shows that missing data is not simply a technical issue, but a structural indicator of compliance risk. These gaps are most commonly linked to fragmented ownership structures such as condominiums, LLCs, and certain public or institutional properties, where coordination, accountability, and access to technical support are often more difficult.
# 
# The second challenge is operational performance. Among buildings that do report, Site Energy Use Intensity (EUI) varies significantly across property types, with laboratories, institutional buildings, and other high-demand facilities showing the highest energy intensity. These buildings face a different type of compliance pressure—not reporting failure, but deeper retrofit complexity. High EUI often reflects aging systems, capital constraints, and the need for engineering-intensive decarbonization strategies rather than simple administrative corrections.
# 
# This creates two separate intervention groups. The first group includes buildings that need outreach, reporting assistance, and ownership coordination support. The second includes buildings that require long-term retrofit planning, financing pathways, and technical decarbonization strategies. Treating both groups the same would overlook the very different barriers they face.
# 
# The most important finding is that compliance outcomes and data availability are not evenly distributed across Boston’s building stock. Larger and more standardized building types, such as multifamily housing and office buildings, generally show stronger reporting consistency, while the broad “Other” category and buildings with missing classifications contribute disproportionately to reporting gaps and reduced policy visibility.
# 
# Achieving meaningful emissions reductions under BERDO will require more than targeting high-energy buildings alone. It will require improving data completeness, reducing reporting friction, and supporting under-resourced ownership groups that struggle to engage with compliance systems. Expanding technical assistance, simplifying reporting pathways, and using missing data as an early warning signal can help shift BERDO from reactive enforcement toward proactive intervention.
# 
# These findings suggest that achieving meaningful emissions reductions under BERDO will require more than targeting high-energy buildings. Improving data completeness and supporting under-resourced ownership groups will be critical to ensuring equitable and effective policy implementation. This includes expanding technical assistance, simplifying reporting processes, and developing targeted outreach strategies for buildings that currently fall outside standard compliance pathways.
# 
# The primary barrier to effective climate policy implementation in this context is not only energy performance, but data visibility and ownership structure, which shape how buildings engage with and comply with BERDO requirements.

# ## What I Learned
# 
# The concentration of missing property type data among “Not Submitted” buildings is not random, but reflects deeper structural barriers to BERDO compliance. Through both quantitative analysis and stakeholder interviews, it became clear that missing data often signals broader ownership and coordination challenges rather than simple reporting mistakes.
# 
# Smaller and more fragmented ownership groups, particularly condominiums, LLC-managed properties, and certain public or institutional buildings, often face difficulty identifying who is responsible for compliance, securing access to engineering expertise, and managing the time-intensive reporting process. Many lack dedicated facilities staff, long-term capital planning systems, or clear decision-making structures, which makes both reporting and retrofit planning significantly more difficult.
# This helped shift my understanding of compliance from a purely technical issue to an operational and organizational one. Buildings that fail to report are often the same buildings lacking the internal capacity to engage with BERDO requirements in the first place.
# 
# As a result, missing property type data should not be treated simply as a limitation in the dataset. It functions as a measurable indicator of compliance risk and highlights where policy support, technical assistance, and targeted outreach are most needed. This reinforced the importance of using data not only to measure outcomes, but also to identify where the system itself is creating barriers to participation.
