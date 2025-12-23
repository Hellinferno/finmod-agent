import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

# 1. Import your pages
from src.ui import home_layout
from src.ui.valuation_layout import create_layout as create_valuation_layout
from src.ui.budget_layout import create_budget_layout
from src.ui.navbar import create_navbar

# Import callbacks (CRITICAL for funcationality)
from src.ui.callbacks import register_callbacks as register_valuation_callbacks
from src.ui.budget_callbacks import register_budget_callbacks
from src.ui.forecast_callbacks import register_forecast_callbacks
from src.ui.liquidity_callbacks import register_liquidity_callbacks
from src.ui.benchmark_callbacks import register_benchmark_callbacks
from src.core.database import init_db

# Load env variables
load_dotenv()
init_db()

# 2. Initialize App with Bootstrap Theme (LITERA for Pro Light Theme)
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.LITERA,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap"
    ],
    suppress_callback_exceptions=True
)
app.title = "FinMod Agent | Professional Valuation"
server = app.server

# 3. Define the Global Layout (Navbar + Page Content)
app.layout = html.Div([
    dcc.Location(id='url', refresh=False), # The URL tracker
    create_navbar(),                       # The Menu Bar
    html.Div(id='page-content')            # Where the pages load
])

# 4. The Router Callback
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/valuation':
        return create_valuation_layout()
    elif pathname == '/budget':
        return create_budget_layout()
    elif pathname == '/' or pathname == '/home':
        return home_layout.layout
    else:
        return home_layout.layout

# Register Callbacks
register_valuation_callbacks(app)
register_budget_callbacks(app)
register_forecast_callbacks(app)
register_liquidity_callbacks(app)
register_benchmark_callbacks(app)

# 5. Run Server
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=False, port=port, host='0.0.0.0')
