from dash import Input, Output, State, callback_context
import dash
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64
import io
from datetime import date, datetime, timedelta
from src.core.forecasting import ForecastEngine 
from src.models.forecast_schemas import ForecastInput

def register_forecast_callbacks(app):
    
    @app.callback(
        [Output('forecast-fan-chart', 'figure'),
         Output('trend-chart', 'figure'),
         Output('seasonal-chart', 'figure'),
         Output('residuals-chart', 'figure')],
        [Input('upload-data', 'contents'),
         Input('horizon-slider', 'value'),
         Input('scenario-selector', 'value')],
        [State('upload-data', 'filename')]
    )
    def update_forecast(contents, horizon, scenario, filename):
        
        # 1. Data Loading (Synthetic or Uploaded)
        if contents is None:
            # Generate Synthetic Demo Data (3 years monthly)
            # 36 months
            dates = pd.date_range(start='2022-01-01', periods=36, freq='MS')
            t = np.arange(36)
            # Linear trend + Annual Seasonality (sin wave) + Noise
            values = 10000 + (200 * t) + (2000 * np.sin(2 * np.pi * t / 12)) + np.random.normal(0, 200, 36)
            dates_str = [d.strftime('%Y-%m-%d') for d in dates]
            values_list = values.tolist()
        else:
            # Parse CSV
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            try:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                # Assume columns "Date", "Value" or first two columns
                if len(df.columns) < 2:
                    return go.Figure(), go.Figure(), go.Figure(), go.Figure()
                
                # Basic cleanup
                df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
                dates_str = [d.strftime('%Y-%m-%d') for d in df.iloc[:, 0]]
                values_list = df.iloc[:, 1].tolist()
            except Exception as e:
                return go.Figure(layout={'title': f"Error parsing CSV: {str(e)}"}), go.Figure(), go.Figure(), go.Figure()

        # 2. Forecasting Call
        try:
            input_data = ForecastInput(
                dates=dates_str,
                values=values_list,
                periods=horizon,
                seasonality_mode='additive'
            )
            forecast_out = ForecastEngine.generate_forecast(input_data)
        except Exception as e:
            err_fig = go.Figure(layout={'title': f"Forecast Error: {str(e)}"})
            return err_fig, err_fig, err_fig, err_fig

        # 3. Scenario Logic
        multiplier = 1.0
        if scenario == 'Optimistic':
            multiplier = 1.10
        elif scenario == 'Pessimistic':
            multiplier = 0.85
            
        forecast_vals = np.array(forecast_out.forecast_values) * multiplier
        lower = np.array(forecast_out.lower_bound) * multiplier
        upper = np.array(forecast_out.upper_bound) * multiplier
        
        # 4. Fan Chart Construction
        fig = go.Figure()
        
        # Trace 1: History
        fig.add_trace(go.Scatter(
            x=forecast_out.history_dates,
            y=forecast_out.history_values,
            name='Historical',
            line=dict(color='blue')
        ))
        
        # Trace 2: Forecast
        fig.add_trace(go.Scatter(
            x=forecast_out.forecast_dates,
            y=forecast_vals,
            name='Forecast',
            line=dict(color='orange', dash='dash')
        ))
        
        # Trace 3: Upper Bound (Transparent)
        fig.add_trace(go.Scatter(
            x=forecast_out.forecast_dates,
            y=upper,
            name='Upper Bound',
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))
        
        # Trace 4: Lower Bound (Filled)
        fig.add_trace(go.Scatter(
            x=forecast_out.forecast_dates,
            y=lower,
            name='95% Confidence Interval',
            mode='lines',
            line=dict(width=0),
            fill='tonexty', # Fills to Upper Bound
            fillcolor='rgba(255, 165, 0, 0.2)', # Light Orange
            showlegend=True
        ))
        
        fig.update_layout(
            title="Revenue Forecast with 95% Confidence Interval",
            template="plotly_dark",
            hovermode="x unified"
        )
        
        # 5. Decomposition Charts
        # Trend
        trend_fig = go.Figure()
        trend_fig.add_trace(go.Scatter(x=forecast_out.history_dates, y=forecast_out.trend, line=dict(color='green')))
        trend_fig.update_layout(title="Trend Component", template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
        
        # Seasonal
        seasonal_fig = go.Figure()
        seasonal_fig.add_trace(go.Scatter(x=forecast_out.history_dates, y=forecast_out.seasonal, line=dict(color='cyan')))
        seasonal_fig.update_layout(title="Seasonal Pattern", template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
        
        # Residuals (Calculate roughly: History - (Trend + Seasonal))
        # Or use output if available. Our Schema has trend/seasonal.
        # Residuals = Val - (Trend + Seasonal)
        resid = np.array(forecast_out.history_values) - (np.array(forecast_out.trend) + np.array(forecast_out.seasonal))
        
        resid_fig = go.Figure()
        resid_fig.add_trace(go.Scatter(x=forecast_out.history_dates, y=resid, mode='markers', marker=dict(color='red', size=4)))
        resid_fig.add_hline(y=0, line_dash='dash', line_color='white')
        resid_fig.update_layout(title="Residuals (Noise)", template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
        
        return fig, trend_fig, seasonal_fig, resid_fig

    # --- PDF Download Callback ---
    @app.callback(
        Output('download-pdf-component', 'data'),
        Input('btn-download-pdf', 'n_clicks'),
        State('forecast-fan-chart', 'figure'),
        prevent_initial_call=True
    )
    def download_board_brief(n_clicks, fig_data):
        if not fig_data or not n_clicks:
            return None
            
        # Parse data from figure to get raw values for table
        # We assume trace 1 is Forecast (index 1) if present
        # Trace structure: 0=History, 1=Forecast, 2=Upper, 3=Lower
        try:
            data_traces = fig_data['data']
            # Find forecast trace
            forecast_trace = next((t for t in data_traces if t.get('name') == 'Forecast'), None)
            lower_trace = next((t for t in data_traces if t.get('name') == '95% Confidence Interval'), None)
            # Upper trace is likely hidden or 'Upper Bound'
            upper_trace = next((t for t in data_traces if t.get('name') == 'Upper Bound'), None)
            
            if not forecast_trace:
                return None
                
            dates = forecast_trace['x']
            values = forecast_trace['y']
            lower = lower_trace['y'] if lower_trace else [0]*len(values)
            upper = upper_trace['y'] if upper_trace else [0]*len(values)
            
            from src.core.export_engine import BoardBriefGenerator
            
            generator = BoardBriefGenerator()
            pdf_bytes = generator.generate_report(dates, values, lower, upper, fig_dict=fig_data)
            
            filename = f"Financial_Forecast_{datetime.now().strftime('%Y-%m-%d')}.pdf"
            
            return dcc.send_bytes(pdf_bytes, filename)
            
        except Exception as e:
            # In prod, handle error notification
            print(f"PDF Gen Error: {e}")
            return None

