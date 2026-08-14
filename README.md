# RouteWatch

Self-collected flight tracking and delay prediction for India-Europe air travel, from raw API data to a live, deployed app.

![Python](https://img.shields.io/badge/python-3.13-blue) ![Streamlit](https://img.shields.io/badge/streamlit-live-red) ![Status](https://img.shields.io/badge/status-active-brightgreen)

**Live app:** [routewatch.streamlit.app](https://routewatch.streamlit.app)

## Highlights

- Self-collected dataset, built daily from a live flight API, not a downloaded Kaggle file
- Four real data quality bugs found and fixed by cross-checking the source, not trusting it blindly
- Two classification models trained and compared, with class imbalance handled properly
- A live "predict my flight" feature backed by the actual trained model, with an honest disclaimer next to every prediction
- Light and dark themed, mobile responsive, adjustable delay threshold slider

## Demo

![Delay rate by route](docs/screenshots/delay_by_route.png)
![BOM-FRA delay by hour](docs/screenshots/bom_fra_by_hour.png)

## Installation

```bash
git clone https://github.com/khushi1215/RouteWatch.git
cd RouteWatch
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS
pip install -r requirements.txt
```

Add a `.env` file in the project root:
```
AVIATIONSTACK_KEY=your_key_here
```

## Usage

Run the app:
```bash
streamlit run app.py
```

Collect a day of fresh data:
```bash
python collect_data.py
```

Explore the analysis notebook:
```bash
jupyter notebook explore.ipynb
```

## How it works

A daily script pulls live flight status for a set of India-Europe routes and appends it to a growing CSV. A Jupyter notebook cleans the data, investigates data quality, runs the analysis, and trains the model. A Streamlit app reads the same data, shows the findings interactively, and lets anyone get a live delay-risk prediction for a hypothetical flight.

**Tech stack:** Python, pandas, scikit-learn, Plotly, Streamlit, requests, python-dotenv

## Project structure

```
RouteWatch/
├── data/flights_log.csv      # growing dataset, appended to daily
├── docs/screenshots/         # demo images
├── collect_data.py           # daily data collection script
├── app.py                    # live Streamlit app
├── explore.ipynb             # analysis and modeling notebook
├── requirements.txt
├── KNOWLEDGE.md              # full reasoning log, every decision explained
└── .env                      # API key, not committed
```

## Learn more

This README stays short on purpose. For the complete decision-by-decision reasoning behind this project, including every data quality investigation, every "why this and not that," modeling details, deployment troubleshooting, and the full progress log, see [`KNOWLEDGE.md`](./KNOWLEDGE.md).

## Limitations

Portfolio-scale dataset, not production-scale. Small model test set, results are re-evaluated as data grows. The live prediction is a directional estimate based on 4 factors, not a weather-aware forecast. Full detail in KNOWLEDGE.md.
