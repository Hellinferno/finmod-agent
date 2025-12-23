import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
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

# Initialize App with Bootstrap Theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
app.title = "FinMod Enterprise Engine"

# Routing Layout
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ]
)

# Routing Callback
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/budgeting':
        return create_budget_layout()
    elif pathname == '/capital' or pathname == '/capital-budgeting':
        return create_capital_layout()
    elif pathname == '/forecasting' or pathname == '/forecast':
        return create_forecast_layout()
    elif pathname == '/liquidity':
        return create_liquidity_layout()
    elif pathname == '/benchmarking' or pathname == '/benchmark':
        return create_benchmark_layout()
    elif pathname == '/valuation' or pathname == '/':
        return create_valuation_layout()
    else:
        return html.H1("404: Page Not Found", className="text-danger text-center my-5")

# Register Callbacks
register_valuation_callbacks(app)
register_budget_callbacks(app)
register_forecast_callbacks(app)
register_liquidity_callbacks(app)
register_benchmark_callbacks(app)

# Expose server for gunicorn
server = app.server

import os

if __name__ == '__main__':
    # Get the PORT from Render (default to 8050 only if running locally)
    port = int(os.environ.get('PORT', 8050))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
