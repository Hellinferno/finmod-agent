from dash import dcc, html
import dash_bootstrap_components as dbc

def create_layout():
    return dbc.Container(
        [
            dbc.Row(
                [
                    # --- Left Column (Sidebar) ---
                    dbc.Col(
                        [
                            html.H2("Valuation Agent", className="mb-4 text-primary"),
                            
                            # Navigation
                            html.Div([
                                dbc.NavLink("Valuation", href="/valuation", active="exact", className="mb-2"),
                                dbc.NavLink("Budgeting", href="/budgeting", active="exact", className="mb-2"),
                            ], className="mb-4"),

                            html.Hr(),
                            
                            # Input Group 1: Assumptions
                            html.H5("Assumptions", className="mt-4 mb-3"),
                            dbc.Label("WACC (%)"),
                            dbc.Input(id='input-wacc', value=0.10, type='number', step=0.001, className="mb-3"),
                            
                            dbc.Label("Terminal Growth (%)"),
                            dbc.Input(id='input-term-growth', value=0.03, type='number', step=0.001, className="mb-3"),
                            
                            # Input Group 2: Financials
                            html.H5("Financials", className="mt-4 mb-3"),
                            dbc.Label("Free Cash Flows (CSV String)"),
                            dbc.Input(id='input-cashflows', value="100,120,140,160,180", type='text', className="mb-4", placeholder="e.g. 1000, 1200, 1450, 1600, 1800"),
                            
                            # Action
                            dbc.Button("Calculate Model", id='btn-calculate', color="primary", className="w-100 mt-3"),
                            
                            # Error Display
                            dbc.Alert(id='error-alert', color="danger", is_open=False, duration=4000, className="mt-3"),
                        ],
                        width=3,
                        className="p-4",
                        style={"height": "100vh", "borderRight": "1px solid #444"}
                    ),
                    
                    # --- Right Column (Dashboard) ---
                    dbc.Col(
                        [
                            # KPI Row
                            dbc.Row(
                                [
                                    dbc.Col(dbc.Card([dbc.CardBody([html.H4("Enterprise Value", className="card-title"), html.H2(id='output-ev', className="text-success")])], className="mb-3"), width=4),
                                    dbc.Col(dbc.Card([dbc.CardBody([html.H4("Equity Value", className="card-title"), html.H2(id='output-equity', className="text-info")])], className="mb-3"), width=4),
                                    dbc.Col(dbc.Card([dbc.CardBody([html.H4("Implied Share Price", className="card-title"), html.H2(id='output-share-price', className="text-warning")])], className="mb-3"), width=4),
                                ],
                                className="mb-4 mt-4"
                            ),
                            
                            # Visuals Row
                            dbc.Row(
                                [
                                    dbc.Col(dcc.Graph(id='waterfall-graph'), width=6),
                                    dbc.Col(dcc.Graph(id='sensitivity-heatmap'), width=6),
                                ]
                            )
                        ],
                        width=9,
                        className="p-4"
                    )
                ]
            )
        ],
        fluid=True
    )
