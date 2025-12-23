from dash import dcc, html
import dash_bootstrap_components as dbc

def create_capital_layout():
    return dbc.Container(
        [
            dbc.Row(
                [
                    # --- Sidebar (Inputs) ---
                    dbc.Col(
                        [
                            html.H2("Capital Budgeting", className="mb-4 text-success"),
                            
                            # Navigation (Standard MPA)
                            html.Div([
                                dbc.NavLink("Valuation", href="/valuation", active="exact", className="mb-2"),
                                dbc.NavLink("Budgeting", href="/budgeting", active="exact", className="mb-2"),
                                dbc.NavLink("Capital Projects", href="/capital", active="exact", className="mb-2"),
                            ], className="mb-4"),
                            
                            html.Hr(),
                            
                            # Project A Inputs
                            html.H5("Project A", className="text-info"),
                            dbc.Label("Initial Investment ($)"),
                            dbc.Input(id='input-a-invest', value=100000, type='number', className="mb-2"),
                            dbc.Label("Cash Flows (CSV)"),
                            dbc.Input(id='input-a-flows', value="30000,40000,50000,60000", type='text', className="mb-2"),
                            dbc.Label("Volatility (Risk)"),
                            dbc.Input(id='input-a-vol', value=0.15, type='number', step=0.01, className="mb-4"),
                            
                            # Project B Inputs
                            html.H5("Project B", className="text-warning"),
                            dbc.Label("Initial Investment ($)"),
                            dbc.Input(id='input-b-invest', value=120000, type='number', className="mb-2"),
                            dbc.Label("Cash Flows (CSV)"),
                            dbc.Input(id='input-b-flows', value="20000,40000,60000,80000", type='text', className="mb-2"),
                            dbc.Label("Volatility (Risk)"),
                            dbc.Input(id='input-b-vol', value=0.25, type='number', step=0.01, className="mb-4"),
                            
                            dbc.Label("Discount Rate (WACC)"),
                            dbc.Input(id='input-wacc-cap', value=0.10, type='number', step=0.01, className="mb-4"),
                            
                            dbc.Button("Compare Projects", id='btn-compare', color="success", className="w-100"),
                        ],
                        width=3,
                        className="p-4",
                        style={"height": "100vh", "borderRight": "1px solid #444"}
                    ),
                    
                    # --- Main Content ---
                    dbc.Col(
                        [
                            html.H2("Project Comparison Dashboard", className="mb-4"),
                            
                            # Comparison Cards
                            dbc.Row(
                                [
                                    # Project A Card
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Project A Metrics", className="bg-info text-dark fw-bold"),
                                                dbc.CardBody(
                                                    [
                                                        html.H4(id='out-a-npv', children="NPV: $0"),
                                                        html.H5(id='out-a-irr', children="IRR: 0%"),
                                                        html.P(id='out-a-payback', children="Payback: 0 yrs"),
                                                        html.P(id='out-a-risk', children="Prob Loss: 0%"),
                                                    ]
                                                )
                                            ],
                                            inverse=True, style={"border": "1px solid #17a2b8"}
                                        ),
                                        width=6
                                    ),
                                    # Project B Card
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Project B Metrics", className="bg-warning text-dark fw-bold"),
                                                dbc.CardBody(
                                                    [
                                                        html.H4(id='out-b-npv', children="NPV: $0"),
                                                        html.H5(id='out-b-irr', children="IRR: 0%"),
                                                        html.P(id='out-b-payback', children="Payback: 0 yrs"),
                                                        html.P(id='out-b-risk', children="Prob Loss: 0%"),
                                                    ]
                                                )
                                            ],
                                            inverse=True, style={"border": "1px solid #ffc107"}
                                        ),
                                        width=6
                                    ),
                                ],
                                className="mb-4"
                            ),
                            
                            # Visuals
                            dbc.Row(
                                [
                                    dbc.Col(dcc.Graph(id='chart-cumulative-flows'), width=6),
                                    dbc.Col(dcc.Graph(id='chart-risk-hist'), width=6),
                                ],
                                className="mb-4"
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
