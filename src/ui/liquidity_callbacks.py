from dash import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.core.treasury import TreasuryEngine

def register_liquidity_callbacks(app):
    
    @app.callback(
        [Output('gauge-runway', 'figure'),
         Output('card-dso', 'children'),
         Output('card-dio', 'children'),
         Output('card-dpo', 'children'),
         Output('card-ccc', 'children'),
         Output('waterfall-liquidity', 'figure')],
        [Input('btn-refresh-liquidity', 'n_clicks'),
         Input('input-net-burn', 'value')]
    )
    def update_liquidity_dashboard(n_clicks, net_burn):
        # 1. Inputs / Mock Data
        # Current Cash Logic
        current_cash = 2500000 # $2.5M Opening
        
        # If user provides burn, use it. Else calculate from mock.
        # User input is typically negative for burn.
        if net_burn is None:
            net_burn = -50000
            
        # 2. Runway Calculation
        # TreasuryEngine.calculate_cash_runway(cash, burn)
        runway_months = TreasuryEngine.calculate_cash_runway(current_cash, net_burn)
        
        # 3. Gauge Chart
        # Red < 3, Yellow 3-6, Green > 6
        gauge_color = "red"
        if runway_months > 6:
            gauge_color = "green"
        elif runway_months >= 3:
            gauge_color = "yellow"
            
        # Handle Infinite
        val_display = runway_months
        if runway_months == float('inf'):
            val_display = 99 # Max out gauge
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = val_display,
            title = {'text': "Months"},
            number = {'suffix': " Mo"},
            gauge = {
                'axis': {'range': [None, 24]},
                'bar': {'color': gauge_color},
                'steps': [
                    {'range': [0, 3], 'color': "rgba(255, 99, 71, 0.3)"},
                    {'range': [3, 6], 'color': "rgba(255, 255, 0, 0.3)"},
                    {'range': [6, 24], 'color': "rgba(50, 205, 50, 0.3)"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': val_display
                }
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        
        # 4. Working Capital Metrics (Mock Data)
        # Create a df with revenue, cogs, receivables, inventory, payables
        # Let's say we have 1 year of data
        data = {
            'revenue': [12000000], # Annual
            'cogs': [8000000],
            'receivables': [1000000], # ~30 days
            'inventory': [2000000], # ~90 days 
            'payables': [1500000] # ~68 days
        }
        df_wc = pd.DataFrame(data)
        metrics = TreasuryEngine.calculate_working_capital_metrics(df_wc)
        
        dso_txt = f"{metrics['dso']} Days"
        dio_txt = f"{metrics['dio']} Days"
        dpo_txt = f"{metrics['dpo']} Days"
        ccc_txt = f"{metrics['ccc']} Days"
        
        # 5. Liquidity Bridge (Waterfall)
        # Mocking "Opening" -> "Movements" -> "Closing"
        # Weekly or Monthly view?
        # Let's show a "Month Flow" bridge
        
        opening = current_cash
        collections = 1000000
        payroll = -600000
        rent = -50000
        suppliers = -400000
        capex = -50000
        
        # Net burn logic check: net_burn user input vs these flows?
        # We'll use the user input 'net_burn' to scale the "Other/Burn" or visually consistent?
        # Let's construct a bridge that sums to Opening + NetBurn approx.
        # Ideally, we construct a scenario.
        
        # Simple Waterfall
        fig_waterfall = go.Figure(go.Waterfall(
            name = "20", orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "relative", "relative", "total"],
            x = ["Opening Balance", "Collections (+)", "Payroll (-)", "Suppliers (-)", "Rent (-)", "CapEx (-)", "Closing Balance"],
            textposition = "outside",
            text = [f"${opening/1000:.0f}k", f"${collections/1000:.0f}k", f"${payroll/1000:.0f}k", f"${suppliers/1000:.0f}k", f"${rent/1000:.0f}k", f"${capex/1000:.0f}k", "Total"],
            y = [opening, collections, payroll, suppliers, rent, capex, 0],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ))
        
        fig_waterfall.update_layout(
             title = "Monthly Liquidity Bridge",
             showlegend = False,
             template="plotly_dark",
             waterfallgap = 0.3
        )
        
        return fig_gauge, dso_txt, dio_txt, dpo_txt, ccc_txt, fig_waterfall
