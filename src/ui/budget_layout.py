from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

def create_budget_layout():
    # Wrap in Container -> Row -> Col(Sidebar) + Col(Content)
    return dbc.Container(
        [
            dbc.Row(
                [
                    # --- Sidebar ---
                    dbc.Col(
                        [
                            html.H2("Budget Agent", className="mb-4 text-warning"),
                            
                            # Navigation
                            html.Div([
                                dbc.NavLink("Valuation", href="/valuation", active="exact", className="mb-2"),
                                dbc.NavLink("Budgeting", href="/budgeting", active="exact", className="mb-2"),
                            ], className="mb-4"),
                            
                            html.Hr(),
                            
                            # Moved Controls to Sidebar for consistency? 
                            # User originally asked for "Top Control Bar".
                            # But standardizing Sidebar logic suggests putting some controls here.
                            # I will keep the Navigation here.
                            # And I will KEEP the Top Control Bar in the Right Column as originally designed?
                            # Or move filters here?
                            # "Update the Sidebar to include NavLink".
                            # I'll just put Nav here.
                        ],
                        width=3,
                        className="p-4",
                        style={"height": "100vh", "borderRight": "1px solid #444"}
                    ),
                    
                    # --- Main Content ---
                    dbc.Col(
                        [
                            html.H2("Budget vs Actuals Module", className="mb-4 text-warning"),
                            
                            # --- Top Control Bar ---
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("Filter Department"),
                                            dbc.Select(
                                                id='dept-filter',
                                                options=[
                                                    {"label": "All Departments", "value": "All"},
                                                    {"label": "Sales", "value": "Sales"},
                                                    {"label": "Engineering", "value": "Engineering"},
                                                    {"label": "Marketing", "value": "Marketing"},
                                                ],
                                                value="All"
                                            )
                                        ],
                                        width=4
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("AI Actions"),
                                            dbc.Button("Run AI Re-forecast", id='btn-reforecast', color="warning", className="w-100")
                                        ],
                                        width=3,
                                        className="d-flex align-items-end"
                                    )
                                ],
                                className="mb-4"
                            ),
                            
                            html.Hr(),
                            
                            # --- KPI Row ---
                            dbc.Row(
                                [
                                    dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Budget", className="card-title"), html.H3(id='kpi-budget', children="$0.00")])], className="mb-3"), width=4),
                                    dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Actual Spend", className="card-title"), html.H3(id='kpi-actual', children="$0.00")])], className="mb-3"), width=4),
                                    dbc.Col(dbc.Card([dbc.CardBody([html.H5("Net Variance", className="card-title"), html.H3(id='kpi-variance', children="$0.00")])], className="mb-3"), width=4),
                                ],
                                className="mb-4"
                            ),
                            
                            # --- Main Visualization (Bullet Chart) ---
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Graph(id='budget-bullet-chart', style={'height': '400px'}),
                                        width=12
                                    )
                                ],
                                className="mb-4"
                            ),
                            
                            # --- Detailed Variance Grid ---
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(
                                            [
                                                html.H4("Detailed Variance Analysis", className="mb-3"),
                                                dash_table.DataTable(
                                                    id='variance-table',
                                                    columns=[
                                                        {"name": "Department", "id": "department"},
                                                        {"name": "GL Code", "id": "gl_code"},
                                                        {"name": "Budget", "id": "budget_amount", "type": "numeric", "format": {"specifier": "$,.2f"}},
                                                        {"name": "Actual", "id": "actual_amount", "type": "numeric", "format": {"specifier": "$,.2f"}},
                                                        {"name": "Variance %", "id": "variance_pct", "type": "numeric", "format": {"specifier": ".1%"}},
                                                        {"name": "Status", "id": "status"}, 
                                                    ],
                                                    style_header={
                                                        'backgroundColor': '#303030',
                                                        'color': 'white',
                                                        'fontWeight': 'bold'
                                                    },
                                                    style_cell={
                                                        'backgroundColor': '#222',
                                                        'color': 'white',
                                                        'border': '1px solid #444'
                                                    },
                                                    style_data_conditional=[
                                                        {
                                                            'if': {
                                                                'filter_query': '{status} = "Unfavorable"',
                                                            },
                                                            'backgroundColor': '#660000',
                                                            'color': 'white'
                                                        },
                                                        {
                                                            'if': {
                                                                'filter_query': '{status} = "Favorable"',
                                                            },
                                                            'backgroundColor': '#004400',
                                                            'color': 'white'
                                                        }
                                                    ],
                                                    filter_action="native",
                                                    sort_action="native",
                                                    page_size=10
                                                )
                                            ]
                                        ),
                                        width=12
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
