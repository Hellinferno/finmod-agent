
def generate_cfo_commentary(runway_months, profit_margin, variance_percent):
    """
    Simulates an AI Agent reasoning about the financials.
    """
    insights = []
    
    # 1. Perception (Ingest Data) & Reasoning (Analyze)
    if runway_months < 3:
        insights.append(f"⚠️ **CRITICAL:** Cash Runway is only {runway_months:.1f} months. Immediate capital injection or cost-cutting required.")
    elif runway_months > 12:
        insights.append(f"✅ **Healthy:** Strong cash position ({runway_months:.1f} months). Consider reinvesting in R&D.")
        
    if variance_percent < -10:
        insights.append(f"📉 **Budget Alert:** Spending is {abs(variance_percent)}% higher than planned. Review 'Marketing' and 'Server' costs.")
        
    if profit_margin < 0.10:
        insights.append("💡 **Strategy:** Net margins are thin (<10%). Focus on high-margin products or raise prices.")

    # 2. Action (Output)
    return "\n\n".join(insights)
