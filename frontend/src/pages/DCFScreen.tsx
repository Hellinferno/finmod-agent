import { useState } from 'react';
import { apiClient } from '../api/client';
import DemoData from '../mocks/dcf-base-case.json';

export default function DCFScreen() {
    const [wacc, setWacc] = useState<number>(10.5);
    const [tgr, setTgr] = useState<number>(2.5);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [errorStatus, setErrorStatus] = useState<string | null>(null);
    const [result, setResult] = useState<any>(null);

    // Golden Path: Demo Mode Toggle
    const [isDemoMode, setIsDemoMode] = useState<boolean>(
        import.meta.env.VITE_FORCE_DEMO_MODE === 'true' ? true : false
    );

    const handleRunDCF = async () => {
        // 1. Data Validation (Empty / Error States)
        if (wacc <= tgr) {
            setErrorStatus("Validation Error: WACC must be strictly greater than Terminal Growth Rate (TGR) for the Gordon Growth Model.");
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
            setErrorStatus(err.response?.data?.message || "Failed to connect to FMVA Agent backend.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-base">
            {/* PAGE HEADER */}
            <div className="sticky top-0 z-10 bg-base/95 backdrop-blur-sm border-b border-border-subtle px-6 py-4 flex items-center justify-between">
                <div>
                    <h1 className="text-[18px] font-semibold text-txt-primary">DCF Valuation</h1>
                    <p className="text-[12px] text-txt-muted">Gordon Growth Method · Exit Multiple Method · WACC Analysis</p>
                </div>
                <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 px-3 py-1.5 rounded border border-border-subtle bg-surface cursor-pointer select-none">
                        <input
                            type="checkbox"
                            checked={isDemoMode}
                            onChange={(e) => setIsDemoMode(e.target.checked)}
                            className="accent-accent"
                        />
                        <span className="text-[12px] font-semibold text-accent">Demo Mode (Safety)</span>
                    </label>
                    <button
                        onClick={handleRunDCF}
                        disabled={isLoading}
                        className={`px-4 py-1.5 rounded text-white text-[12px] font-semibold transition-colors ${isLoading ? "bg-accent/50 cursor-not-allowed" : "bg-accent hover:bg-accent-hover"
                            }`}
                    >
                        {isLoading ? "Agent Thinking..." : "Run Valuation Engine"}
                    </button>
                </div>
            </div>

            <div className="p-6 space-y-6">
                {errorStatus && (
                    <div className="bg-neg-bg border border-neg/30 p-4 rounded-lg flex items-start gap-3">
                        <div className="text-neg shrink-0 mt-0.5">⚠️</div>
                        <div>
                            <h3 className="text-[13px] font-semibold text-neg-text">Valuation Rule Violated</h3>
                            <p className="text-[12px] text-neg-text/80">{errorStatus}</p>
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-3 gap-6">
                    {/* INPUT PORTION */}
                    <div className="col-span-1 space-y-4">
                        <div className="bg-panel rounded-lg border border-border-subtle p-5">
                            <h2 className="text-[14px] font-semibold text-txt-primary mb-4">Core Assumptions</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-[12px] font-medium text-txt-secondary mb-1">
                                        WACC (%)
                                    </label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={wacc}
                                        onChange={(e) => setWacc(parseFloat(e.target.value))}
                                        className="w-full bg-base border border-border-subtle rounded px-3 py-2 text-[13px] text-txt-primary focus:border-accent focus:ring-1 focus:ring-accent outline-none font-mono"
                                    />
                                </div>

                                <div>
                                    <label className="block text-[12px] font-medium text-txt-secondary mb-1">
                                        Terminal Growth Rate (%)
                                    </label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={tgr}
                                        onChange={(e) => setTgr(parseFloat(e.target.value))}
                                        className="w-full bg-base border border-border-subtle rounded px-3 py-2 text-[13px] text-txt-primary focus:border-accent focus:ring-1 focus:ring-accent outline-none font-mono"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* OUTPUT PORTION */}
                    <div className="col-span-2">
                        {isLoading ? (
                            <div className="bg-panel rounded-lg border border-border-subtle p-8 flex flex-col items-center justify-center min-h-[300px]">
                                <div className="w-8 h-8 rounded-full border-2 border-border-subtle border-t-accent animate-spin mb-4"></div>
                                <div className="text-[13px] font-semibold text-txt-primary">Computing Present Values</div>
                                <div className="text-[12px] text-txt-muted mt-1">Calculating Unlevered Free Cash Flows & Terminal Value...</div>

                                <div className="w-full max-w-sm mt-8 space-y-3">
                                    <div className="h-2 bg-border-subtle rounded w-full overflow-hidden">
                                        <div className="h-full bg-accent animate-pulse w-2/3"></div>
                                    </div>
                                    <div className="h-2 bg-border-subtle rounded w-5/6"></div>
                                    <div className="h-2 bg-border-subtle rounded w-4/6"></div>
                                </div>
                            </div>
                        ) : result ? (
                            <div className="bg-panel rounded-lg border border-border-subtle p-6 min-h-[300px]">
                                <div className="flex items-center justify-between mb-6 pb-4 border-b border-border-subtle">
                                    <h2 className="text-[16px] font-semibold text-txt-primary">Target Output</h2>
                                    <span className="px-2 py-0.5 rounded-full bg-pos-bg border border-pos-DEFAULT text-pos-text text-[10px] mono">
                                        {result.status.toUpperCase()}
                                    </span>
                                </div>

                                <div className="grid grid-cols-3 gap-6">
                                    <div>
                                        <div className="text-[11px] text-txt-muted uppercase tracking-wider mb-1">Implied Share Price</div>
                                        <div className="text-[28px] font-bold text-accent mono">${result.implied_share_price}</div>
                                    </div>
                                    <div>
                                        <div className="text-[11px] text-txt-muted uppercase tracking-wider mb-1">Enterprise Value</div>
                                        <div className="text-[24px] font-semibold text-txt-primary mono">${result.enterprise_value_m?.toLocaleString() || "N/A"}</div>
                                    </div>
                                    <div>
                                        <div className="text-[11px] text-txt-muted uppercase tracking-wider mb-1">Equity Value</div>
                                        <div className="text-[24px] font-semibold text-txt-primary mono">${result.equity_value_m?.toLocaleString() || "N/A"}</div>
                                    </div>
                                </div>

                                <div className="mt-8">
                                    <h3 className="text-[13px] font-semibold text-txt-primary mb-3">PV of Cash Flows (Next 5 Years)</h3>
                                    <div className="flex gap-2 h-24 items-end border-b border-l border-border-subtle p-2">
                                        {(result.pv_ufcfs || []).map((cf: number, idx: number) => (
                                            <div key={idx} className="flex-1 bg-accent/20 hover:bg-accent/40 rounded-t transition-colors relative group" style={{ height: `${(cf / 150) * 100}%` }}>
                                                <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] mono hidden group-hover:block bg-elevated border shadow p-1 rounded z-10">
                                                    ${cf}M
                                                </div>
                                            </div>
                                        ))}
                                        {/* Terminal Value Bar */}
                                        <div className="flex-1 bg-cell-output/50 hover:bg-cell-output rounded-t transition-colors relative group" style={{ height: `100%` }}>
                                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] mono hidden group-hover:block bg-elevated border shadow p-1 rounded z-10">
                                                TV: ${result.pv_terminal_value || 'N/A'}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex gap-2 px-2 mt-2 pt-1 text-[10px] text-txt-muted mono text-center">
                                        <div className="flex-1">Y1</div>
                                        <div className="flex-1">Y2</div>
                                        <div className="flex-1">Y3</div>
                                        <div className="flex-1">Y4</div>
                                        <div className="flex-1">Y5</div>
                                        <div className="flex-1">Terminal</div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-panel rounded-lg border border-border-subtle border-dashed p-8 flex flex-col items-center justify-center min-h-[300px] opacity-70">
                                <div className="text-[24px] mb-2">📊</div>
                                <div className="text-[14px] font-medium text-txt-primary">Awaiting Configuration</div>
                                <div className="text-[12px] text-txt-muted mt-1 text-center max-w-sm">
                                    Adjust the DCF assumptions in the panel on the left and click "Run Valuation Engine" to generate terminal values and cash flow implied shares.
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
