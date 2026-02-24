import { useState } from 'react';

const tabs = ["Income Statement", "Balance Sheet", "Cash Flow"];

const mockIncomeStatement = [
    { lineItem: "Total Revenue", isHeader: true, values: [413.2, 454.5, 500.0, 550.0, 605.0] },
    { lineItem: "Cost of Goods Sold (COGS)", isHeader: false, values: [124.0, 136.3, 150.0, 165.0, 181.5] },
    { lineItem: "Gross Profit", isHeader: true, isHighlight: true, values: [289.2, 318.2, 350.0, 385.0, 423.5] },
    { lineItem: "Research & Development", isHeader: false, values: [70.0, 75.0, 80.0, 85.0, 90.0] },
    { lineItem: "Sales & Marketing", isHeader: false, values: [100.0, 110.0, 120.0, 130.0, 140.0] },
    { lineItem: "General & Administrative", isHeader: false, values: [20.0, 24.1, 25.0, 28.0, 30.2] },
    { lineItem: "Total Operating Expenses", isHeader: true, values: [190.0, 209.1, 225.0, 243.0, 260.2] },
    { lineItem: "EBITDA", isHeader: true, isHighlight: true, values: [99.2, 109.1, 125.0, 142.0, 163.3] },
    { lineItem: "Depreciation & Amortization", isHeader: false, values: [18.5, 22.0, 25.0, 27.5, 30.2] },
    { lineItem: "EBIT", isHeader: true, values: [80.7, 87.1, 100.0, 114.5, 133.1] },
    { lineItem: "Interest Expense", isHeader: false, values: [8.0, 7.5, 7.0, 6.5, 6.0] },
    { lineItem: "EBT", isHeader: true, values: [72.7, 79.6, 93.0, 108.0, 127.1] },
    { lineItem: "Taxes (21%)", isHeader: false, values: [15.3, 16.7, 19.5, 22.7, 26.7] },
    { lineItem: "Net Income", isHeader: true, isHighlight: true, values: [57.4, 62.9, 73.5, 85.3, 100.4] },
];

const mockBalanceSheet = [
    { lineItem: "Cash & Equivalents", isHeader: false, values: [150.0, 180.0, 220.0, 270.0, 330.0] },
    { lineItem: "Accounts Receivable", isHeader: false, values: [60.0, 65.0, 75.0, 85.0, 95.0] },
    { lineItem: "Total Current Assets", isHeader: true, values: [210.0, 245.0, 295.0, 355.0, 425.0] },
    { lineItem: "Net PP&E", isHeader: false, values: [120.0, 135.0, 150.0, 165.0, 180.0] },
    { lineItem: "Goodwill", isHeader: false, values: [80.0, 80.0, 80.0, 80.0, 80.0] },
    { lineItem: "Total Assets", isHeader: true, isHighlight: true, values: [410.0, 460.0, 525.0, 600.0, 685.0] },
    { lineItem: "Accounts Payable", isHeader: false, values: [30.0, 35.0, 40.0, 45.0, 50.0] },
    { lineItem: "Accrued Liabilities", isHeader: false, values: [20.0, 22.0, 25.0, 28.0, 32.0] },
    { lineItem: "Total Current Liabilities", isHeader: true, values: [50.0, 57.0, 65.0, 73.0, 82.0] },
    { lineItem: "Long-Term Debt", isHeader: false, values: [100.0, 95.0, 90.0, 85.0, 80.0] },
    { lineItem: "Total Liabilities", isHeader: true, values: [150.0, 152.0, 155.0, 158.0, 162.0] },
    { lineItem: "Retained Earnings", isHeader: false, values: [160.0, 208.0, 270.0, 342.0, 423.0] },
    { lineItem: "Common Stock", isHeader: false, values: [100.0, 100.0, 100.0, 100.0, 100.0] },
    { lineItem: "Total Equity", isHeader: true, values: [260.0, 308.0, 370.0, 442.0, 523.0] },
    { lineItem: "Total Liabilities & Equity", isHeader: true, isHighlight: true, values: [410.0, 460.0, 525.0, 600.0, 685.0] },
];

const mockCashFlow = [
    { lineItem: "Net Income", isHeader: false, values: [57.4, 62.9, 73.5, 85.3, 100.4] },
    { lineItem: "Depreciation & Amortization", isHeader: false, values: [18.5, 22.0, 25.0, 27.5, 30.2] },
    { lineItem: "Change in Net Working Capital", isHeader: false, values: [-5.0, -8.0, -12.0, -15.0, -18.0] },
    { lineItem: "Cash from Operations", isHeader: true, isHighlight: true, values: [70.9, 76.9, 86.5, 97.8, 112.6] },
    { lineItem: "Capital Expenditures (CapEx)", isHeader: false, values: [-20.0, -37.0, -40.0, -42.5, -45.2] },
    { lineItem: "Cash from Investing", isHeader: true, isHighlight: true, values: [-20.0, -37.0, -40.0, -42.5, -45.2] },
    { lineItem: "Debt Repayment", isHeader: false, values: [-5.0, -5.0, -5.0, -5.0, -5.0] },
    { lineItem: "Cash from Financing", isHeader: true, isHighlight: true, values: [-5.0, -5.0, -5.0, -5.0, -5.0] },
    { lineItem: "Net Change in Cash", isHeader: true, values: [45.9, 34.9, 41.5, 50.3, 62.4] },
];

const parseData = (tab: string) => {
    if (tab === "Income Statement") return mockIncomeStatement;
    if (tab === "Balance Sheet") return mockBalanceSheet;
    return mockCashFlow;
};

export default function ModelScreen() {
    const [activeTab, setActiveTab] = useState(tabs[0]);
    const currentData = parseData(activeTab);

    return (
        <div className="flex-1 overflow-y-auto bg-base h-full">
            {/* Header */}
            <div className="sticky top-0 z-10 bg-base/95 backdrop-blur-sm border-b border-border-subtle px-6 py-4">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-0.5">
                            <h1 className="text-[18px] font-semibold text-txt-primary">3-Statement Model</h1>
                            <span className="px-2 py-0.5 rounded-full bg-pos-bg text-pos-DEFAULT border border-pos-DEFAULT/30 text-[10px] uppercase font-bold tracking-wider">Balanced</span>
                        </div>
                        <p className="text-[12px] text-txt-muted">Historical and projected financial statements connected end-to-end.</p>
                    </div>
                </div>
            </div>

            <div className="px-6 py-5">
                {/* Tab Navigation */}
                <div className="flex items-center border-b border-border-subtle mb-4">
                    {tabs.map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-4 py-2 text-[13px] font-medium border-b-2 transition-colors ${activeTab === tab
                                    ? 'border-accent text-accent'
                                    : 'border-transparent text-txt-muted hover:text-txt-primary hover:border-border-default'
                                }`}
                        >
                            {tab}
                        </button>
                    ))}
                </div>

                {/* Data Grid */}
                <div className="bg-panel rounded-lg border border-border-subtle overflow-x-auto">
                    <table className="w-full text-[12px] whitespace-nowrap">
                        <thead>
                            <tr className="border-b border-border-subtle bg-surface/50">
                                <th className="text-left px-4 py-3 font-semibold text-txt-secondary uppercase tracking-wider text-[10px] w-64 md:w-80 sticky left-0 bg-surface/95 backdrop-blur-sm z-10 border-r border-border-subtle">
                                    in $ Millions, Fiscal Year End Dec 31
                                </th>
                                <th className="text-right px-4 py-3 font-semibold text-txt-secondary">2021A</th>
                                <th className="text-right px-4 py-3 font-semibold text-txt-secondary">2022A</th>
                                <th className="text-right px-4 py-3 font-semibold text-txt-secondary border-l-2 border-accent/30 bg-accent/5">2023E</th>
                                <th className="text-right px-4 py-3 font-semibold text-txt-secondary bg-accent/5">2024E</th>
                                <th className="text-right px-4 py-3 font-semibold text-txt-secondary bg-accent/5">2025E</th>
                            </tr>
                        </thead>
                        <tbody>
                            {currentData.map((row, idx) => (
                                <tr
                                    key={idx}
                                    className={`
                                        border-b border-border-subtle/50 
                                        ${row.isHighlight ? 'bg-surface/30' : 'hover:bg-surface/20'}
                                        transition-colors
                                    `}
                                >
                                    <td
                                        className={`
                                            px-4 py-2 sticky left-0 bg-panel z-10 border-r border-border-subtle/50
                                            ${row.isHeader ? 'font-semibold text-txt-primary' : 'text-txt-secondary pl-8'}
                                        `}
                                    >
                                        {row.lineItem}
                                    </td>
                                    {row.values.map((val, vIdx) => (
                                        <td
                                            key={vIdx}
                                            className={`
                                                px-4 py-2 text-right mono
                                                ${vIdx >= 2 ? 'bg-accent/5' : ''}
                                                ${vIdx === 2 ? 'border-l-2 border-accent/30' : ''}
                                                ${row.isHighlight ? 'font-semibold text-txt-primary' : 'text-cell-input'}
                                                ${val < 0 ? 'text-neg-DEFAULT' : ''}
                                            `}
                                        >
                                            {val < 0 ? `(${Math.abs(val).toFixed(1)})` : val.toFixed(1)}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
