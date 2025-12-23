# 🚀 FinMod AI: Intelligent Financial CFO Agent

![Financial Model Audit](https://github.com/Hellinferno/finmod-agent/actions/workflows/financial_audit.yml/badge.svg)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](YOUR_RENDER_URL_HERE)

**A Full-Stack AI Financial Platform that automates valuation, forecasting, and strategic decision-making.**

---

## 💼 What It Does
FinMod AI replaces the Junior Analyst. Instead of static Excel sheets, it uses **Python & AI** to:
1.  **🤖 Think:** An embedded **AI Agent** analyzes runway/burn rate and generates text-based strategic advice (e.g., "Critical: Runway < 3 months").
2.  **🔮 Forecast:** Uses **Holt-Winters Exponential Smoothing** to predict future cash flows with confidence intervals.
3.  **🌍 Benchmark:** Connects to **Yahoo Finance API** to compare your KPIs against real-time S&P 500 data.
4.  **🛡️ Verify:** Automated **CI/CD Pipelines** audit the financial math on every code push to ensure accuracy.

---

## 🛠️ Tech Stack
* **Core:** Python 3.10, Pandas, NumPy Financial.
* **AI/ML:** Scikit-Learn (Regression), Statsmodels (Time-Series).
* **Interface:** Plotly Dash Enterprise, Bootstrap Components.
* **Live Data:** Yahoo Finance API (`yfinance`).
* **DevOps:** Docker, GitHub Actions (CI/CD), Render Cloud.

---

## ⚡ Quick Start
**Want to try it locally?**

1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/Hellinferno/finmod-agent.git
    cd finmod-agent
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App:**
    ```bash
    python src/ui/app.py
    ```
    *Open http://127.0.0.1:8050 in your browser.*

---

## 📸 Key Features
| Feature | Description | Tech Used |
| :--- | :--- | :--- |
| **Virtual CFO** | Rule-based AI that interprets financial health in plain English. | `agent_logic.py` |
| **Live Benchmarking** | Real-time comparison of P/E ratios vs. S&P 500. | `yfinance` API |
| **Valuation Engine** | DCF (Discounted Cash Flow) Calculator with Sensitivity Heatmaps. | `numpy_financial` |
| **Auto-Audit** | GitHub Action that tests math logic on every commit. | `pytest` |

---

## 👨‍💻 Author
**Ravi **
*B.Sc. AI & Data Science | CA Student*
