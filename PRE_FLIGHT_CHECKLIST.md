# Investor Showcase: The "Pre-Flight" Checklist

Before presenting the Financial Modeling Agent (FMVA) to investors, run through this 5-point checklist to guarantee a flawless, high-speed professional demo.

### 1. [ ] Confirm "Demo Mode" is Enabled (Safety Check)
- Ensure the `isDemoMode` toggle in the React UI is set to **TRUE** by default.
- Verify that clicking "Run DCF" or "Generate Report" returns the hardcoded JSON payload from your `/mocks` directory. This prevents live LLM/API timeouts from impacting your pitch.

### 2. [ ] Verify Empty States and Validation Barriers
- Start with a "clean slate" where no data is loaded yet. Confirm the screen displays the professional "Awaiting Valuation Configuration" visual, not a broken table or blank abyss.
- Intentionally enter an invalid parameter (e.g., WACC < TGR) and verify that the UI surfaces a clean red error banner rather than freezing or crashing.

### 3. [ ] Check the Loading Skeletons and UX Polish (Perceived Latency)
- When simulating an API request, verify that the `animate-pulse` components (loading skeletons) appear immediately.
- Ensure the button state changes to `disabled` and reads "FMVA Agent is Thinking..." to provide the investor with immediate, satisfying visual feedback.

### 4. [ ] Boot and Health-Check the Backend Stack
- In Terminal 1, ensure the FastAPI server is running (`uvicorn api.main:app --reload`).
- Ping the health check by opening `http://localhost:8000/api/health` in your browser. It MUST return `{"status": "ok"}`.
- If pitching to investors with live data instead of mock data, ensure the `.env` variables containing your LLM/database keys are loaded and strictly pointed to `production` variants.

### 5. [ ] Network Independence (Local Verification)
- **The Ultimate Test:** Briefly disconnect from the Wi-Fi.
- Click through the app in Demo Mode. Assuming the Vite Dev Server and FastAPI server are running on `localhost`, the entire presentation should proceed flawlessly with zero internet connection. (If using cloud fonts like Google Fonts, ensure they are cached, or UI will look degraded offline).
