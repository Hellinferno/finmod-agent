# FMVA Step-by-Step Integration Guide

This guide outlines exactly how the UI connects to the Python `fmva` backend to ensure a zero-latency, production-ready feel for the investor showcase.

## 1. Project Restructuring (The "Plumbing")
We are migrating the raw 10 HTML templates from the `UI/` folder into a Vite + React application. This allows for component reuse, state management, and the optimistic UI updates required.

**Modified Files / Architecture Link:**
- **Frontend App**: `frontend/src/`
- **Backend API**: `fmva/api/`

---

## 2. Setting Up the Vite Request Client (Axios)

Create `frontend/src/api/client.ts` to manage all external calls to the Python backend.

```typescript
import axios from 'axios';

// The URL to the local FastAPI server
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds for LLM generations
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error("API Error: ", error.response?.data?.message || error.message);
    return Promise.reject(error);
  }
);
```

---

## 3. Mapping the HTML to React (Example: `DCFScreen.tsx`)

Convert action components (like "Run DCF", "Calculate WACC") into React state components that utilize API Handlers, Loading States, and "Demo Mode".

```tsx
import React, { useState } from 'react';
import { apiClient } from '../api/client';
import DemoData from '../mocks/dcf-base-case.json';

export default function DCFScreen() {
  const [wacc, setWacc] = useState(10.5);
  const [tgr, setTgr] = useState(2.5);
  const [isLoading, setIsLoading] = useState(false);
  const [errorStatus, setErrorStatus] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  
  // Golden Path: Demo Mode Toggle
  const [isDemoMode, setIsDemoMode] = useState(true);

  const handleRunDCF = async () => {
    // 1. Data Validation (Empty / Error States)
    if (wacc <= tgr) {
      setErrorStatus("WACC must be strictly greater than Terminal Growth Rate.");
      return;
    }
    setErrorStatus(null);
    setIsLoading(true);

    try {
      if (isDemoMode) {
        // Hardcoded "Safety" Data — Ensures flawless demo
        await new Promise(resolve => setTimeout(resolve, 800)); // simulate slight network delay 
        setResult(DemoData);
      } else {
        // Live Mode Data flow to FastAPI backend
        const res = await apiClient.post('/api/dcf/run', {
            company_id: 'TECH',
            wacc_pct: wacc,
            tgr_pct: tgr
        });
        setResult(res);
      }
    } catch (err: any) {
       setErrorStatus(err.response?.data?.message || "Failed to connect to FMVA Agent.");
    } finally {
       setIsLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between">
        <h1 className="text-xl font-bold text-txt-primary">DCF Valuation</h1>
        <label className="flex items-center space-x-2">
            <input type="checkbox" checked={isDemoMode} onChange={(e) => setIsDemoMode(e.target.checked)} />
            <span className="text-sm font-semibold text-accent">Demo Mode (Safety)</span>
        </label>
      </div>

      {errorStatus && (
        <div className="bg-neg-bg border border-neg text-neg-text p-3 my-4 rounded">
            {errorStatus}
        </div>
      )}

      {/* Optimistic UI Updates / Loading Skeletons */}
      {isLoading ? (
        <div className="animate-pulse flex space-x-4 mt-8">
          <div className="flex-1 space-y-4 py-1">
            <div className="h-4 bg-border-subtle rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-border-subtle rounded"></div>
              <div className="h-4 bg-border-subtle rounded w-5/6"></div>
            </div>
          </div>
        </div>
      ) : result ? (
        <div className="mt-8 border p-4 bg-pos-bg text-pos-text rounded">
            Enterprise Value: ${result.enterprise_value_m}M
        </div>
      ) : (
        <div className="mt-8">
            <p className="text-txt-muted">Awaiting Valuation Configuration...</p>
        </div>
      )}

      <button 
        onClick={handleRunDCF}
        disabled={isLoading}
        className="mt-6 px-4 py-2 bg-accent text-white rounded font-bold hover:bg-accent-hover disabled:opacity-50"
      >
         {isLoading ? "FMVA Agent is Thinking..." : "Run DCF"}
      </button>
    </div>
  );
}
```

---

## 4. Run the Full Stack Locally

To test the integration seamlessly, open two terminal windows.

**Terminal 1: Start the FastAPI Backend**
```bash
cd d:/finmod-agent/fmva
# If not installed, pip install fastapi uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
*The backend is now listening at `http://localhost:8000`*

**Terminal 2: Start the Vite Frontend**
```bash
cd d:/finmod-agent/frontend
# If newly initialized, run npm install
npm run dev
```
*The UI is now accessible at `http://localhost:5173`*
