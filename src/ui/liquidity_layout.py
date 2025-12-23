from dash import dcc, html
import dash_bootstrap_components as dbc
from src.core.agent_logic import generate_cfo_insights

def create_liquidity_layout():
    return dbc.Container(
        [
            dbc.Row(
                [
                    # --- Sidebar (Navigation) ---
                    dbc.Col(
                        [
                            html.H2("Liquidity", className="mb-4 text-warning"),
                            
                            html.Div([
                                dbc.NavLink("Valuation", href="/valuation", active="exact", className="mb-2"),
                                dbc.NavLink("Budgeting", href="/budgeting", active="exact", className="mb-2"),
                                dbc.NavLink("Capital Projects", href="/capital", active="exact", className="mb-2"),
                                dbc.NavLink("Forecasting", href="/forecasting", active="exact", className="mb-2"),
                                dbc.NavLink("Liquidity", href="/liquidity", active="exact", className="mb-2"),
                            ], className="mb-4"),
                            
                            html.Hr(),
                            html.H5("Controls", className="text-secondary"),
                            dbc.Label("Simulate Burn ($/Mo)"),
                            dbc.Input(id='input-net-burn', type='number', value=-50000, className="mb-3"),
                            
                            dbc.Button("Refresh Metrics", id='btn-refresh-liquidity', color="warning", className="w-100"),
                        ],
                        width=3,
                        className="p-4",
                        style={"height": "100vh", "borderRight": "1px solid #444"}
                    ),
                    
                    # --- Main Content ---
                    dbc.Col(
                        [
                            html.H2("Cash & Working Capital Mission Control", className="mb-4"),
                            
                            # Top Row: Gauge + CCC Cards
                            dbc.Row(
                                [
                                    # Survival Gauge
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Cash Runway", className="bg-dark fw-bold"),
                                                dbc.CardBody(dcc.Graph(id='gauge-runway', style={'height': '250px'}))
                                            ],
                                            className="shadow-sm h-100"
                                        ),
                                        width=5
                                    ),
                                    
                                    # CCC Cards
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(dbc.Card([dbc.CardHeader("DSO (Receivables)"), dbc.CardBody([html.H3(id='card-dso', children="0 Days"), html.Small("Avg Time to Collect")])], color="dark", inverse=True, className="mb-2 h-100"), width=4),
                                                    dbc.Col(dbc.Card([dbc.CardHeader("DIO (Inventory)"), dbc.CardBody([html.H3(id='card-dio', children="0 Days"), html.Small("Avg Shelf Time")])], color="dark", inverse=True, className="mb-2 h-100"), width=4),
                                                    dbc.Col(dbc.Card([dbc.CardHeader("DPO (Payables)"), dbc.CardBody([html.H3(id='card-dpo', children="0 Days"), html.Small("Avg Payment Delay")])], color="dark", inverse=True, className="mb-2 h-100"), width=4),
                                                ],
                                                className="h-50"
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dbc.Card(
                                                            [
                                                                dbc.CardHeader("Cash Conversion Cycle (CCC)", className="text-info"),
                                                                dbc.CardBody(html.H2(id='card-ccc', children="0 Days", className="text-center"))
                                                            ],
                                                            color="secondary", inverse=True, className="h-100"
                                                        ), 
                                                        width=12
                                                    )
                                                ],
                                                className="h-50 pt-2"
                                            )
                                        ],
                                        width=7
                                    )
                                ],
                                className="mb-4",
                                style={"height": "320px"}
                            ),
                            
                            html.Hr(),
                            
                            # Bottom: Liquidity Bridge (Waterfall)
                            dbc.Card(
                                [
                                    dbc.CardHeader("Liquidity Bridge (Weekly Cash Flow)", className="bg-dark fw-bold"),
                                    dbc.CardBody(
                                        dcc.Graph(id='waterfall-liquidity', style={'height': '400px'})
                                    )
                                ],
                                className="shadow-sm"
                            )
                        ],
                        width=9,
                        className="p-4"
                    ),
                    
                    # AI Insight Card (Full Width at Bottom)
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader("🤖 AI CFO Commentary"),
                            dbc.CardBody([
                                dcc.Markdown(
                                    id='cfo-insight-box',
                                    children="Waiting for data analysis...", 
                                    style={'fontSize': '16px'}
                                )
                            ])
                        ], className="mb-4 mt-4 shadow-lg border-info"),
                        width=12,
                        className="px-4"
                    )
                ]
            )
        ],
        fluid=True
    )
