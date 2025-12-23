from dash import dcc, html
import dash_bootstrap_components as dbc
import urllib.parse

def create_layout():
    return dbc.Container([
        # Error Notification Component
        dbc.Toast(
            id="error-toast",
            header="Error",
            is_open=False,
            dismissable=True,
            duration=4000,
            icon="danger",
            style={"position": "fixed", "top": 80, "right": 10, "zIndex": 1050},
        ),

        # SECTION 1: HEADER & ACTIONS
        dbc.Row([
            dbc.Col([
                html.H2("Discounted Cash Flow (DCF)", className="fw-bold"),
                html.P("Projected Enterprise Value & Sensitivity Analysis", className="text-muted")
            ], width=8),
            dbc.Col([
                # The Download Button
                 html.A(
                    dbc.Button("📥 Template", id="btn-dl", color="light", className="me-2"),
                    id="download-link",
                    download="finmod_template.csv",
                    href="data:text/csv;charset=utf-8," + urllib.parse.quote("year,revenue,growth_rate,ebitda_margin,tax_rate,capex_ratio\n2024,1000,0.10,0.25,0.21,0.05\n2025,1100,0.10,0.25,0.21,0.05"),
                    target="_blank"
                ),
                dbc.Button("▶ Run Model", id="btn-calculate", color="primary", className="fw-bold")
            ], width=4, className="text-end")
        ], className="mb-4 align-items-center"),

        # SECTION 2: INPUTS (Left) & OUTPUTS (Right)
        dbc.Row([
            # --- LEFT COLUMN: INPUTS CARD ---
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Model Assumptions", className="bg-white fw-bold border-bottom-0 pt-3"),
                    dbc.CardBody([
                        html.Label("WACC (%)", className="small fw-bold text-secondary"),
                        dcc.Slider(
                            id='input-wacc',
                            min=0.05, max=0.15, step=0.005, 
                            value=0.10,
                            marks={0.05: '5%', 0.10: '10%', 0.15: '15%'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        
                        html.Label("Terminal Growth (%)", className="small fw-bold text-secondary mt-3"),
                        dcc.Slider(
                            id='input-term-growth',
                            min=0.01, max=0.05, step=0.005, 
                            value=0.03,
                            marks={0.01: '1%', 0.03: '3%', 0.05: '5%'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        
                        html.Label("Cash Flows (CSV)", className="small fw-bold text-secondary mt-3"),
                        dcc.Textarea(
                            id='input-cashflows',
                            placeholder="2024, 1000\n2025, 1200...", 
                            value="100,120,140,160,180", # Default simple list for compatibility
                            className="form-control", 
                            style={'fontFamily': 'monospace', 'fontSize': '12px', 'height': '150px'}
                        ),
                        
                        # Error Alert (Moved here for visibility)
                        dbc.Alert(id='error-alert', color="danger", is_open=False, duration=4000, className="mt-3"),
                        
                     ])
                ], className="shadow-sm border-0 h-100") # 'border-0' + 'shadow-sm' = Modern Look
            ], width=12, lg=4),

            # --- RIGHT COLUMN: CHARTS ---
            dbc.Col([
                # SCORECARD ROW
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H6("Enterprise Value", className="card-subtitle text-muted small"),
                            html.H3("$0.00", id="output-ev", className="card-title text-primary fw-bold")
                        ])
                    ], className="shadow-sm border-0 mb-3"), width=6),
                    
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H6("Equity Value", className="card-subtitle text-muted small"),
                            html.H3("$0.00", id="output-equity", className="card-title text-success fw-bold")
                        ])
                    ], className="shadow-sm border-0 mb-3"), width=6),
                ]),
                 # Share Price (Hidden or extra row? User asked for 2 cards in scorecard, but callback outputs 3. Let's add the 3rd one)
                 dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.H6("Implied Share Price", className="card-subtitle text-muted small"),
                            html.H3("$0.00", id="output-share-price", className="card-title text-warning fw-bold")
                        ])
                    ], className="shadow-sm border-0 mb-3"), width=12),
                 ]),

                # MAIN CHART CARD (Waterfall)
                dbc.Card([
                    dbc.CardHeader("Valuation Visualization", className="bg-white fw-bold border-bottom-0"),
                    dbc.CardBody([
                        dcc.Graph(id="waterfall-graph", style={'height': '350px'})
                    ])
                ], className="shadow-sm border-0 mb-3"),
                
                # SENSITIVITY CHART CARD (Heatmap)
                dbc.Card([
                    dbc.CardHeader("Sensitivity Analysis", className="bg-white fw-bold border-bottom-0"),
                    dbc.CardBody([
                        dcc.Graph(id="sensitivity-heatmap", style={'height': '350px'})
                    ])
                ], className="shadow-sm border-0")
                
            ], width=12, lg=8)
        ])
    ], fluid=True, className="px-4 py-3", style={'fontFamily': 'Inter, sans-serif', 'backgroundColor': '#f8f9fa'})
