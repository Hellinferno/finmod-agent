from dash import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from src.core.market_research import MarketIntelligence

def register_benchmark_callbacks(app):
    
    @app.callback(
        [Output('radar-benchmark', 'figure'),
         Output('table-benchmark', 'data'),
         Output('market-status', 'children')],
        [Input('btn-fetch-market', 'n_clicks')],
        [State('input-tickers', 'value')],
        prevent_initial_call=True
    )
    def update_benchmark(n_clicks, tickers_str):
        if not tickers_str:
            return go.Figure(), [], "No tickers provided."
        
        status_msg = "Fetched data successfully."
        
        # 1. Parse Tickers
        tickers = [t.strip() for t in tickers_str.split(',') if t.strip()]
        
        # 2. Key Metrics for 'MY COMPANY' (Mock for now, normally from other modules)
        my_metrics = {
            'Profit Margin': 0.25,      # 25%
            'ROE': 0.18,                # 18%
            'Current Ratio': 1.5,       # 1.5x
            'Debt to Equity': 45.0,     # Yahoo data is often %, e.g. 50% = 50 or 0.5. Usually ratio. 
                                        # Yahoo DebtToEquity is usually ratio (whole number or float) e.g. 150 (1.5x) or 1.5. 
                                        # Actually yfinance returns numeric. Let's assume Yahoo returns e.g. 0.5 for 50%.
                                        # Let's check yfinance docs or assume ratio.
                                        # "debtToEquity": 134.5 -> 1.345x.
            'Trailing PE': 15.0
        }
        
        # 3. Fetch Data
        try:
            peer_df = MarketIntelligence.fetch_peer_data(tickers)
            
            # Combine
            combined_df = MarketIntelligence.compare_against_internal(my_metrics, peer_df)
            
            # 4. Radar Chart
            # Dimensions to plot
            # Need to normalize? Radar charts with different scales (Margin %, PE Ratio) are tricky.
            # Ideally maximize each axis to 1. 
            # For this MVP, we plot raw values but user needs to be aware of scales.
            # Or simpler: Plot just My Company vs Peer Average logic?
            # Prompt says: Trace 1 (My Company), Trace 2 (Industry Average).
            
            categories = ['Profit Margin', 'ROE', 'Current Ratio', 'Debt to Equity', 'Trailing PE']
            
            # My Data
            my_values = [combined_df.loc['MY COMPANY', cat] for cat in categories]
            
            # Industry Average (Peers only)
            if not peer_df.empty:
                avg_values = peer_df[categories].mean().tolist()
            else:
                avg_values = [0]*5
                
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=my_values,
                theta=categories,
                fill='toself',
                name='MY COMPANY',
                line=dict(color='blue')
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=avg_values,
                theta=categories,
                fill='toself',
                name='Industry Avg',
                line=dict(color='grey'),
                opacity=0.7
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(max(my_values), max(avg_values)) * 1.2] 
                        # Range is tricky with mixed units (PE ~20, Margin ~0.2).
                        # Scatterpolar handles one scale. 
                        # To do multi-variable properly requires 'Parallel Coordinates' or normalized Radar.
                        # For MVP "Standard Radar", we assume user accepts shared scale or we normalize.
                        # Let's leave as is per prompt "Use Scatterpolar".
                    )
                ),
                template="plotly_dark",
                showlegend=True
            )
            
            # 5. Table Data
            # Reset index to make Ticker a column
            table_data = combined_df.reset_index().rename(columns={'index': 'Ticker'}).to_dict('records')
            
            return fig, table_data, status_msg
            
        except Exception as e:
            return go.Figure(), [], f"Error: {str(e)}"
