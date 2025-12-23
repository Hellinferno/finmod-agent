from dash import Input, Output, State, callback, no_update
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc
from pydantic import ValidationError

from src.core.valuation import calculate_dcf, run_sensitivity_analysis
from src.models.schemas import FinancialInput

def register_callbacks(app):
    
    @app.callback(
        [
            Output('output-ev', 'children'),
            Output('output-equity', 'children'),
            Output('output-share-price', 'children'),
            Output('waterfall-graph', 'figure'),
            Output('sensitivity-heatmap', 'figure'),
            Output('error-alert', 'children'),
            Output('error-alert', 'is_open')
        ],
        [Input('btn-calculate', 'n_clicks')],
        [
            State('input-wacc', 'value'),
            State('input-term-growth', 'value'),
            State('input-cashflows', 'value')
        ],
        prevent_initial_call=True
    )
    def update_model(n_clicks, wacc, term_growth, cashflows_str):
        if not n_clicks:
            return no_update

        # 1. Parsing and Validation
        try:
            # Parse CSV string
            if not cashflows_str:
                raise ValueError("Cash flows cannot be empty")
            
            try:
                cash_flows = [float(x.strip()) for x in cashflows_str.split(',')]
            except ValueError:
                raise ValueError("Cash flows must be a comma-separated list of numbers")

            # Instantiate Pydantic Model
            # Note: We divide percentages by 100 if user input 10 for 10%?
            # Layout default was 0.10. User prompt says "WACC (%) -> value=0.10".
            # So inputs are decimals.
            
            fin_input = FinancialInput(
                wacc=float(wacc),
                terminal_growth_rate=float(term_growth),
                cash_flows=cash_flows
            )
            
        except (ValidationError, ValueError) as e:
            # Format error message
            msg = str(e)
            if hasattr(e, 'errors'): # Pydantic
                msg = "; ".join([err['msg'] for err in e.errors()])
            
            return no_update, no_update, no_update, no_update, no_update, msg, True

        # 2. Calculation
        try:
            results = calculate_dcf(fin_input)
            sensitivity = run_sensitivity_analysis(fin_input)
        except Exception as e:
             return no_update, no_update, no_update, no_update, no_update, f"Calculation Error: {str(e)}", True

        # 3. Visualization
        
        # Format KPIs
        ev_fmt = f"${results['enterprise_value']:,.2f}"
        eq_fmt = f"${results['equity_value']:,.2f}"
        # Implied Share Price: Arbitrary share count since not in input.
        # Let's assume 1M shares or just display "N/A" if not provided?
        # User requested "Implied Share Price".
        # I'll assume 1.0 (Value per share = Equity Value) or 1M shares.
        # Or better, just display Equity Value / 1 (Per Share implies we assume 1 share 100%).
        # I'll just equate it to Equity Value for this demo context or divide by 1.
        share_price_fmt = f"${results['equity_value']:,.2f} (100% Equity)" 

        # Waterfall Chart
        # PV of Cash Flows vs PV of Terminal Value
        npv_fcf = results['npv']
        pv_tv = results['pv_terminal_value']
        ev = results['enterprise_value']
        
        fig_waterfall = go.Figure(go.Waterfall(
            name = "DCF Valuation",
            orientation = "v",
            measure = ["relative", "relative", "total"],
            x = ["PV of Free Cash Flows", "PV of Terminal Value", "Enterprise Value"],
            textposition = "outside",
            text = [f"{npv_fcf:.0f}", f"{pv_tv:.0f}", f"{ev:.0f}"],
            y = [npv_fcf, pv_tv, ev],
            connector = {"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig_waterfall.update_layout(
            title = "Valuation Waterfall",
            template="plotly_dark",
            showlegend = False
        )
        
        # Heatmap
        # Sensitivity matrix is 5x5
        # Axes
        base_wacc = fin_input.wacc
        base_growth = fin_input.growth_rate_projection # 0.0
        
        wacc_axis = np.linspace(base_wacc - 0.02, base_wacc + 0.02, 5)
        growth_axis = np.linspace(base_growth - 0.01, base_growth + 0.01, 5)
        
        # Format axis labels to percentages
        x_labels = [f"G:{g:.1%}" for g in growth_axis]
        y_labels = [f"W:{w:.1%}" for w in wacc_axis]
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=sensitivity,
            x=x_labels,
            y=y_labels,
            colorscale='Viridis',
            hoverongaps = False,
            texttemplate="%{z:.0f}"
        ))
        
        fig_heatmap.update_layout(
            title="Sensitivity: WACC vs Growth",
            template="plotly_dark",
            xaxis_title="Growth Scenarios",
            yaxis_title="WACC Scenarios"
        )
        
        return ev_fmt, eq_fmt, share_price_fmt, fig_waterfall, fig_heatmap, "", False
