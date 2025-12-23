import pandas as pd

# Hardcoded contacts for MVP
DEPARTMENT_HEADS = {
    "Sales": "Director of Sales",
    "Engineering": "CTO",
    "Marketing": "CMO",
    "G&A": "CFO"
}

def generate_variance_email(department: str, actuals_df: pd.DataFrame, budget_df: pd.DataFrame) -> str:
    """
    Generates an email draft for variances > 10% and > $1,000.
    SAFE VERSION: No infinite loops.
    """
    
    # 1. Merge Data (Safety Check: Ensure columns exist)
    # We assume the DFs are already filtered to the current month/dept or we filter here
    merged = pd.merge(
        budget_df, 
        actuals_df, 
        on=['department', 'gl_code'], 
        suffixes=('_budget', '_actual'),
        how='inner'
    )
    
    # Filter for specific department
    dept_data = merged[merged['department'] == department].copy()
    
    if dept_data.empty:
        return "No data found for this department."

    # 2. Calculate Variances (Vectorized - Instant)
    dept_data['variance_amt'] = dept_data['amount_actual'] - dept_data['amount_budget']
    # Avoid div by zero
    dept_data['variance_pct'] = dept_data.apply(
        lambda x: (x['variance_amt'] / x['amount_budget']) if x['amount_budget'] != 0 else 0, 
        axis=1
    )

    # 3. Identify Critical Items (The "Audit" Rule)
    # Rules: Over budget by > 10% AND Amount > $1000
    critical_items = dept_data[
        (dept_data['variance_pct'] > 0.10) & 
        (dept_data['variance_amt'] > 1000)
    ]

    if critical_items.empty:
        return f"Subject: Budget Update - {department}\n\nNo significant variances detected for this period. Great job!"

    # 4. Draft the Email
    manager_name = DEPARTMENT_HEADS.get(department, "Department Head")
    
    email_body = f"Subject: ACTION REQUIRED: Budget Variance Report - {department}\n\n"
    email_body += f"Hi {manager_name},\n\n"
    email_body += "Our automated audit detected the following significant budget overages for this month:\n\n"
    
    for _, row in critical_items.iterrows():
        email_body += f"- {row['gl_code']}: Budget ${row['amount_budget']:,.2f} vs Actual ${row['amount_actual']:,.2f} "
        email_body += f"(Over by {row['variance_pct']*100:.1f}% / ${row['variance_amt']:,.2f})\n"
    
    email_body += "\nCould you please provide a brief explanation for these variances by EOD Friday?\n\n"
    email_body += "Best,\nAI FP&A Controller"

    return email_body
