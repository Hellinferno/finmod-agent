# Quantitative Valuation Engine & Dashboard
![Financial Model Audit](https://github.com/Hellinferno/finmod-agent/actions/workflows/financial_audit.yml/badge.svg)

## Overview
A Python-based financial modeling tool capable of performing DCF Valuation and Sensitivity Analysis with vector-based performance.

## 🚀 Quick Start
1. **Download Sample Data:** [Click here to download sample.csv](data/sample_data.csv)
2. **Launch App:** Click the [Live Demo](YOUR_RENDER_URL)
3. **Upload:** Go to the "Forecasting" tab and drop the CSV.
4. **See Magic:** Watch the AI generate the fan chart instantly.

## Architecture
This project follows a strict MVC (Model-View-Controller) pattern to ensure scalability and maintainability:
- **Model (`src/models`)**: Defines data structures and strict validation rules using Pydantic.
- **Controller/Core (`src/core`)**: Handles pure business logic and mathematical computations using Numpy for vectorization.
- **View (`src/ui`)**: A Plotly Dash application providing an interactive "Darkly" themed interface for users.

## Key Features
- **Vectorized Numpy calculations**: Optimized math with no loops for high performance.
- **Pydantic Data Validation**: Ensures financial integrity by strictly enforcing constraints (e.g., WACC parameters).
- **Interactive Plotly Sensitivity Heatmaps**: Visualizes how valuation changes with key assumptions.

## How to Run

### Local
```bash
python -m src.ui.app
```
Then access at [http://127.0.0.1:8050](http://127.0.0.1:8050)

### Docker
```bash
docker build -t finmod-agent:v1 .
docker run -p 8050:8050 finmod-agent:v1
```

## Disclaimer
For educational/portfolio purposes only.
