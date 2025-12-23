from dash import Input, Output, State, callback, no_update
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date
from src.core.variance import BudgetEngine

def get_mock_data():
    # Create a dummy dataset (Jan Actuals, Feb-Dec Future)
    # Engineering: Overspending in Jan
    # Sales: Underspending in Jan
    departments = ["Engineering", "Sales", "Marketing", "G&A"]
    months = [date(2024, i, 1) for i in range(1, 13)]
    
    data = []
    
    for month in months:
        for dept in departments:
            # Base Budget
            budget = 10000.0 if dept == "Engineering" else 5000.0
            
            # Actuals (Only for Jan - Month 1)
            actual = 0.0
            if month.month == 1:
                if dept == "Engineering":
                    actual = 12000.0 # Unfavorable
                elif dept == "Sales":
                    actual = 4000.0 # Favorable
                else:
                    actual = budget # Neutral
            
            # GL Code simplification
            gl = "5000-Salaries"
            
            data.append({
                "department": dept,
                "gl_code": gl,
                "month": month,
                "amount_budget": budget,
                "amount_actual": actual
            })
            
    return pd.DataFrame(data)

# Global Mock Data Store (Simplification for this persistent session demo)
# In real app, this would be in a dcc.Store or database.
MOCK_DF = get_mock_data()

def register_budget_callbacks(app):
    
    @app.callback(
        [
            Output('variance-table', 'data'),
            Output('budget-bullet-chart', 'figure'),
            Output('kpi-budget', 'children'),
            Output('kpi-actual', 'children'),
            Output('kpi-variance', 'children')
        ],
        [
            Input('dept-filter', 'value'),
            Input('btn-reforecast', 'n_clicks')
        ]
    )
    def update_budget_dashboard(dept_filter, n_clicks):
        global MOCK_DF
        
        # 1. Logic: Reforecast
        # Check if Reforecast triggered (context is useful but simpler to just check n_clicks > 0)
        # Note: In a real multi-user app, we wouldn't mutate global MOCK_DF like this without dcc.Store.
        # But for this "Senior" demo verifying logic, we will apply forecast if clicked.
        
        df_to_use = MOCK_DF.copy()
        
        # If forecasting, we update the budgets for Feb-Dec
        if n_clicks and n_clicks > 0:
            engine = BudgetEngine()
            df_to_use = engine.generate_forecast(df_to_use)
            # Forecaster updates 'forecasted_budget' column in 'generate_forecast'. 
            # But the table expects 'amount_budget'.
            # Let's override amount_budget with forecasted for the display if forecasting.
            if 'forecasted_budget' in df_to_use.columns:
                df_to_use['amount_budget'] = df_to_use['forecasted_budget']

        # 2. Logic: Calculate Variance (Vectorized)
        # BudgetEngine expects budget_df and actual_df usually, but calculate_variance 
        # is designed for separate DFs. Our Mock is already merged/single source.
        # Let's adapt. calculate_variance expects 'amount_budget' and 'amount_actual' columns?
        # Let's look at source: 
        # merged['amount_budget'].fillna(0) ... merged['variance_abs'] = budget - actual
        # So we can just call the logic part or pass the DF as both?
        # Actually BudgetEngine.calculate_variance merges them. 
        # If we already have a merged DF, we can just run the calc logic directly or 
        # split them up to use the engine strictly. 
        # Let's split to be strict "MVC" and use the Engine.
        
        budget_cols = ['department', 'gl_code', 'month', 'amount_budget']
        actual_cols = ['department', 'gl_code', 'month', 'amount_actual']
        
        # We need to rename columns back to 'amount' for the Engine input?
        # Engine: "Expects DataFrames with columns: [..., 'amount']"
        b_df = df_to_use[budget_cols].rename(columns={'amount_budget': 'amount'})
        a_df = df_to_use[actual_cols].rename(columns={'amount_actual': 'amount'})
        
        engine = BudgetEngine()
        # This will merge them back. A bit redundant but proves the Engine works.
        full_df = engine.calculate_variance(b_df, a_df)
        
        # 3. Filtering
        if dept_filter and dept_filter != "All":
            filtered_df = full_df[full_df['department'] == dept_filter]
        else:
            filtered_df = full_df
            
        # 4. Aggregations for KPIs
        total_budget = filtered_df['amount_budget'].sum()
        total_actual = filtered_df['amount_actual'].sum()
        total_variance = filtered_df['variance_abs'].sum() # Budget - Actual
        
        # 5. Bullet Chart
        # Actual vs Budget
        # Range could be Forecast? Or just max range.
        # User: "Forecast (Background Range)".
        # Since we overwrote Budget with Forecast in reforecast mode, Budget IS Forecast.
        # If not reforecast, Budget is Budget.
        # Let's use simple Actual vs Budget Bullet.
        
        fig = go.Figure(go.Indicator(
            mode = "number+gauge+delta",
            value = total_actual,
            delta = {'reference': total_budget, 'position': "top", 'relative': False, 'valueformat': "$,.0f"},
            domain = {'x': [0.1, 0.9], 'y': [0.2, 0.8]}, # Center it
            title = {'text': "Spend Performance"},
            number = {'prefix': "$"},
            gauge = {
                'shape': "bullet",
                'axis': {'range': [None, max(total_budget, total_actual) * 1.2]},
                'threshold': {
                    'line': {'color': "white", 'width': 2},
                    'thickness': 0.75,
                    'value': total_budget
                },
                'bar': {'color': "#1f77b4"}, # Blue for Actuals
                # We can add background ranges if we had "Original Budget" vs "Forecast" separately.
                # For now, simplistic.
            }
        ))
        
        fig.update_layout(
            height=250,
            margin={'t': 20, 'b': 20},
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'}
        )
        
        # 6. Table Data
        # Format for DataTable
        table_data = filtered_df.to_dict('records')
        
        # 7. KPI Formatting
        kpi_b = f"${total_budget:,.2f}"
        kpi_a = f"${total_actual:,.2f}"
        kpi_v = f"${total_variance:,.2f}" # Positive = Favorable (Underspend) ? 
        # Wait, calculate_variance: variance_abs = Budget - Actual.
        # If Budget 100, Actual 120. Var = -20.
        # If Var is negative, it's Unfavorable (Red).
        
        # Logic for Color (handled in Layout conditional style, here just text)
        
        return table_data, fig, kpi_b, kpi_a, kpi_v
