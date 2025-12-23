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
            Output('error-toast', 'is_open'),
            Output('error-toast', 'header'),
            Output('error-toast', 'children')
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

        # Wrapper for Error Handling
        try:
            # 1. Parsing and Validation
            try:
                # Handle Multiline (Year, CashFlow) OR Simple List
                if not cashflows_str:
                     raise ValueError("Cash flows cannot be empty")
                     
                if '\n' in cashflows_str or (',' in cashflows_str and cashflows_str.count(',') > len(cashflows_str.split('\n'))):
                    # It's likely a CSV structure
                    rows = [row.split(',') for row in cashflows_str.strip().split('\n') if row.strip()]
                    cash_flows = [float(row[-1].strip()) for row in rows]
                else:
                    # Fallback
                    cash_flows = [float(x.strip()) for x in cashflows_str.split(',')]
                    
                if len(cash_flows) < 2:
                    raise ValueError("Need at least 2 years of cash flow data.")
                    
            except ValueError:
                raise ValueError("Invalid format. Usage: 'Year, Value' per line (e.g. 2024, 1000) or comma-separated list.")

            # Instantiate Pydantic Model
            fin_input = FinancialInput(
                wacc=float(wacc),
                terminal_growth_rate=float(term_growth),
                cash_flows=cash_flows
            )

            # 2. Calculation
            results = calculate_dcf(fin_input)
            sensitivity = run_sensitivity_analysis(fin_input)

            # 3. Visualization
            ev_fmt = f"${results['enterprise_value']:,.2f}"
            eq_fmt = f"${results['equity_value']:,.2f}"
            share_price_fmt = f"${results['equity_value']:,.2f} (100% Equity)" 

            # Waterfall Chart
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
                title = dict(text="Valuation Waterfall", font=dict(size=14, color="#1e293b")),
                template="plotly_white",
                showlegend = False,
                font=dict(family="Inter, sans-serif", size=12, color="#1e293b"),
                margin=dict(l=40, r=20, t=40, b=40),
                hovermode="x unified",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, linecolor='#e2e8f0'),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False),
            )
            
            # Heatmap
            base_wacc = fin_input.wacc
            base_growth = fin_input.growth_rate_projection
            
            wacc_axis = np.linspace(base_wacc - 0.02, base_wacc + 0.02, 5)
            growth_axis = np.linspace(base_growth - 0.01, base_growth + 0.01, 5)
            
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
                title=dict(text="Sensitivity: WACC vs Growth", font=dict(size=14, color="#1e293b")),
                template="plotly_white",
                xaxis_title="Growth Scenarios",
                yaxis_title="WACC Scenarios",
                font=dict(family="Inter, sans-serif", size=12, color="#1e293b"),
                margin=dict(l=40, r=20, t=40, b=40),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, linecolor='#e2e8f0'),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False),
            )
            
            return ev_fmt, eq_fmt, share_price_fmt, fig_waterfall, fig_heatmap, False, "", ""

        except Exception as e:
            # ERROR: Show Toast
            error_msg = str(e)
            if hasattr(e, 'errors'): # Pydantic
                 error_msg = "; ".join([err['msg'] for err in e.errors()])
            
            # Return no_update for charts (Stability Fix), and OPEN the Toast
            return "---", "---", "---", no_update, no_update, True, "Calculation Error", error_msg
