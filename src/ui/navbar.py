import dash_bootstrap_components as dbc

def create_navbar():
    return dbc.NavbarSimple(
        brand="FinMod Agent",
        brand_href="/",
        brand_style={'fontWeight': '600', 'fontFamily': 'Inter, sans-serif'},
        color="white",
        dark=False,  # This tells Bootstrap to use dark text
        sticky="top",
        className="mb-4",
        style={"boxShadow": "0 4px 6px -1px rgba(0,0,0,0.05)"}, # Subtle modern shadow
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
            dbc.NavItem(dbc.NavLink("Valuation", href="/valuation", active="exact")),
            dbc.NavItem(dbc.NavLink("Budgeting", href="/budget", active="exact")),
            dbc.NavItem(dbc.NavLink("Settings", href="#")), # Placeholder
        ]
    )
