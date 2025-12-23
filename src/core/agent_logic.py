
import google.generativeai as genai
import os

# Configure the AI
# For production, use: os.getenv("GEMINI_API_KEY")
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_cfo_insights(metrics):
    """
    Sends financial metrics to Gemini Pro and gets a strategic CFO analysis.
    """
    try:
        # 1. Define the Persona and Data
        prompt = f"""
        Act as a veteran CFO for a startup. Analyze these monthly metrics:
        - Cash Runway: {metrics.get('runway')} months
        - Monthly Burn: ${metrics.get('burn'):,.0f}
        - Month-over-Month Growth: {metrics.get('growth', 0)*100:.1f}%

        Task:
        1. Give a 1-sentence assessment of financial health (Critical/Healthy/Stable).
        2. Provide 2 specific, actionable strategic recommendations based on these numbers.
        3. Use professional but urgent tone if runway is low.
        4. Keep it under 100 words.
        """

        # 2. Call the Model
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)

        # 3. Return the AI's words
        return response.text

    except Exception as e:
        # Fallback if internet/API fails
        return f"⚠️ AI Analysis Unavailable: {str(e)}. (Check API Key)"
