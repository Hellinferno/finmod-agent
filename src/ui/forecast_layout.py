from dash import dcc, html
import dash_bootstrap_components as dbc

def create_forecast_layout():
    return dbc.Container(
        [
            dbc.Row(
                [
                    # --- Sidebar (Controls) ---
                    dbc.Col(
                        [
                            html.H2("Forecasting", className="mb-4 text-info"),
                            
                            # Navigation
                            html.Div([
                                dbc.NavLink("Valuation", href="/valuation", active="exact", className="mb-2"),
                                dbc.NavLink("Budgeting", href="/budgeting", active="exact", className="mb-2"),
                                dbc.NavLink("Capital Projects", href="/capital", active="exact", className="mb-2"),
                                dbc.NavLink("Forecasting", href="/forecasting", active="exact", className="mb-2"),
                            ], className="mb-4"),
                            
                            html.Hr(),
                            
                            # Data Source
                            html.H5("Data Source", className="text-secondary"),
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div(['Drag and Drop or ', html.A('Select CSV')]),
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px 0'
                                },
                                multiple=False
                            ),
                            
                            # Horizon
                            html.H5("Forecast Horizon", className="mt-3 text-secondary"),
                            dbc.Label("Months to Predict"),
                            dcc.Slider(
                                id='horizon-slider',
                                min=3,
                                max=24,
                                step=3,
                                value=12,
                                marks={12: '1 Yr', 24: '2 Yrs'},
                                className="mb-4"
                            ),
                            
                            # Scenario
                            html.H5("Scenario Planner", className="mt-3 text-secondary"),
                            dbc.RadioItems(
                                id='scenario-selector',
                                options=[
                                    {'label': 'Base Case', 'value': 'Base'},
                                    {'label': 'Optimistic (+10%)', 'value': 'Optimistic'},
                                    {'label': 'Pessimistic (-15%)', 'value': 'Pessimistic'}
                                ],
                                value='Base',
                                className="mb-4"
                            ),
                        ],
                        width=3,
                        className="p-4",
                        style={"height": "100vh", "borderRight": "1px solid #444"}
                    ),
                    
                    # --- Main Content ---
                    dbc.Col(
                        [
                            html.H2("Revenue Forecast Analysis", className="mb-4"),
                            
                            # Fan Chart
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        dcc.Graph(id='forecast-fan-chart', style={'height': '500px'})
                                    )
                                ],
                                className="mb-4 shadow-sm"
                            ),
                            
                            html.Hr(),
                            html.H4("Under the Hood (Decomposition)", className="mb-3 text-secondary"),
                            
                            # Decomposition Panel
                            dbc.Row(
                                [
                                    dbc.Col(dcc.Graph(id='trend-chart', style={'height': '250px'}), width=4),
                                    dbc.Col(dcc.Graph(id='seasonal-chart', style={'height': '250px'}), width=4),
                                    dbc.Col(dcc.Graph(id='residuals-chart', style={'height': '250px'}), width=4),
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
