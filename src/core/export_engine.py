from fpdf import FPDF
import pandas as pd
import tempfile
import os
import plotly.io as pio
import plotly.graph_objects as go
from datetime import datetime

class BoardBriefGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'AI FINANCIAL AGENT', 0, 0, 'L')
        self.cell(0, 5, datetime.now().strftime('%Y-%m-%d'), 0, 0, 'R')
        self.ln(10) # Line break

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def generate_report(self, forecast_dates: list, forecast_values: list, lower: list, upper: list, fig_dict: dict = None) -> bytes:
        """
        Generates PDF report.
        Returns PDF bytes.
        """
        self.add_page()
        
        # 1. Title
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Executive Financial Forecast', 0, 1, 'C')
        self.ln(5)
        
        # 2. Executive Summary
        self.set_font('Arial', '', 12)
        
        # Calculate Stats
        start_val = forecast_values[0] if forecast_values else 0
        end_val = forecast_values[-1] if forecast_values else 0
        if start_val != 0:
            growth = ((end_val - start_val) / start_val) * 100
        else:
            growth = 0
            
        direction = "Growth" if growth >= 0 else "Decline"
        low_bound = lower[-1] if lower else 0
        high_bound = upper[-1] if upper else 0
        
        summary = (
            f"The AI model predicts a {direction} of {abs(growth):.1f}% over the forecast horizon. "
            f"Revenue is expected to move from ${start_val:,.2f} to ${end_val:,.2f}. "
            f"The 95% confidence interval suggests a range between ${low_bound:,.2f} and ${high_bound:,.2f} "
            f"by the end of the period."
        )
        
        self.multi_cell(0, 10, summary)
        self.ln(10)
        
        # 3. Chart Embedding
        if fig_dict:
            try:
                # Convert dict to Figure
                fig = go.Figure(fig_dict)
                # Update layout for print
                fig.update_layout(template="plotly_white", width=800, height=400, title="")
                
                # Write to temp image
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    # Use kaleido engine
                    # Note: pio.write_image requires kaleido installed
                    # Handling potential static export issues in some envs
                    # We assume Kaleido is present per requirements.
                    fig.write_image(tmp.name, engine="kaleido", scale=2)
                    tmp_path = tmp.name
                
                self.image(tmp_path, x=10, w=190)
                self.ln(5)
                
                # Clean up
                try:
                    os.remove(tmp_path)
                except:
                    pass
            except Exception as e:
                self.set_font('Arial', 'I', 10)
                self.cell(0, 10, f"[Chart Generation Error: {str(e)}]", 0, 1)
                self.ln(5)

        # 4. Data Table (First 6-12 months)
        self.ln(5)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Forecast Data (Next 12 Periods)', 0, 1)
        
        # Header
        self.set_font('Arial', 'B', 10)
        col_w = 40
        self.cell(col_w, 10, 'Date', 1)
        self.cell(col_w, 10, 'Revenue ($)', 1)
        self.cell(col_w, 10, 'Growth (%)', 1)
        self.ln()
        
        # Rows
        self.set_font('Arial', '', 10)
        
        limit = min(len(forecast_dates), 12)
        prev_val = start_val # Approx
        
        for i in range(limit):
            val = forecast_values[i]
            date_str = str(forecast_dates[i])
            
            # Month-over-Month growth
            if i > 0:
                mom = ((val - forecast_values[i-1]) / forecast_values[i-1]) * 100
            else:
                mom = 0.0 # First period
            
            self.cell(col_w, 10, date_str, 1)
            self.cell(col_w, 10, f"{val:,.2f}", 1)
            self.cell(col_w, 10, f"{mom:+.1f}%", 1)
            self.ln()
            
        # Output as bytes
        # fpdf output(dest='S') returns a string (latin-1). convert to bytes.
        # Ideally use output to a temp file and read bytes for safety with binary images, 
        # but output(dest='S').encode('latin-1') works for simple cases.
        # Robust way:
        
        return self.output(dest='S').encode('latin-1')
