import { Link } from 'react-router-dom';

export default function Dashboard() {
    return (
        <div>
            {/* PAGE HEADER */}
            <div className="sticky top-0 z-10 bg-base/95 backdrop-blur-sm border-b border-border-subtle px-6 py-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-[18px] font-semibold text-txt-primary">Dashboard</h1>
                        <p className="text-[12px] text-txt-muted">Platform overview · Recent valuations · Quick actions</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <Link to="/ingest" className="px-4 py-1.5 rounded bg-accent text-white text-[12px] font-semibold hover:bg-accent-hover transition-colors">
                            + New Valuation
                        </Link>
                    </div>
                </div>
            </div>

            <div className="px-6 py-5 space-y-5">
                {/* WELCOME CARD */}
                <div className="bg-accent-subtle rounded-lg border border-accent/20 p-6">
                    <div className="flex items-start justify-between">
                        <div>
                            <h2 className="text-[16px] font-semibold text-txt-primary mb-1">Welcome to FMVA</h2>
                            <p className="text-[13px] text-txt-secondary max-w-xl">Financial Modeling & Valuation Agent — AI-augmented institutional-grade company valuations. Automated DCF, Comparable Company Analysis, Sensitivity Matrices, and LLM-generated narratives.</p>
                        </div>
                        <div className="shrink-0 w-12 h-12 rounded-lg bg-accent flex items-center justify-center">
                            <span className="mono text-white font-bold text-[16px]">FV</span>
                        </div>
                    </div>
                </div>

                {/* QUICK STATS */}
                <div className="grid grid-cols-4 gap-4">
                    <div className="bg-panel rounded-lg border border-border-subtle p-4">
                        <div className="text-[10px] text-txt-muted uppercase tracking-widest mb-1">Active Session</div>
                        <div className="mono text-[22px] font-bold text-accent">1</div>
                        <div className="text-[10px] text-txt-muted mt-1">TechCorp Inc.</div>
                    </div>
                    <div className="bg-panel rounded-lg border border-border-subtle p-4">
                        <div className="text-[10px] text-txt-muted uppercase tracking-widest mb-1">Test Coverage</div>
                        <div className="mono text-[22px] font-bold text-cell-output">40/40</div>
                        <div className="text-[10px] text-pos-DEFAULT mt-1">All passing</div>
                    </div>
                    <div className="bg-panel rounded-lg border border-border-subtle p-4">
                        <div className="text-[10px] text-txt-muted uppercase tracking-widest mb-1">Modules Ready</div>
                        <div className="mono text-[22px] font-bold text-txt-primary">5/7</div>
                        <div className="text-[10px] text-txt-muted mt-1">Phases complete</div>
                    </div>
                    <div className="bg-panel rounded-lg border border-border-subtle p-4">
                        <div className="text-[10px] text-txt-muted uppercase tracking-widest mb-1">Export Formats</div>
                        <div className="mono text-[22px] font-bold text-txt-primary">3</div>
                        <div className="text-[10px] text-txt-muted mt-1">XLSX · JSON · PDF</div>
                    </div>
                </div>

                {/* RECENT VALUATION */}
                <div className="bg-panel rounded-lg border border-border-subtle overflow-hidden">
                    <div className="px-4 py-3 border-b border-border-subtle flex items-center justify-between">
                        <div>
                            <div className="text-[13px] font-semibold text-txt-primary">Recent Valuations</div>
                            <div className="text-[11px] text-txt-muted mt-0.5">Your most recent analysis sessions</div>
                        </div>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-[12px]">
                            <thead>
                                <tr className="bg-surface border-b border-border-subtle">
                                    <th className="text-left px-4 py-2.5 text-txt-muted font-medium">Company</th>
                                    <th className="text-left px-4 py-2.5 text-txt-muted font-medium">Ticker</th>
                                    <th className="text-right px-4 py-2.5 text-txt-muted font-medium">Implied Price</th>
                                    <th className="text-right px-4 py-2.5 text-txt-muted font-medium">EV ($M)</th>
                                    <th className="text-center px-4 py-2.5 text-txt-muted font-medium">Scenario</th>
                                    <th className="text-center px-4 py-2.5 text-txt-muted font-medium">Status</th>
                                    <th className="text-right px-4 py-2.5 text-txt-muted font-medium">Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr className="border-b border-border-subtle/50 hover:bg-surface/40 transition-colors">
                                    <td className="px-4 py-3 font-medium text-txt-primary">TechCorp Inc.</td>
                                    <td className="px-4 py-3 mono text-txt-secondary">TECH</td>
                                    <td className="px-4 py-3 mono text-right text-accent font-semibold">$9.52</td>
                                    <td className="px-4 py-3 mono text-right text-cell-output">$1,102</td>
                                    <td className="px-4 py-3 text-center"><span className="px-2 py-0.5 rounded bg-accent-subtle text-accent text-[10px] font-medium">Base</span></td>
                                    <td className="px-4 py-3 text-center"><span className="px-2 py-0.5 rounded-full bg-pos-bg border border-pos-DEFAULT text-pos-text text-[10px]">✓ Complete</span></td>
                                    <td className="px-4 py-3 mono text-right text-txt-muted text-[11px]">2026-02-23</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
