import { useState } from 'react';

const mockNarrative = {
    title: "Executive Valuation Summary — TechCorp Inc.",
    content: `Based on the financial projections and valuation methodologies applied, the implied enterprise value for TechCorp Inc. is estimated to range between **$23.5M and $28.2M**, with a base case implied share price of **$152.40**.

**Discounted Cash Flow (DCF):**
The DCF analysis yields a base enterprise value of $25.1M. This assumes a WACC of 10.0% and a Terminal Growth Rate of 2.5%. The projected Unlevered Free Cash Flow grows from $45.8M in FY21 to $112.6M by FY25, driven by margin expansion in the software segment.

**Comparable Companies:**
Trading multiples of 5 peer companies indicate a median EV/EBITDA of 43.1x. Applying this to TechCorp's LTM EBITDA suggests an implied Enterprise Value consistent with the upper bound of the DCF range.

**Key Risk Factors:**
• Revenue concentration in top 3 clients (42% of FY22 revenue).
• Increasing customer acquisition costs (CAC) observed in recent quarters.
• Potential regulatory changes regarding data privacy in the EU market.`,
    isVerified: true
};

function renderParagraphWithBold(paragraph: string) {
    return paragraph.split(/(\*\*.*?\*\*)/g).map((segment, index) => {
        if (segment.startsWith('**') && segment.endsWith('**')) {
            return (
                <strong key={index} className="text-txt-primary font-semibold">
                    {segment.slice(2, -2)}
                </strong>
            );
        }
        return <span key={index}>{segment}</span>;
    });
}

export default function ExportScreen() {
    const [isExporting, setIsExporting] = useState<{ [key: string]: boolean }>({});

    const handleExport = (type: string) => {
        setIsExporting(prev => ({ ...prev, [type]: true }));
        // Simulate network delay for export generation
        setTimeout(() => {
            setIsExporting(prev => ({ ...prev, [type]: false }));
            // Add a temporary success state or toast notification in a real app
        }, 1500);
    };

    return (
        <div className="flex-1 overflow-y-auto bg-base h-full">
            {/* Header */}
            <div className="sticky top-0 z-10 bg-base/95 backdrop-blur-sm border-b border-border-subtle px-6 py-4 flex items-center justify-between">
                <div>
                    <h1 className="text-[18px] font-semibold text-txt-primary mb-0.5">Report & Export Center</h1>
                    <p className="text-[12px] text-txt-muted">AI-Generated Narratives · Institutional-Grade Excel Models</p>
                </div>
            </div>

            <div className="px-6 py-5 max-w-5xl mx-auto space-y-6">

                {/* Top Section: Export Formats */}
                <h2 className="text-[14px] font-semibold text-txt-primary px-1">Download Deliverables</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

                    {/* Excel Card */}
                    <div className="bg-panel border border-border-subtle rounded-xl p-5 hover:border-accent/50 transition-colors group">
                        <div className="w-12 h-12 rounded-lg bg-green-500/10 text-green-500 flex items-center justify-center mb-4">
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <h3 className="text-[15px] font-semibold text-txt-primary mb-1">Full Valuation Model</h3>
                        <p className="text-[12px] text-txt-secondary mb-5 h-10">Institutional-grade Excel workbook with 10 formatted sheets. No VBA macros.</p>
                        <button
                            onClick={() => handleExport('excel')}
                            disabled={isExporting['excel']}
                            className="w-full py-2 rounded-lg bg-surface border border-border-default text-[13px] font-medium text-txt-primary hover:bg-elevated transition-colors flex justify-center items-center gap-2 group-hover:border-accent group-hover:text-accent disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isExporting['excel'] ? (
                                <span className="flex items-center gap-2"><svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Generating...</span>
                            ) : (
                                <>Export .XLSX</>
                            )}
                        </button>
                    </div>

                    {/* PDF Card */}
                    <div className="bg-panel border border-border-subtle rounded-xl p-5 hover:border-accent/50 transition-colors group">
                        <div className="w-12 h-12 rounded-lg bg-red-500/10 text-red-500 flex items-center justify-center mb-4">
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <h3 className="text-[15px] font-semibold text-txt-primary mb-1">Executive Summary</h3>
                        <p className="text-[12px] text-txt-secondary mb-5 h-10">Print-ready PDF report including the LLM narrative, football field chart, and DCF summary.</p>
                        <button
                            onClick={() => handleExport('pdf')}
                            disabled={isExporting['pdf']}
                            className="w-full py-2 rounded-lg bg-surface border border-border-default text-[13px] font-medium text-txt-primary hover:bg-elevated transition-colors flex justify-center items-center gap-2 group-hover:border-accent group-hover:text-accent disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isExporting['pdf'] ? (
                                <span className="flex items-center gap-2"><svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Generating...</span>
                            ) : (
                                <>Export .PDF</>
                            )}
                        </button>
                    </div>

                    {/* JSON Card */}
                    <div className="bg-panel border border-border-subtle rounded-xl p-5 hover:border-accent/50 transition-colors group">
                        <div className="w-12 h-12 rounded-lg bg-yellow-500/10 text-yellow-500 flex items-center justify-center mb-4">
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                            </svg>
                        </div>
                        <h3 className="text-[15px] font-semibold text-txt-primary mb-1">Raw Data (API)</h3>
                        <p className="text-[12px] text-txt-secondary mb-5 h-10">Complete structured output including assumptions, computed metrics, and audit trail.</p>
                        <button
                            onClick={() => handleExport('json')}
                            disabled={isExporting['json']}
                            className="w-full py-2 rounded-lg bg-surface border border-border-default text-[13px] font-medium text-txt-primary hover:bg-elevated transition-colors flex justify-center items-center gap-2 group-hover:border-accent group-hover:text-accent disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isExporting['json'] ? (
                                <span className="flex items-center gap-2"><svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Generating...</span>
                            ) : (
                                <>Export .JSON</>
                            )}
                        </button>
                    </div>
                </div>

                {/* Bottom Section: AI Narrative */}
                <h2 className="text-[14px] font-semibold text-txt-primary px-1 pt-4">AI-Generated Analysis</h2>
                <div className="bg-panel border border-border-subtle rounded-xl overflow-hidden shadow-sm">
                    <div className="px-5 py-4 border-b border-border-subtle flex items-center justify-between bg-surface/30">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded bg-accent text-white flex items-center justify-center">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="text-[14px] font-semibold text-txt-primary">{mockNarrative.title}</h3>
                                <p className="text-[11px] text-txt-muted">Generated by Unsloth Fin-LLM (4-bit)</p>
                            </div>
                        </div>
                        {mockNarrative.isVerified && (
                            <div className="flex items-center gap-1.5 px-3 py-1 bg-pos-DEFAULT/10 border border-pos-DEFAULT/20 rounded-full">
                                <svg className="w-3.5 h-3.5 text-pos-DEFAULT" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span className="text-[10px] uppercase font-bold text-pos-DEFAULT tracking-wider">Hallucination Free</span>
                            </div>
                        )}
                    </div>

                    <div className="p-6 text-[13px] text-txt-secondary leading-relaxed space-y-4">
                        {mockNarrative.content.split('\n\n').map((paragraph, idx) => (
                            <p key={idx}>{renderParagraphWithBold(paragraph)}</p>
                        ))}
                    </div>

                    <div className="px-6 py-3 border-t border-border-subtle bg-surface/30 flex justify-end">
                        <button className="text-[12px] font-medium text-accent hover:text-accent-hover transition-colors flex items-center gap-1">
                            Regenerate Analysis
                            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
}
