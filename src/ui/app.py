import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
from src.ui import home_layout
from src.ui.layout import create_layout as create_valuation_layout
from src.ui.budget_layout import create_budget_layout
from src.ui.capital_layout import create_capital_layout
from src.ui.forecast_layout import create_forecast_layout
from src.ui.liquidity_layout import create_liquidity_layout
from src.ui.benchmark_layout import create_benchmark_layout
from src.ui.callbacks import register_callbacks as register_valuation_callbacks
from src.ui.budget_callbacks import register_budget_callbacks
from src.ui.forecast_callbacks import register_forecast_callbacks
from src.ui.liquidity_callbacks import register_liquidity_callbacks
from src.ui.benchmark_callbacks import register_benchmark_callbacks
from src.core.market_data import get_market_benchmark
from src.core.database import init_db, save_scenario, load_scenarios
from dash import State

# Create the database file locally (or connect to cloud)
init_db()


# Initialize App with Bootstrap Theme
from dotenv import load_dotenv
load_dotenv()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
app.title = "FinMod Enterprise Engine"

# ---------------------------------------------------------
# CALLBACK: Fetch Live Market Data
# ---------------------------------------------------------
@app.callback(
    Output("benchmark-data", "children"),
    Input("btn-refresh-market", "n_clicks"),
    prevent_initial_call=True
)
def update_benchmark_card(n_clicks):
    # 1. Fetch live data for the S&P 500 (SPY)
    # You can change 'SPY' to 'AAPL' or 'MSFT' if you want
    data = get_market_benchmark("SPY")
    
    if not data['success']:
        return "⚠️ Error fetching market data. Check internet connection."

    # 2. Extract metrics
    market_pe = data['pe_ratio']
    market_price = data['price']
    
    # 3. (Optional) Define YOUR company's metric for comparison
    # In the future, replace this 15.0 with your actual calculated P/E from your CSV
    my_company_pe = 15.0 
    
    # 4. Generate the Comparison Logic
    if my_company_pe < market_pe:
        comparison = f"✅ Cheaper than Market ({market_pe})"
    else:
        comparison = f"❌ More Expensive than Market ({market_pe})"

    # 5. Return the formatted text
    # Using dcc.Markdown for better formatting if element allows, but element is html.P.
    # Just returning text for now as per instructions, but adding markdown render for safety.
    return f"""
    🇺🇸 **S&P 500 ETF (SPY)**
    Price: ${market_price}
    Market P/E Ratio: {market_pe}
    
    🔍 **Comparison:**
    Your P/E (est. {my_company_pe}) is {comparison}.
    """

# Routing Layout
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ]
)

# Routing Callback
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/valuation':
        return create_valuation_layout()
    elif pathname == '/budget':
        return create_budget_layout()
    # IF pathname is '/' (root) or anything else, show Home Page
    else:
        return home_layout.layout

# Register Callbacks
register_valuation_callbacks(app)
register_budget_callbacks(app)
register_forecast_callbacks(app)
register_liquidity_callbacks(app)
register_benchmark_callbacks(app)

# ---------------------------------------------------------
# CALLBACK: Save Scenario
# ---------------------------------------------------------
@app.callback(
    Output("save-status", "children"),
    Input("btn-save", "n_clicks"),
    State("save-name", "value"),
    State("input-wacc", "value"),        # Corrected ID from layout.py
    State("input-term-growth", "value"),      # Corrected ID from layout.py
    State("input-cashflows", "value"),   # Corrected ID from layout.py
    prevent_initial_call=True
)
def save_to_db(n_clicks, name, wacc, growth, cash_flows):
    if not name:
        return "⚠️ Name required."
    return save_scenario(name, wacc, growth, cash_flows)

# ---------------------------------------------------------
# CALLBACK: Update Dropdown List
# ---------------------------------------------------------
@app.callback(
    Output("load-dropdown", "options"),
    Input("save-status", "children"), # Refresh list whenever we save
    Input("url", "pathname")          # Refresh list when page loads
)
def update_dropdown(save_msg, pathname):
    scenarios = load_scenarios()
    # Create list for dropdown: [{'label': 'Name', 'value': 'ID'}]
    return [{'label': s.name, 'value': s.id} for s in scenarios]

# ---------------------------------------------------------
# CALLBACK: Load Data into Inputs
# ---------------------------------------------------------
@app.callback(
    [Output("input-wacc", "value"),          # Corrected to match layout
     Output("input-term-growth", "value"),   # Corrected to match layout
     Output("input-cashflows", "value")],    # Corrected to match layout
    Input("btn-load", "n_clicks"),
    State("load-dropdown", "value"),
    prevent_initial_call=True
)
def load_from_db(n_clicks, selected_id):
    if not selected_id:
        return dash.no_update

    # Fetch directly (in a real app, optimize this, but this is fine for MVP)
    scenarios = load_scenarios()
    target = next((s for s in scenarios if s.id == selected_id), None)

    if target:
        return target.wacc, target.growth_rate, target.cash_flows
    return dash.no_update

# Expose server for gunicorn
server = app.server

import os

if __name__ == '__main__':
    # Get the PORT from Render (default to 8050 only if running locally)
    port = int(os.environ.get('PORT', 8050))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
