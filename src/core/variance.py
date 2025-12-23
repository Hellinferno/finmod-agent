import pandas as pd
import numpy as np

class BudgetEngine:
    
    @staticmethod
    def calculate_variance(budget_df: pd.DataFrame, actual_df: pd.DataFrame) -> pd.DataFrame:
        """
        Vectorized calculation of variances.
        Expects DataFrames with columns: ['department', 'gl_code', 'month', 'amount']
        """
        # Merge on keys
        # We assume outer join to catch items in budget but not actuals, and vice versa.
        # FillNa with 0.0 for amounts.
        keys = ['department', 'gl_code', 'month']
        merged = pd.merge(budget_df, actual_df, on=keys, how='outer', suffixes=('_budget', '_actual'))
        
        merged['amount_budget'] = merged['amount_budget'].fillna(0.0)
        merged['amount_actual'] = merged['amount_actual'].fillna(0.0)
        
        # Vectorized Variance Stats
        # Var $ = Budget - Actual (Positive is Favorable for expenses? User said "If Actual > Budget, status is Unfavorable")
        # So usually Var = Budget - Actual.
        # If Budget 100, Actual 120. Var = -20. (Unfavorable).
        
        merged['variance_abs'] = merged['amount_budget'] - merged['amount_actual']
        
        # Var % = (Budget - Actual) / Budget ? or (Actual - Budget) / Budget?
        # User said: "Calculate % Variance. ... If Budget == 0, % Variance should be 0.0"
        # Usually Var% = (Budget - Actual) / Budget.
        # Let's align with "Status":
        # If Actual > Budget -> Unfavorable.
        
        # Handling Division by Zero
        # np.where(condition, x, y)
        budget_col = merged['amount_budget'].values
        var_abs_col = merged['variance_abs'].values
        
        # We need simple (Budget - Actual) / Budget
        # Safe division
        with np.errstate(divide='ignore', invalid='ignore'):
            var_pct = np.where(
                budget_col == 0.0, 
                0.0, # User req: "If Budget == 0, % Variance should be 0.0"
                var_abs_col / budget_col
            )
        
        merged['variance_pct'] = var_pct
        
        # Status
        # If Actual > Budget => Unfavorable
        # Else => Favorable (or Neutral if equal?)
        # Let's use np.select or np.where
        
        actual_col = merged['amount_actual'].values
        
        conditions = [
            actual_col > budget_col,  # Unfavorable
            actual_col < budget_col,  # Favorable
        ]
        choices = ["Unfavorable", "Favorable"]
        
        merged['status'] = np.select(conditions, choices, default="Neutral")
        
        return merged

    @staticmethod
    def generate_forecast(merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        1. Filter for Actuals (Year-to-Date? We assume 'amount_actual' > 0 implies YTD occurred?)
           Or we need a reference month?
           User said: "Filter for 'Actuals' (YTD). Calculate avg monthly spend (Burn Rate).
           For remaining months, replace Budget with Burn Rate."
           
           We need to know WHICH months are "remaining".
           Actually, the `merged_df` likely has months.
           Lets assume we distinguish YTD based on presence of actuals?
           Or simpler: For a dept, calculate avg_actual of months WHERE actual > 0 ?
           Then for months where actual == 0 (future), update budget?
           
           This is slightly ambiguous without a "Current Month" input.
           I will assume: Any row with `amount_actual` > 0 (or present) is YTD.
           Any row with `amount_actual` == 0 AND `amount_budget` > 0 is Future?
           
           Let's compute "Burn Rate" per Department.
           Burn Rate = Sum(Actuals) / Count(Months with Actuals)
        """
        
        # Identify months with actuals
        has_actuals = merged_df['amount_actual'] > 0
        ytd_df = merged_df[has_actuals]
        
        # Calculate Burn Rate per Department
        # We group by Department (and maybe GL Code? User said "per Department")
        # "Calculate the average monthly spend (Burn Rate) per Department."
        # This implies broad aggregation.
        
        burn_rates = ytd_df.groupby('department')['amount_actual'].mean().to_dict()
        
        # Apply to Future (rows without actuals)
        # We need to preserve the df structure.
        
        def apply_forecast(row):
            dept = row['department']
            actual = row['amount_actual']
            budget = row['amount_budget']
            
            # If no actual, it's future
            if actual == 0.0:
                # Replace Budget with Department Burn Rate
                return burn_rates.get(dept, budget) # Fallback to original budget if no burn rate
            else:
                return budget
                
        # Optimization: Vectorized approach is harder with map/dict lookup.
        # But `map` is reasonably fast.
        
        # Let's use map
        merged_df['forecasted_budget'] = merged_df['amount_budget'] # Default
        
        # Future mask
        future_mask = merged_df['amount_actual'] == 0.0
        
        # Map department to burn rate
        dept_burn_map = merged_df['department'].map(burn_rates)
        
        # Update forecasted_budget where future
        # If NaN in burn map (no history for that dept), keep original budget (fillna)
        dept_burn_values = dept_burn_map.fillna(merged_df['amount_budget'])
        
        merged_df.loc[future_mask, 'forecasted_budget'] = dept_burn_values[future_mask]
        
        return merged_df
