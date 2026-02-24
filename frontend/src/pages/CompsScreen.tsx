import { useState } from 'react';

const mockComps = [
    { ticker: "WDAY", name: "Workday, Inc.", ev: 62450.0, rev: 7250.0, ebitda: 1450.0, pe: 65.2 },
    { ticker: "NOW", name: "ServiceNow, Inc.", ev: 145200.0, rev: 8970.0, ebitda: 2150.0, pe: 82.5 },
    { ticker: "CRM", name: "Salesforce, Inc.", ev: 285400.0, rev: 34850.0, ebitda: 8710.0, pe: 45.8 },
    { ticker: "ADBE", name: "Adobe Inc.", ev: 235100.0, rev: 19410.0, ebitda: 7760.0, pe: 42.1 },
    { ticker: "TEAM", name: "Atlassian Corp.", ev: 48900.0, rev: 4100.0, ebitda: 610.0, pe: 85.0 },
];

const mockSubject = {
    ticker: "TECH",
    name: "TechCorp Inc.",
    rev: 500.0, // LTM
    ebitda: 125.0, // LTM
    shares: 100.0,
    netDebt: 25.0
};

export default function CompsScreen() {
    const [comps, setComps] = useState(mockComps);
    const [newTicker, setNewTicker] = useState("");

    // Calculated fields per comp
    const compsWithMultiples = comps.map(c => ({
        ...c,
        evRev: c.ev / c.rev,
        evEbitda: c.ev / c.ebitda
    }));

    // Summary Statistics
    const evRevSorted = [...compsWithMultiples].sort((a, b) => a.evRev - b.evRev);
    const evEbitdaSorted = [...compsWithMultiples].sort((a, b) => a.evEbitda - b.evEbitda);

    const calcMedian = (arr: any[], key: string) => {
        const mid = Math.floor(arr.length / 2);
        return arr.length % 2 !== 0 ? arr[mid][key] : (arr[mid - 1][key] + arr[mid][key]) / 2;
    };

    const stats = {
        mean: {
            evRev: compsWithMultiples.reduce((sum, c) => sum + c.evRev, 0) / comps.length,
            evEbitda: compsWithMultiples.reduce((sum, c) => sum + c.evEbitda, 0) / comps.length,
        },
        median: {
            evRev: calcMedian(evRevSorted, 'evRev'),
            evEbitda: calcMedian(evEbitdaSorted, 'evEbitda'),
        },
        min: {
            evRev: evRevSorted[0]?.evRev || 0,
            evEbitda: evEbitdaSorted[0]?.evEbitda || 0,
        },
        max: {
            evRev: evRevSorted[evRevSorted.length - 1]?.evRev || 0,
            evEbitda: evEbitdaSorted[evEbitdaSorted.length - 1]?.evEbitda || 0,
        }
    };

    // Implied Valuation (using EV/EBITDA median)
    const impliedEv = mockSubject.ebitda * stats.median.evEbitda;
    const impliedEq = impliedEv - mockSubject.netDebt;
    const impliedPrice = impliedEq / mockSubject.shares;

    return (
        <div className="flex-1 overflow-y-auto bg-base h-full">
            {/* Header */}
            <div className="sticky top-0 z-10 bg-base/95 backdrop-blur-sm border-b border-border-subtle px-6 py-4 flex items-center justify-between">
                <div>
                    <div className="flex items-center gap-2 mb-0.5">
                        <h1 className="text-[18px] font-semibold text-txt-primary">Comparable Company Analysis</h1>
                    </div>
                    <p className="text-[12px] text-txt-muted">Trading multiples · Peer group statistics · Implied valuation</p>
                </div>
                <div className="flex items-center gap-2">
                    <input
                        type="text"
                        placeholder="Add ticker (e.g. SNOW)"
                        value={newTicker}
                        onChange={(e) => setNewTicker(e.target.value)}
                        className="bg-surface border border-border-default rounded px-3 py-1.5 text-[12px] text-txt-primary focus:outline-none focus:border-accent w-48 uppercase"
                    />
                    <button className="px-3 py-1.5 rounded bg-surface border border-border-default text-[12px] text-txt-secondary hover:bg-elevated transition-colors">
                        Add Peer
                    </button>
                    <button className="px-4 py-1.5 rounded bg-accent text-white text-[12px] font-semibold hover:bg-accent-hover transition-colors">
                        Refresh Data
                    </button>
                </div>
            </div>

            <div className="px-6 py-5 space-y-5">
                {/* Comps Data Table */}
                <div className="bg-panel rounded-lg border border-border-subtle overflow-hidden">
                    <div className="px-4 py-3 border-b border-border-subtle">
                        <h2 className="text-[13px] font-semibold text-txt-primary">Public Trading Multiples</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-[12px] whitespace-nowrap">
                            <thead>
                                <tr className="border-b border-border-subtle bg-surface/50">
                                    <th className="text-left px-4 py-3 font-semibold text-txt-secondary">Company Name</th>
                                    <th className="text-left px-4 py-3 font-semibold text-txt-secondary">Ticker</th>
                                    <th className="text-right px-4 py-3 font-semibold text-txt-secondary">EV ($M)</th>
                                    <th className="text-right px-4 py-3 font-semibold text-txt-secondary">LTM Rev ($M)</th>
                                    <th className="text-right px-4 py-3 font-semibold text-txt-secondary">LTM EBITDA ($M)</th>
                                    <th className="text-right px-4 py-3 font-semibold text-txt-secondary border-l border-border-subtle bg-accent/5">EV / Rev</th>
                                    <th className="text-right px-4 py-3 font-semibold text-txt-secondary bg-accent/5">EV / EBITDA</th>
                                    <th className="text-right px-4 py-3 font-semibold text-txt-secondary bg-accent/5">P / E</th>
                                    <th className="px-4 py-3"></th>
                                </tr>
                            </thead>
                            <tbody>
                                {compsWithMultiples.map((c, idx) => (
                                    <tr key={idx} className="border-b border-border-subtle/50 hover:bg-surface/20 transition-colors">
                                        <td className="px-4 py-2 text-txt-primary font-medium">{c.name}</td>
                                        <td className="px-4 py-2 mono text-txt-secondary">{c.ticker}</td>
                                        <td className="px-4 py-2 mono text-right text-txt-secondary">${c.ev.toLocaleString()}</td>
                                        <td className="px-4 py-2 mono text-right text-txt-secondary">${c.rev.toLocaleString()}</td>
                                        <td className="px-4 py-2 mono text-right text-txt-secondary">${c.ebitda.toLocaleString()}</td>
                                        <td className="px-4 py-2 mono text-right text-txt-primary font-medium border-l border-border-subtle bg-accent/5">{c.evRev.toFixed(1)}x</td>
                                        <td className="px-4 py-2 mono text-right text-txt-primary font-medium bg-accent/5">{c.evEbitda.toFixed(1)}x</td>
                                        <td className="px-4 py-2 mono text-right text-txt-primary font-medium bg-accent/5">{c.pe.toFixed(1)}x</td>
                                        <td className="px-4 py-2 text-right">
                                            <button className="text-txt-muted hover:text-neg-DEFAULT transition-colors">
                                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                </svg>
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Bottom Row: Stats & Implied Valuation */}
                <div className="grid grid-cols-2 gap-5">
                    {/* Peer Statistics */}
                    <div className="bg-panel rounded-lg border border-border-subtle overflow-hidden">
                        <div className="px-4 py-3 border-b border-border-subtle">
                            <h2 className="text-[13px] font-semibold text-txt-primary">Peer Group Statistics</h2>
                        </div>
                        <table className="w-full text-[12px]">
                            <tbody>
                                <tr className="border-b border-border-subtle/50">
                                    <td className="px-4 py-2 text-txt-secondary">Mean</td>
                                    <td className="px-4 py-2 mono text-right text-txt-primary font-medium">{stats.mean.evRev.toFixed(1)}x</td>
                                    <td className="px-4 py-2 mono text-right text-txt-primary font-medium">{stats.mean.evEbitda.toFixed(1)}x</td>
                                </tr>
                                <tr className="border-b border-border-subtle/50 bg-accent/5">
                                    <td className="px-4 py-2 text-txt-primary font-semibold">Median</td>
                                    <td className="px-4 py-2 mono text-right text-accent font-bold">{stats.median.evRev.toFixed(1)}x</td>
                                    <td className="px-4 py-2 mono text-right text-accent font-bold">{stats.median.evEbitda.toFixed(1)}x</td>
                                </tr>
                                <tr className="border-b border-border-subtle/50">
                                    <td className="px-4 py-2 text-txt-secondary">Min</td>
                                    <td className="px-4 py-2 mono text-right text-txt-secondary">{stats.min.evRev.toFixed(1)}x</td>
                                    <td className="px-4 py-2 mono text-right text-txt-secondary">{stats.min.evEbitda.toFixed(1)}x</td>
                                </tr>
                                <tr>
                                    <td className="px-4 py-2 text-txt-secondary">Max</td>
                                    <td className="px-4 py-2 mono text-right text-txt-secondary">{stats.max.evRev.toFixed(1)}x</td>
                                    <td className="px-4 py-2 mono text-right text-txt-secondary">{stats.max.evEbitda.toFixed(1)}x</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    {/* Implied Valuation */}
                    <div className="bg-panel rounded-lg border border-border-subtle overflow-hidden">
                        <div className="px-4 py-3 border-b border-border-subtle flex justify-between items-center">
                            <h2 className="text-[13px] font-semibold text-txt-primary">Implied Valuation (Subject Co)</h2>
                            <span className="text-[10px] text-txt-muted uppercase tracking-wider">Using Median EV/EBITDA</span>
                        </div>
                        <div className="p-4 space-y-3">
                            <div className="flex justify-between items-center pb-2 border-b border-border-subtle/50">
                                <span className="text-[12px] text-txt-secondary">Subject LTM EBITDA</span>
                                <span className="mono text-[13px] text-txt-primary">${mockSubject.ebitda.toFixed(1)}M</span>
                            </div>
                            <div className="flex justify-between items-center pb-2 border-b border-border-subtle/50">
                                <span className="text-[12px] text-txt-secondary">× Peer Median Multiple</span>
                                <span className="mono text-[13px] text-accent font-semibold">{stats.median.evEbitda.toFixed(1)}x</span>
                            </div>
                            <div className="flex justify-between items-center pb-2 border-b border-border-subtle/50">
                                <span className="text-[12px] font-medium text-txt-primary">Implied Enterprise Value</span>
                                <span className="mono text-[14px] font-bold text-txt-primary">${impliedEv.toLocaleString()}M</span>
                            </div>
                            <div className="flex justify-between items-center pb-2 border-b border-border-subtle/50">
                                <span className="text-[12px] text-txt-secondary">− Net Debt</span>
                                <span className="mono text-[13px] text-neg-DEFAULT">(${mockSubject.netDebt.toFixed(1)}M)</span>
                            </div>
                            <div className="flex justify-between items-center pt-2">
                                <div className="flex flex-col">
                                    <span className="text-[13px] font-bold text-txt-primary">Implied Share Price</span>
                                    <span className="text-[10px] text-txt-muted w-[${mockSubject.shares}M shares]">{mockSubject.shares}M diluted shares</span>
                                </div>
                                <span className="mono text-[20px] font-bold text-pos-DEFAULT">${impliedPrice.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
