import { useState } from 'react';

export default function AssumptionsScreen() {
    const [waccPct, setWaccPct] = useState<number>(10.0);
    const [tgrPct, setTgrPct] = useState<number>(2.5);

    const hasValidInputs = Number.isFinite(waccPct) && Number.isFinite(tgrPct);
    const isGordonValid = hasValidInputs && waccPct > tgrPct;

    return (
        <div className="flex-1 flex flex-col h-full bg-base">
            <header className="shrink-0 h-14 bg-panel border-b border-border-subtle flex items-center px-4 gap-3 sticky top-0 z-10 w-full">
                <div className="flex items-center gap-2">
                    <span className="text-[13px] text-txt-secondary">Assumption Engine</span>
                </div>
                <div className="ml-auto flex items-center gap-2">
                    <button className="px-3 py-1.5 rounded bg-surface border border-border-default text-[12px] text-txt-secondary hover:bg-elevated transition-colors">
                        Save Assumptions
                    </button>
                    <button className="px-4 py-1.5 rounded bg-accent text-white text-[12px] font-semibold hover:bg-accent-hover transition-colors">
                        Apply and Recalculate
                    </button>
                </div>
            </header>

            <div className="flex flex-1 overflow-hidden">
                <aside className="w-[240px] shrink-0 bg-panel border-r border-border-subtle h-full pt-4 flex flex-col">
                    <div className="px-4 mb-4 flex-1">
                        <div className="text-[10px] text-txt-muted uppercase tracking-widest font-medium mb-2">Scenario Manager</div>
                        <div className="space-y-1.5">
                            <button className="w-full flex items-center justify-between px-3 py-2.5 rounded bg-surface border border-border-subtle hover:bg-elevated transition-colors">
                                <div className="flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-neg-DEFAULT"></span>
                                    <span className="text-[12px] text-txt-secondary">Bear Case</span>
                                </div>
                                <span className="mono text-[10px] text-txt-muted">Saved</span>
                            </button>
                            <button className="w-full flex items-center justify-between px-3 py-2.5 rounded bg-accent-subtle border border-accent transition-colors">
                                <div className="flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
                                    <span className="text-[12px] text-accent font-semibold">Base Case</span>
                                </div>
                                <span className="mono text-[10px] text-accent">Active</span>
                            </button>
                            <button className="w-full flex items-center justify-between px-3 py-2.5 rounded bg-surface border border-border-subtle hover:bg-elevated transition-colors">
                                <div className="flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-pos-DEFAULT"></span>
                                    <span className="text-[12px] text-txt-secondary">Bull Case</span>
                                </div>
                                <span className="mono text-[10px] text-txt-muted">Saved</span>
                            </button>
                            <button className="w-full flex items-center justify-between px-3 py-2.5 rounded bg-surface border border-dashed border-border-default hover:bg-elevated transition-colors">
                                <div className="flex items-center gap-2">
                                    <span className="text-txt-muted text-[12px]">+</span>
                                    <span className="text-[12px] text-txt-muted">New Scenario</span>
                                </div>
                            </button>
                        </div>
                    </div>

                    <div className="px-4 py-3 border-t border-border-subtle">
                        <div className="text-[10px] text-txt-muted uppercase tracking-widest font-medium mb-2">Quick Summary</div>
                        <div className="space-y-1.5 text-[11px]">
                            <div className="flex justify-between"><span className="text-txt-muted">Implied EV</span><span className="mono text-cell-output">$1,102M</span></div>
                            <div className="flex justify-between"><span className="text-txt-muted">Share Price</span><span className="mono text-accent">$9.52</span></div>
                            <div className="flex justify-between"><span className="text-txt-muted">Rev CAGR (5yr)</span><span className="mono text-cell-input">9.2%</span></div>
                            <div className="flex justify-between"><span className="text-txt-muted">Final EBITDA</span><span className="mono text-cell-formula">25.0%</span></div>
                        </div>
                    </div>
                </aside>

                <main className="flex-1 p-6 space-y-5 overflow-y-auto">
                    <div>
                        <h1 className="text-[18px] font-semibold text-txt-primary">Assumption Engine</h1>
                        <p className="text-[12px] text-txt-muted mt-1">All changes propagate instantly to DCF - Projections - Sensitivity</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-panel rounded-lg border border-border-subtle p-4">
                            <div className="text-[13px] font-semibold text-txt-primary mb-3">Revenue Growth</div>
                            <div className="space-y-4">
                                <LabeledPercentInput label="Stage 1 Growth (Years 1-5)" value="10.0" />
                                <input type="range" min="-50" max="100" defaultValue="10" className="w-full accent-accent" />
                                <LabeledPercentInput label="Stage 2 Growth (Years 6-10)" value="5.0" />
                                <input type="range" min="-50" max="50" defaultValue="5" className="w-full accent-accent" />
                            </div>
                        </div>

                        <div className="bg-panel rounded-lg border border-border-subtle p-4">
                            <div className="text-[13px] font-semibold text-txt-primary mb-3">Margin Assumptions</div>
                            <div className="space-y-4">
                                <LabeledPercentInput label="EBITDA Margin" value="25.0" />
                                <input type="range" min="0" max="80" defaultValue="25" className="w-full accent-accent" />
                                <LabeledPercentInput label="D&A as % of Revenue" value="5.0" />
                                <input type="range" min="0" max="20" defaultValue="5" className="w-full accent-accent" />
                            </div>
                        </div>

                        <div className="bg-panel rounded-lg border border-border-subtle p-4">
                            <div className="text-[13px] font-semibold text-txt-primary mb-3">CapEx and Working Capital</div>
                            <div className="space-y-4">
                                <LabeledPercentInput label="CapEx as % of Revenue" value="6.0" />
                                <input type="range" min="0" max="30" defaultValue="6" className="w-full accent-accent" />
                                <LabeledPercentInput label="Delta NWC as % of Revenue" value="8.0" />
                                <input type="range" min="-10" max="20" defaultValue="8" className="w-full accent-accent" />
                                <LabeledPercentInput label="Effective Tax Rate" value="21.0" />
                                <input type="range" min="0" max="40" defaultValue="21" className="w-full accent-accent" />
                            </div>
                        </div>

                        <div className="bg-panel rounded-lg border border-border-subtle p-4">
                            <div className="text-[13px] font-semibold text-txt-primary mb-3">DCF Parameters</div>
                            <div className="space-y-4">
                                <div>
                                    <div className="flex justify-between items-center mb-2">
                                        <label className="text-[11px] text-txt-secondary">WACC</label>
                                        <div className="flex items-center gap-1.5">
                                            <input
                                                type="number"
                                                step="0.1"
                                                value={waccPct}
                                                onChange={(e) => setWaccPct(Number.parseFloat(e.target.value))}
                                                className="w-16 bg-surface border border-border-default rounded px-2 py-1 mono text-[12px] text-cell-input text-right focus:outline-none focus:border-accent"
                                            />
                                            <span className="text-[11px] text-txt-muted">%</span>
                                        </div>
                                    </div>
                                    <input
                                        type="range"
                                        min="5"
                                        max="25"
                                        step="0.1"
                                        value={Number.isFinite(waccPct) ? waccPct : 10}
                                        onChange={(e) => setWaccPct(Number.parseFloat(e.target.value))}
                                        className="w-full accent-accent"
                                    />
                                </div>

                                <div>
                                    <div className="flex justify-between items-center mb-2">
                                        <div>
                                            <label className="text-[11px] text-txt-secondary">Terminal Growth Rate</label>
                                            <div className="text-[10px] text-txt-muted">Must be lower than WACC</div>
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                            <input
                                                type="number"
                                                step="0.1"
                                                value={tgrPct}
                                                onChange={(e) => setTgrPct(Number.parseFloat(e.target.value))}
                                                className="w-16 bg-surface border border-border-default rounded px-2 py-1 mono text-[12px] text-cell-input text-right focus:outline-none focus:border-accent"
                                            />
                                            <span className="text-[11px] text-txt-muted">%</span>
                                        </div>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="5"
                                        step="0.1"
                                        value={Number.isFinite(tgrPct) ? tgrPct : 2.5}
                                        onChange={(e) => setTgrPct(Number.parseFloat(e.target.value))}
                                        className="w-full accent-accent"
                                    />
                                </div>

                                <div>
                                    <div className="flex justify-between items-center mb-2">
                                        <label className="text-[11px] text-txt-secondary">Exit Multiple (EV/EBITDA)</label>
                                        <div className="flex items-center gap-1.5">
                                            <input
                                                type="number"
                                                defaultValue="12.0"
                                                className="w-16 bg-surface border border-border-default rounded px-2 py-1 mono text-[12px] text-cell-input text-right focus:outline-none focus:border-accent"
                                            />
                                            <span className="text-[11px] text-txt-muted">x</span>
                                        </div>
                                    </div>
                                    <input type="range" min="4" max="25" defaultValue="12" className="w-full accent-accent" />
                                </div>

                                <div className={`p-2.5 rounded border flex items-center gap-2 ${isGordonValid ? 'bg-pos-bg border-pos-DEFAULT' : 'bg-neg-bg border-neg/40'}`}>
                                    <svg className={`w-3.5 h-3.5 shrink-0 ${isGordonValid ? 'text-pos-DEFAULT' : 'text-neg'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <span className={`text-[10px] mono ${isGordonValid ? 'text-pos-text' : 'text-neg-text'}`}>
                                        {hasValidInputs
                                            ? isGordonValid
                                                ? `WACC (${waccPct.toFixed(1)}%) > TGR (${tgrPct.toFixed(1)}%) - Gordon Growth valid`
                                                : `Invalid input: WACC (${waccPct.toFixed(1)}%) must be greater than TGR (${tgrPct.toFixed(1)}%)`
                                            : 'Enter valid numeric WACC and TGR values'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

function LabeledPercentInput({ label, value }: { label: string; value: string }) {
    return (
        <div>
            <div className="flex justify-between items-center mb-2">
                <label className="text-[11px] text-txt-secondary">{label}</label>
                <div className="flex items-center gap-1.5">
                    <input
                        type="number"
                        defaultValue={value}
                        className="w-16 bg-surface border border-border-default rounded px-2 py-1 mono text-[12px] text-cell-input text-right focus:outline-none focus:border-accent"
                    />
                    <span className="text-[11px] text-txt-muted">%</span>
                </div>
            </div>
        </div>
    );
}
