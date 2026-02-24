export default function IngestionScreen() {
    return (
        <div className="flex-1 overflow-y-auto bg-base h-full">
            {/* PAGE HEADER */}
            <div className="sticky top-0 z-10 bg-base/95 backdrop-blur-sm border-b border-border-subtle px-6 py-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-[18px] font-semibold text-txt-primary">Data Ingestion</h1>
                        <p className="text-[12px] text-txt-muted">Upload financial statements · Income Statement + Balance Sheet + Cash Flow</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="px-3 py-1.5 rounded bg-surface border border-border-default text-[12px] text-txt-secondary hover:bg-elevated transition-colors">
                            Load Sample Data
                        </button>
                        <button className="px-4 py-1.5 rounded bg-accent text-white text-[12px] font-semibold hover:bg-accent-hover transition-colors disabled:opacity-40">
                            Process & Normalize →
                        </button>
                    </div>
                </div>
            </div>

            <div className="px-6 py-5 space-y-5">
                {/* Company Metadata Row */}
                <div className="bg-panel rounded-lg border border-border-subtle p-4">
                    <div className="text-[13px] font-semibold text-txt-primary mb-3">Company Metadata</div>
                    <div className="grid grid-cols-4 gap-4">
                        <div>
                            <label className="block text-[10px] text-txt-muted uppercase tracking-widest mb-1.5">Company Name *</label>
                            <input type="text" defaultValue="TechCorp Inc."
                                className="w-full bg-surface border border-border-default rounded px-3 py-2 text-[13px] text-txt-primary focus:outline-none focus:border-accent mono transition-colors" />
                        </div>
                        <div>
                            <label className="block text-[10px] text-txt-muted uppercase tracking-widest mb-1.5">Ticker Symbol</label>
                            <input type="text" defaultValue="TECH"
                                className="w-full bg-surface border border-border-default rounded px-3 py-2 text-[13px] text-cell-input focus:outline-none focus:border-accent mono transition-colors uppercase" />
                        </div>
                        <div>
                            <label className="block text-[10px] text-txt-muted uppercase tracking-widest mb-1.5">Currency Units</label>
                            <select
                                className="w-full bg-surface border border-border-default rounded px-3 py-2 text-[13px] text-txt-primary focus:outline-none focus:border-accent mono transition-colors">
                                <option>USD Millions ($M)</option>
                                <option>USD Thousands ($K)</option>
                                <option>USD Actuals</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-[10px] text-txt-muted uppercase tracking-widest mb-1.5">Fiscal Year End</label>
                            <select
                                className="w-full bg-surface border border-border-default rounded px-3 py-2 text-[13px] text-txt-primary focus:outline-none focus:border-accent mono transition-colors">
                                <option>December (Calendar)</option>
                                <option>June</option>
                                <option>March</option>
                                <option>September</option>
                            </select>
                        </div>
                    </div>
                    <div className="grid grid-cols-4 gap-4 mt-4">
                        <div>
                            <label className="block text-[10px] text-txt-muted uppercase tracking-widest mb-1.5">Industry</label>
                            <input type="text" defaultValue="SaaS / Enterprise Software"
                                className="w-full bg-surface border border-border-default rounded px-3 py-2 text-[13px] text-txt-primary focus:outline-none focus:border-accent transition-colors" />
                        </div>
                        <div>
                            <label className="block text-[10px] text-txt-muted uppercase tracking-widest mb-1.5">Diluted Shares (M)</label>
                            <input type="text" defaultValue="100.0"
                                className="w-full bg-surface border border-border-default rounded px-3 py-2 text-[13px] text-cell-input focus:outline-none focus:border-accent mono transition-colors" />
                        </div>
                        <div>
                            <label className="block text-[10px] text-txt-muted uppercase tracking-widest mb-1.5">Current Share Price ($)</label>
                            <input type="text" defaultValue="8.50"
                                className="w-full bg-surface border border-border-default rounded px-3 py-2 text-[13px] text-cell-input focus:outline-none focus:border-accent mono transition-colors" />
                        </div>
                        <div>
                            <label className="block text-[10px] text-txt-muted uppercase tracking-widest mb-1.5">Accounting Standard</label>
                            <select
                                className="w-full bg-surface border border-border-default rounded px-3 py-2 text-[13px] text-txt-primary focus:outline-none focus:border-accent mono transition-colors">
                                <option>GAAP (US)</option>
                                <option>IFRS</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* File Upload Zone */}
                <div className="grid grid-cols-3 gap-4">

                    {/* Income Statement Upload */}
                    <div
                        className="bg-panel rounded-lg border-2 border-dashed border-border-default hover:border-accent transition-colors cursor-pointer group">
                        <div className="p-6 text-center">
                            <div
                                className="w-12 h-12 rounded-lg bg-surface border border-border-subtle flex items-center justify-center mx-auto mb-3 group-hover:border-accent/50 transition-colors">
                                <svg className="w-6 h-6 text-txt-muted group-hover:text-accent transition-colors" fill="none"
                                    stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5"
                                        d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                                </svg>
                            </div>
                            <div className="text-[13px] font-semibold text-txt-primary mb-1">Income Statement</div>
                            <div className="text-[11px] text-txt-muted mb-3">Revenue · EBITDA · Net Income<br />Min. 3 historical years</div>
                            <div
                                className="px-3 py-1.5 rounded bg-surface border border-border-default text-[11px] text-txt-secondary inline-block group-hover:bg-elevated transition-colors">
                                Drop file or click to browse
                            </div>
                        </div>
                    </div>

                    {/* Balance Sheet Upload — Uploaded State */}
                    <div className="bg-panel rounded-lg border-2 border-pos-DEFAULT bg-pos-bg/20">
                        <div className="p-6 text-center">
                            <div
                                className="w-12 h-12 rounded-lg bg-pos-bg border border-pos-DEFAULT flex items-center justify-center mx-auto mb-3">
                                <svg className="w-6 h-6 text-pos-DEFAULT" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                                </svg>
                            </div>
                            <div className="text-[13px] font-semibold text-txt-primary mb-0.5">Balance Sheet</div>
                            <div className="mono text-[11px] text-pos-text mb-1">techcorp_bs.csv</div>
                            <div className="text-[10px] text-txt-muted mb-3">3 periods · 24 line items · USD $M</div>
                            <div className="flex items-center justify-center gap-2">
                                <span
                                    className="px-2 py-0.5 rounded-full bg-pos-bg border border-pos-DEFAULT text-pos-text text-[10px] font-medium">✓
                                    BS BALANCED</span>
                                <button className="text-[10px] text-txt-muted hover:text-neg-text transition-colors">Remove</button>
                            </div>
                        </div>
                    </div>

                    {/* Cash Flow Upload — Error State */}
                    <div
                        className="bg-panel rounded-lg border-2 border-dashed border-border-default hover:border-accent transition-colors cursor-pointer group">
                        <div className="p-6 text-center">
                            <div
                                className="w-12 h-12 rounded-lg bg-surface border border-border-subtle flex items-center justify-center mx-auto mb-3 group-hover:border-accent/50 transition-colors">
                                <svg className="w-6 h-6 text-txt-muted group-hover:text-accent transition-colors" fill="none"
                                    stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5"
                                        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div className="text-[13px] font-semibold text-txt-primary mb-1">Cash Flow Statement</div>
                            <div className="text-[11px] text-txt-muted mb-3">Operating · Investing · Financing<br />Required for UFCF calculation</div>
                            <div
                                className="px-3 py-1.5 rounded bg-surface border border-border-default text-[11px] text-txt-secondary inline-block group-hover:bg-elevated transition-colors">
                                Drop file or click to browse
                            </div>
                        </div>
                    </div>
                </div>

                {/* Normalization Preview Table */}
                <div className="bg-panel rounded-lg border border-border-subtle overflow-hidden">
                    <div className="px-4 py-3 border-b border-border-subtle flex items-center justify-between">
                        <div>
                            <div className="text-[13px] font-semibold text-txt-primary">Normalization Preview</div>
                            <div className="text-[11px] text-txt-muted mt-0.5">Balance Sheet · Auto-mapped 22/24 fields · <span
                                className="text-warn-DEFAULT">2 require review</span></div>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="flex items-center gap-1.5 text-[10px]">
                                <span className="w-2 h-2 rounded-full bg-pos-DEFAULT"></span><span className="text-txt-muted">Mapped</span>
                                <span className="w-2 h-2 rounded-full bg-warn-DEFAULT ml-2"></span><span className="text-txt-muted">Review Required</span>
                                <span className="w-2 h-2 rounded-full bg-neg-DEFAULT ml-2"></span><span className="text-txt-muted">Error</span>
                            </div>
                        </div>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-[11px]">
                            <thead>
                                <tr className="bg-surface border-b border-border-subtle">
                                    <th className="text-left px-4 py-2 text-txt-muted font-medium">Raw Field Name</th>
                                    <th className="text-left px-4 py-2 text-txt-muted font-medium">→ Canonical Name</th>
                                    <th className="text-left px-4 py-2 text-txt-muted font-medium">Status</th>
                                    <th className="text-right px-4 py-2 text-txt-muted font-medium">FY2021</th>
                                    <th className="text-right px-4 py-2 text-txt-muted font-medium">FY2022</th>
                                    <th className="text-right px-4 py-2 text-txt-muted font-medium">FY2023</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr className="border-b border-border-subtle/50 hover:bg-surface/40 transition-colors">
                                    <td className="px-4 py-2 mono text-txt-secondary">Total Revenue</td>
                                    <td className="px-4 py-2 mono text-cell-input">total_revenue</td>
                                    <td className="px-4 py-2"><span
                                        className="px-2 py-0.5 rounded-full bg-pos-bg border border-pos-DEFAULT text-pos-text text-[9px]">✓ Auto-mapped</span></td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">413.2</td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">454.5</td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">500.0</td>
                                </tr>
                                <tr className="border-b border-border-subtle/50 hover:bg-surface/40 transition-colors">
                                    <td className="px-4 py-2 mono text-txt-secondary">Gross Profit</td>
                                    <td className="px-4 py-2 mono text-cell-input">gross_profit</td>
                                    <td className="px-4 py-2"><span
                                        className="px-2 py-0.5 rounded-full bg-pos-bg border border-pos-DEFAULT text-pos-text text-[9px]">✓ Auto-mapped</span></td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">289.2</td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">318.2</td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">350.0</td>
                                </tr>
                                <tr className="border-b border-border-subtle/50 bg-warn-bg/30">
                                    <td className="px-4 py-2 mono text-warn-DEFAULT">Operating EBITDA</td>
                                    <td className="px-4 py-2">
                                        <select
                                            className="bg-surface border border-warn-DEFAULT rounded px-2 py-1 mono text-[10px] text-warn-DEFAULT focus:outline-none">
                                            <option>ebitda</option>
                                            <option>ebit</option>
                                            <option>gross_profit</option>
                                        </select>
                                    </td>
                                    <td className="px-4 py-2"><span
                                        className="px-2 py-0.5 rounded-full bg-warn-bg border border-warn-DEFAULT text-warn-DEFAULT text-[9px]">⚠ Review</span></td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">99.2</td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">109.1</td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">125.0</td>
                                </tr>
                                <tr className="border-b border-border-subtle/50 bg-warn-bg/30">
                                    <td className="px-4 py-2 mono text-warn-DEFAULT">Depr. & Amort.</td>
                                    <td className="px-4 py-2">
                                        <select
                                            className="bg-surface border border-warn-DEFAULT rounded px-2 py-1 mono text-[10px] text-warn-DEFAULT focus:outline-none">
                                            <option>depreciation_and_amortization</option>
                                            <option>da</option>
                                            <option>capex</option>
                                        </select>
                                    </td>
                                    <td className="px-4 py-2"><span
                                        className="px-2 py-0.5 rounded-full bg-warn-bg border border-warn-DEFAULT text-warn-DEFAULT text-[9px]">⚠ Review</span></td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">18.5</td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">22.0</td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">25.0</td>
                                </tr>
                                <tr className="border-b border-border-subtle/50 hover:bg-surface/40 transition-colors">
                                    <td className="px-4 py-2 mono text-txt-secondary">Net Income</td>
                                    <td className="px-4 py-2 mono text-cell-input">net_income</td>
                                    <td className="px-4 py-2"><span
                                        className="px-2 py-0.5 rounded-full bg-pos-bg border border-pos-DEFAULT text-pos-text text-[9px]">✓ Auto-mapped</span></td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">57.3</td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">62.9</td>
                                    <td className="px-4 py-2 font-mono text-[12px] text-right text-cell-formula">71.0</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Balance Sheet Check Result */}
                <div className="bg-panel rounded-lg border border-border-subtle overflow-hidden">
                    <div className="px-4 py-3 border-b border-border-subtle flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="text-[13px] font-semibold text-txt-primary">Balance Sheet Integrity Check</div>
                            <span
                                className="px-2 py-0.5 rounded-full bg-pos-bg border border-pos-DEFAULT text-pos-text text-[10px] font-medium">ALL PERIODS PASS</span>
                        </div>
                        <span className="text-[11px] text-txt-muted mono">δ tolerance: ±$0.01M</span>
                    </div>
                    <div className="p-4">
                        <div className="grid grid-cols-3 gap-3">
                            <div className="p-3 rounded bg-surface border border-border-subtle">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-[11px] font-semibold text-txt-secondary">FY2021</span>
                                    <span
                                        className="px-1.5 py-0.5 rounded-full bg-pos-bg border border-pos-DEFAULT text-pos-text text-[9px]">✓ PASS</span>
                                </div>
                                <div className="space-y-1 text-[11px]">
                                    <div className="flex justify-between"><span className="text-txt-muted">Total Assets</span><span
                                        className="mono text-cell-formula">$1,240.5M</span></div>
                                    <div className="flex justify-between"><span className="text-txt-muted">Liabilities + Equity</span><span
                                        className="mono text-cell-formula">$1,240.5M</span></div>
                                    <div className="flex justify-between border-t border-border-subtle pt-1"><span
                                        className="text-txt-muted">Delta</span><span className="mono text-pos-DEFAULT">$0.00M</span></div>
                                </div>
                            </div>
                            <div className="p-3 rounded bg-surface border border-border-subtle">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-[11px] font-semibold text-txt-secondary">FY2022</span>
                                    <span
                                        className="px-1.5 py-0.5 rounded-full bg-pos-bg border border-pos-DEFAULT text-pos-text text-[9px]">✓ PASS</span>
                                </div>
                                <div className="space-y-1 text-[11px]">
                                    <div className="flex justify-between"><span className="text-txt-muted">Total Assets</span><span
                                        className="mono text-cell-formula">$1,380.0M</span></div>
                                    <div className="flex justify-between"><span className="text-txt-muted">Liabilities + Equity</span><span
                                        className="mono text-cell-formula">$1,380.0M</span></div>
                                    <div className="flex justify-between border-t border-border-subtle pt-1"><span
                                        className="text-txt-muted">Delta</span><span className="mono text-pos-DEFAULT">$0.00M</span></div>
                                </div>
                            </div>
                            <div className="p-3 rounded bg-surface border border-border-subtle">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-[11px] font-semibold text-txt-secondary">FY2023</span>
                                    <span
                                        className="px-1.5 py-0.5 rounded-full bg-pos-bg border border-pos-DEFAULT text-pos-text text-[9px]">✓ PASS</span>
                                </div>
                                <div className="space-y-1 text-[11px]">
                                    <div className="flex justify-between"><span className="text-txt-muted">Total Assets</span><span
                                        className="mono text-cell-formula">$1,500.0M</span></div>
                                    <div className="flex justify-between"><span className="text-txt-muted">Liabilities + Equity</span><span
                                        className="mono text-cell-formula">$1,500.0M</span></div>
                                    <div className="flex justify-between border-t border-border-subtle pt-1"><span
                                        className="text-txt-muted">Delta</span><span className="mono text-pos-DEFAULT">$0.00M</span></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
