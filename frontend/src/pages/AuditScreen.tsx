import { useState } from 'react';

const mockAuditLogs = [
    { step: "Calculate Revenue", formula: "Base Rev * (1 + Growth)", inputs: { "Base Rev": 413.2, "Growth": 0.10 }, output: 454.5, time: "10:04:01:230", status: "success" },
    { step: "Calculate COGS", formula: "Rev * COGS Margin", inputs: { "Rev": 454.5, "COGS %": 0.30 }, output: 136.3, time: "10:04:01:235", status: "success" },
    { step: "Calculate Gross Profit", formula: "Rev - COGS", inputs: { "Rev": 454.5, "COGS": 136.3 }, output: 318.2, time: "10:04:01:240", status: "success" },
    { step: "Calculate OpEx", formula: "S&M + R&D + G&A", inputs: { "S&M": 110.0, "R&D": 75.0, "G&A": 24.1 }, output: 209.1, time: "10:04:01:255", status: "success" },
    { step: "Calculate EBITDA", formula: "Gross Profit - OpEx", inputs: { "Gross": 318.2, "OpEx": 209.1 }, output: 109.1, time: "10:04:01:262", status: "success" },
    { step: "Depreciation Check", formula: "D&A / PP&E", inputs: { "D&A": 22.0, "PP&E": 135.0 }, output: "16.3%", time: "10:04:01:270", status: "warning", message: "D&A rate exceeds historical average (>15%)" },
    { step: "Calculate EBIT", formula: "EBITDA - D&A", inputs: { "EBITDA": 109.1, "D&A": 22.0 }, output: 87.1, time: "10:04:01:281", status: "success" },
    { step: "Calculate NOPAT", formula: "EBIT * (1 - Tax)", inputs: { "EBIT": 87.1, "Tax Rate": 0.21 }, output: 68.8, time: "10:04:01:290", status: "success" },
    { step: "Calculate UFCF", formula: "NOPAT + D&A - CapEx - ΔNWC", inputs: { "NOPAT": 68.8, "D&A": 22.0, "CapEx": 37.0, "ΔNWC": 8.0 }, output: 45.8, time: "10:04:01:315", status: "success" },
    { step: "BS Integrity Check", formula: "Assets - (Liab + Equity)", inputs: { "Assets": 460.0, "L+E": 460.0 }, output: 0.0, time: "10:04:01:400", status: "success" },
];

export default function AuditScreen() {
    const [searchTerm, setSearchTerm] = useState("");
    const [filterStatus, setFilterStatus] = useState("all");

    const filteredLogs = mockAuditLogs.filter(log => {
        const matchesSearch = log.step.toLowerCase().includes(searchTerm.toLowerCase()) ||
            log.formula.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = filterStatus === "all" || log.status === filterStatus;
        return matchesSearch && matchesStatus;
    });

    return (
        <div className="flex-1 flex flex-col h-full bg-base overflow-hidden">
            {/* Header */}
            <div className="flex-none bg-base/95 backdrop-blur-sm border-b border-border-subtle px-6 py-4">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-0.5">
                            <h1 className="text-[18px] font-semibold text-txt-primary">Audit Trail</h1>
                            <span className="px-2 py-0.5 rounded-full bg-surface border border-border-subtle text-txt-secondary text-[10px] uppercase font-bold tracking-wider">
                                {mockAuditLogs.length} Records
                            </span>
                        </div>
                        <p className="text-[12px] text-txt-muted">Forensic computation log and integrity checks</p>
                    </div>

                    {/* Controls */}
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <svg className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-txt-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            <input
                                type="text"
                                placeholder="Search formulas..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-9 pr-4 py-1.5 bg-surface border border-border-default rounded text-[12px] text-txt-primary focus:outline-none focus:border-accent w-64"
                            />
                        </div>
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className="px-3 py-1.5 bg-surface border border-border-default rounded text-[12px] text-txt-primary focus:outline-none focus:border-accent appearance-none cursor-pointer"
                        >
                            <option value="all">All Statuses</option>
                            <option value="success">Success</option>
                            <option value="warning">Warnings</option>
                            <option value="error">Errors</option>
                        </select>
                        <button className="px-3 py-1.5 rounded bg-surface border border-border-default text-[12px] text-txt-secondary hover:bg-elevated transition-colors flex items-center gap-2">
                            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                            </svg>
                            Export JSON
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto px-6 py-5">
                <div className="bg-panel rounded-lg border border-border-subtle shadow-sm overflow-hidden">
                    <table className="w-full text-[12px] text-left">
                        <thead className="bg-surface/50 border-b border-border-subtle sticky top-0 z-10">
                            <tr>
                                <th className="px-4 py-3 font-semibold text-txt-secondary w-24">Timestamp</th>
                                <th className="px-4 py-3 font-semibold text-txt-secondary w-48">Computation Step</th>
                                <th className="px-4 py-3 font-semibold text-txt-secondary">Formula Logic</th>
                                <th className="px-4 py-3 font-semibold text-txt-secondary w-64">Input Variables</th>
                                <th className="px-4 py-3 font-semibold text-txt-secondary text-right w-24">Output</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border-subtle/50">
                            {filteredLogs.length > 0 ? (
                                filteredLogs.map((log, idx) => (
                                    <tr key={idx} className="hover:bg-surface/30 transition-colors group">
                                        <td className="px-4 py-3 text-[11px] font-mono text-txt-muted whitespace-nowrap">
                                            {log.time}
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-2">
                                                {log.status === 'success' && (
                                                    <span className="w-1.5 h-1.5 rounded-full bg-pos-DEFAULT shrink-0"></span>
                                                )}
                                                {log.status === 'warning' && (
                                                    <span className="w-1.5 h-1.5 rounded-full bg-warn shrink-0"></span>
                                                )}
                                                {log.status === 'error' && (
                                                    <span className="w-1.5 h-1.5 rounded-full bg-neg-DEFAULT shrink-0"></span>
                                                )}
                                                <span className="font-medium text-txt-primary truncate">
                                                    {log.step}
                                                </span>
                                            </div>
                                            {log.message && (
                                                <div className="mt-1 pl-3.5 text-[11px] text-warn opacity-90">
                                                    ↳ {log.message}
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-4 py-3">
                                            <code className="px-1.5 py-0.5 rounded bg-surface border border-border-subtle/50 text-accent font-mono text-[11px]">
                                                {log.formula}
                                            </code>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex flex-wrap gap-1.5">
                                                {Object.entries(log.inputs).map(([key, value], i) => (
                                                    <div key={i} className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-surface/50 border border-border-subtle/30 text-[10px] font-mono">
                                                        <span className="text-txt-muted">{key}:</span>
                                                        <span className="text-txt-primary">{value}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            <span className={`font-mono font-medium ${log.status === 'warning' ? 'text-warn' : log.status === 'error' ? 'text-neg-DEFAULT' : 'text-pos-DEFAULT'}`}>
                                                {typeof log.output === 'number' ? log.output.toFixed(1) : log.output}
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={5} className="px-4 py-8 text-center text-txt-muted text-[13px]">
                                        No audit logs found matching your criteria.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
