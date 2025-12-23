
def generate_cfo_insights(metrics):
    """
    Analyzes financial metrics and generates a 'CFO Commentary'.
    Input: metrics (dict) -> {'runway': 5.2, 'burn': -2000, 'growth': 0.15}
    """
    runway = metrics.get('runway', 0)
    burn = metrics.get('burn', 0)
    growth = metrics.get('growth', 0)
    
    insights = []
    
    # 1. RUNWAY ANALYSIS (Survival Logic)
    if runway < 3:
        insights.append(f"🔴 **CRITICAL DANGER:** Cash runway is only {runway:.1f} months. You must cut costs or raise capital immediately.")
    elif runway < 6:
        insights.append(f"⚠️ **WARNING:** Cash runway is {runway:.1f} months. Start fundraising conversations now.")
    else:
        insights.append(f"✅ **HEALTHY:** Strong cash position ({runway:.1f} months). You have room to invest in growth.")

    # 2. BURN RATE ANALYSIS (Efficiency Logic)
    if burn > 50000 and growth < 0.10:
        insights.append(f"📉 **EFFICIENCY ALERT:** You are burning ${burn:,.0f}/mo but only growing {growth*100:.1f}%. Review marketing spend.")
    elif growth > 0.20:
        insights.append(f"🚀 **HIGH GROWTH:** Growing at {growth*100:.1f}% monthly. Current burn rate is justified.")

    # 3. STRATEGIC ADVICE
    if runway > 12 and growth < 0.05:
        insights.append("💡 **CFO ADVICE:** You are too conservative. Use your cash pile to hire sales staff or acquire a competitor.")

    if not insights:
        insights.append("ℹ️ **STATUS:** Financials look stable. No immediate alerts.")

    return "\n\n".join(insights)
