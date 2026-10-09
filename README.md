# 🌍 Global CO₂ Emissions Dashboard

**Sustainability Analytics | Tableau • Python • CO₂ Trends • Geographic Analysis • Data Storytelling**

An interactive **Tableau** dashboard exploring carbon dioxide emissions around the world — which countries emit the most, how emissions have changed over time, and how they relate to population and economic output.

![Tableau](https://img.shields.io/badge/Tableau-E97627?style=flat-square&logo=tableau&logoColor=white)
![Excel](https://img.shields.io/badge/Excel-217346?style=flat-square&logo=microsoft-excel&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)

## 🌐 Live Report

**[scarface96.github.io/Global-CO2-Emissions-Dashboard](https://scarface96.github.io/Global-CO2-Emissions-Dashboard/)**

The Tableau workbook is still here. The same dataset now also drives a Python analysis that publishes an interactive web report, rebuilt by GitHub Actions on every push. No Tableau licence is needed to view it.

**What the Python analysis adds:**

- **Emissions by source since 1850:** coal is still 40% of the 2021 total
- **Animated world map** of CO₂ per person, 1960–2021, with a year slider and play button
- **Three rankings that disagree:** China leads on annual totals, Gulf producers per person, the United States over all of history
- **Historical responsibility:** the US holds 24% of all CO₂ ever emitted with 4% of the world's people; Africa holds 18% of people but 3% of emissions
- **Decoupling:** 34 of 92 sizeable emitters grew GDP while cutting CO₂ (1990–2018), with indexed GDP vs CO₂ for six countries
- **Last decade's trend** for the 25 largest emitters (log-linear fit)
- **Country explorer:** pick any country to see its emissions by fuel and compare its emissions per person with any other

## Business value

Turn country-level emissions data into geographic comparisons and historical trends. The dashboard supports exploration of absolute emissions alongside population and economic measures.

### Questions this project addresses

- Which countries have the highest annual emissions?
- How have emissions changed over time?
- How do comparisons change when emissions are measured per capita?


## 📋 Overview

Climate data is huge and hard to read in a table. This dashboard turns more than 50,000 rows of emissions data into a single view where you can compare countries and see long-term trends.

## 📈 Visuals

The first image is the dashboard preview stored in the workbook. Charts built with Python (pandas + matplotlib) from the data files in this repo.

<p align="center"><img src="docs/images/tableau_preview.png" alt="Preview of the Tableau dashboard" width="384"></p>
<p align="center"><sub>Dashboard preview saved inside the Tableau workbook (top-left section)</sub></p>

<p align="center"><img src="docs/images/world_trend.png" alt="Global CO2 emissions from 1850 to 2021" width="85%"></p>

<p align="center"><img src="docs/images/top_emitters.png" alt="Top 10 emitting countries in 2021" width="85%"></p>

## 🗂️ Dataset

`visualizing_global_co2_data.csv` — **278 countries and regions**, yearly from **1750 to 2021** (~50,600 rows).

Includes, among other fields:
- `co2` — annual CO₂ emissions
- `co2_per_capita`, `co2_per_gdp` — emissions relative to population and economy
- `co2_growth_abs`, `co2_growth_prct` — year-on-year change
- Emissions by source (e.g. cement, coal, oil, gas)
- `co2_including_luc` — emissions including land-use change
- `population`, `gdp`

Full field definitions are in `visualizing_global_CO2_emissions_data_dictionary.xlsx`.

## 📊 Dashboard Views

The **Global CO2 Emissions** dashboard combines:

| View | Purpose |
|------|---------|
| 🗺️ **Map** | Emissions by country on a world map |
| 📈 **Line Chart** | Emissions over time |
| 🔵 **Scatter Plot** | Relationship between emissions and other measures (e.g. GDP, population) |

## 📁 Repository Contents

```
├── analysis/
│   ├── data.py        # Loading, country vs aggregate split, rankings, shares, decoupling, trends, explorer data
│   ├── report.py      # Turns the analysis into the interactive web page
│   └── build.py       # Charts, map animation, country explorer, site/index.html
├── tests/             # pytest checks (aggregates excluded, fuels add up, rankings, indices, trend maths)
├── .github/workflows/deploy.yml   # Test, build and publish to GitHub Pages
├── Global CO2 Emissions Dashboard.twbx   # Tableau workbook
├── visualizing_global_co2_data.csv
├── visualizing_global_CO2_emissions_data_dictionary.xlsx
└── requirements.txt
```

**Run the Python report locally:**

```bash
pip install -r requirements.txt
python -m pytest
python -m analysis.build    # writes site/index.html
```

## 🚀 How to Use

Download `Global CO2 Emissions Dashboard.twbx` and open it in **Tableau Desktop** or the free **[Tableau Public](https://public.tableau.com/app/discover)** app. The data is packaged inside the workbook, so no extra setup is needed.

## 🛠️ Skills Demonstrated

Geographic (map) visualisation · time-series charts · scatter plots · dashboard design in Tableau · working with large real-world datasets

---

👤 **Tony Mulunda** — [GitHub @Scarface96](https://github.com/Scarface96)

## Interpretation & limitations

The dataset ends in 2021. Country records and regional aggregates must be distinguished to avoid double-counting; missing observations should not be interpreted as zero emissions.

## Explore the analytics portfolio

- [sql_retail_sales_p1](https://github.com/Scarface96/sql_retail_sales_p1)
- [HR-Analysis-Dashboard](https://github.com/Scarface96/HR-Analysis-Dashboard)
- [B2B-Sales-Pipeline-CRM-Dashboard-for-TechSolutions-Inc.](https://github.com/Scarface96/B2B-Sales-Pipeline-CRM-Dashboard-for-TechSolutions-Inc.)
- [Toy-Store-KPI-Report](https://github.com/Scarface96/Toy-Store-KPI-Report)

## About This Project

A Tableau analytics project that transforms historical global CO₂ data into interactive visual insights. It demonstrates dashboard design, geographic analysis, trend exploration and data storytelling for environmental and sustainability-focused decision making.
