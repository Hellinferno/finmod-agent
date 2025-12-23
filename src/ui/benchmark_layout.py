from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

def create_benchmark_layout():
    return dbc.Container(
        [
            dbc.Row(
                [
                    # --- Sidebar (Controls) ---
                    dbc.Col(
                        [
                            html.H2("Market Intelligence", className="mb-4 text-primary"),
                            
                            # Navigation
                            html.Div([
                                dbc.NavLink("Valuation", href="/valuation", active="exact", className="mb-2"),
                                dbc.NavLink("Budgeting", href="/budgeting", active="exact", className="mb-2"),
                                dbc.NavLink("Capital Projects", href="/capital", active="exact", className="mb-2"),
                                dbc.NavLink("Forecasting", href="/forecasting", active="exact", className="mb-2"),
                                dbc.NavLink("Liquidity", href="/liquidity", active="exact", className="mb-2"),
                                dbc.NavLink("Benchmarking", href="/benchmarking", active="exact", className="mb-2"),
                            ], className="mb-4"),
                            
                            html.Hr(),
                            
                            html.H5("Peer Group", className="text-secondary"),
                            dbc.Label("Compare against: (e.g. MSFT, AAPL)"),
                            dbc.Input(id='input-tickers', type='text', value="AAPL, MSFT, GOOG, NVDA", className="mb-3"),
                            
                            dbc.Button("Fetch Market Data", id='btn-fetch-market', color="primary", className="w-100 mb-4"),
                            
                            html.Div(id='market-status', className="text-muted small")
                        ],
                        width=3,
                        className="p-4",
                        style={"height": "100vh", "borderRight": "1px solid #444"}
                    ),
                    
                    # --- Main Content ---
                    dbc.Col(
                        [
                            html.H2("Competitor Benchmarking", className="mb-4"),
                            
                            # Radar Chart
                            dbc.Card(
                                [
                                    dbc.CardHeader("Industry Position (Radar)", className="bg-dark fw-bold"),
                                    dbc.CardBody(
                                        dcc.Graph(id='radar-benchmark', style={'height': '500px'})
                                    )
                                ],
                                className="mb-4 shadow-sm"
                            ),
                            
                            html.Hr(),
                            
                            # Leaderboard
                            html.H4("Industry Leaderboard", className="text-secondary mb-3"),
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        dash_table.DataTable(
                                            id='table-benchmark',
                                            columns=[
                                                {'name': 'Ticker', 'id': 'Ticker'},
                                                {'name': 'Profit Margin', 'id': 'Profit Margin', 'type': 'numeric', 'format': {'specifier': '.1%'}},
                                                {'name': 'ROE', 'id': 'ROE', 'type': 'numeric', 'format': {'specifier': '.1%'}},
                                                {'name': 'Current Ratio', 'id': 'Current Ratio', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                                                {'name': 'Debt/Equity', 'id': 'Debt to Equity', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                                                {'name': 'P/E', 'id': 'Trailing PE', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                                            ],
                                            # Removed dark mode styles
                                            style_data_conditional=[
                                                {
                                                    'if': {'filter_query': '{Ticker} = "MY COMPANY"'},
                                                    'backgroundColor': '#FFD700',
                                                    'color': 'black',
                                                    'fontWeight': 'bold'
                                                }
                                            ],
                                            sort_action='native'
                                        )
                                    )
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
