
from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    # --- HERO SECTION ---
    dbc.Row([
        dbc.Col([
            html.H1("FinMod AI", className="display-3 fw-bold text-primary mb-3"),
            html.P("The Intelligent CFO Agent for Modern Finance", className="lead text-dark"),
            html.Hr(className="my-4", style={"borderColor": "rgba(0,0,0,0.1)"}),
            html.P("Select a module below to begin your automated financial analysis.", className="text-muted"),
        ], width=12, className="text-center py-5")
    ]),

    # --- MODULE CARDS SECTION ---
    dbc.Row([
        # Card 1: Valuation Agent
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📊 Core Module"),
                dbc.CardBody([
                    html.H3("Valuation Agent", className="card-title text-info"),
                    html.P(
                        "Perform automated Discounted Cash Flow (DCF) modeling. "
                        "Includes sensitivity analysis and WACC calculations.",
                        className="card-text mt-3",
                    ),
                    dbc.Button("Launch Valuation", href="/valuation", color="info", className="mt-4 w-100 fw-bold"),
                ])
            ], className="h-100 shadow-lg border-info")
        ], width=12, lg=5, className="mb-4"),

        # Spacer
        dbc.Col([], width=12, lg=2),

        # Card 2: Budget Agent
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("💰 AI Module"),
                dbc.CardBody([
                    html.H3("Budget Agent", className="card-title text-warning"),
                    html.P(
                        "Run AI-powered variance analysis and automated re-forecasting. "
                        "Detects anomalies in spending patterns.",
                        className="card-text mt-3",
                    ),
                    dbc.Button("Launch Budgeting", href="/budget", color="warning", className="mt-4 w-100 fw-bold text-dark"),
                ])
            ], className="h-100 shadow-lg border-warning")
        ], width=12, lg=5, className="mb-4"),
    ], className="justify-content-center px-5"),

    # --- FOOTER TRUST BADGES ---
    dbc.Row([
        dbc.Col([
            html.P("🔒 Secure Environment • ⚡ Powered by Gemini AI • ☁️ Cloud Native", 
                   className="text-muted text-center mt-5 small")
        ])
    ])
], fluid=True)
