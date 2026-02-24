import React, { useState } from 'react';

interface WaccTgrMatrix {
    waccRange: number[];
    tgrRange: number[];
    baseWacc: number;
    baseTgr: number;
    data: number[][];
}

interface WaccMultipleMatrix {
    waccRange: number[];
    multRange: number[];
    baseWacc: number;
    baseMult: number;
    data: number[][];
}

const mockWaccTgr: WaccTgrMatrix = {
    waccRange: [0.08, 0.09, 0.10, 0.11, 0.12],
    tgrRange: [0.015, 0.020, 0.025, 0.030, 0.035],
    baseWacc: 0.10,
    baseTgr: 0.025,
    data: [
        [185.2, 201.5, 222.4, 250.2, 288.7],
        [158.4, 170.1, 184.6, 203.1, 227.5],
        [138.5, 147.2, 157.8, 171.0, 188.0], // Base case row
        [123.0, 129.8, 137.9, 147.8, 160.1],
        [110.8, 116.2, 122.5, 130.2, 139.7]
    ]
};

const mockWaccMultiple: WaccMultipleMatrix = {
    waccRange: [0.08, 0.09, 0.10, 0.11, 0.12],
    multRange: [8.0, 9.0, 10.0, 11.0, 12.0],
    baseWacc: 0.10,
    baseMult: 10.0,
    data: [
        [142.5, 158.2, 174.0, 189.7, 205.5],
        [135.8, 150.1, 164.5, 178.8, 193.2],
        [129.8, 142.9, 156.0, 169.1, 182.2], // Base case row
        [124.2, 136.3, 148.4, 160.5, 172.6],
        [119.1, 130.3, 141.5, 152.7, 163.9]
    ]
};

const mockFootballField = {
    currentPrice: 152.40,
    ranges: [
        { label: "52-Week Range", low: 110.50, high: 165.80, color: "bg-surface" },
        { label: "Analyst Targets", low: 135.00, high: 180.00, color: "bg-border-default" },
        { label: "DCF (Gordon Growth)", low: 138.50, high: 188.00, color: "bg-accent/80" },
        { label: "DCF (Exit Multiple)", low: 129.80, high: 182.20, color: "bg-accent" },
        { label: "Trading Comps", low: 145.20, high: 210.50, color: "bg-pos-DEFAULT/80" },
        { label: "Precedent Transactions", low: 160.00, high: 235.00, color: "bg-purple-500/80" },
    ]
};

// Heatmap color generator based on value relative to base case
const getHeatmapColor = (val: number, base: number) => {
    const diff = (val - base) / base;
    if (diff > 0.15) return 'bg-pos-DEFAULT/50 text-pos-DEFAULT';
    if (diff > 0.05) return 'bg-pos-DEFAULT/20 text-pos-DEFAULT hover:bg-pos-DEFAULT/30';
    if (diff > -0.05) return 'bg-surface/50 text-txt-primary';
    if (diff > -0.15) return 'bg-neg-DEFAULT/20 text-neg-DEFAULT hover:bg-neg-DEFAULT/30';
    return 'bg-neg-DEFAULT/50 text-neg-DEFAULT';
};

export default function SensitivityScreen() {
    const [activeMatrix, setActiveMatrix] = useState<'tgr' | 'mult'>('tgr');
    const matrix = activeMatrix === 'tgr' ? mockWaccTgr : mockWaccMultiple;
    const columnValues = activeMatrix === 'tgr' ? mockWaccTgr.tgrRange : mockWaccMultiple.multRange;
    const baseVal = activeMatrix === 'tgr' ? mockWaccTgr.data[2][2] : mockWaccMultiple.data[2][2];

    const minPrice = 80; // Hardcoded scaling for viz purposes
    const maxPrice = 250;
    const priceRange = maxPrice - minPrice;

    return (
        <div className="flex-1 overflow-y-auto bg-base h-full">
            {/* Header */}
            <div className="sticky top-0 z-10 bg-base/95 backdrop-blur-sm border-b border-border-subtle px-6 py-4">
                <div className="flex items-center gap-2 mb-0.5">
                    <h1 className="text-[18px] font-semibold text-txt-primary">Sensitivity Analysis</h1>
                </div>
                <p className="text-[12px] text-txt-muted">Valuation matrices and Football Field summary</p>
            </div>

            <div className="px-6 py-5 space-y-6">

                {/* Top Section: Matrices */}
                <div className="bg-panel rounded-lg border border-border-subtle overflow-hidden">
                    <div className="px-4 py-3 border-b border-border-subtle flex justify-between items-center">
                        <h2 className="text-[14px] font-semibold text-txt-primary">Implied Share Price Sensitivity</h2>
                        <div className="flex items-center bg-surface rounded border border-border-default p-0.5">
                            <button
                                onClick={() => setActiveMatrix('tgr')}
                                className={`px-3 py-1 rounded text-[11px] font-medium transition-colors ${activeMatrix === 'tgr' ? 'bg-panel shadow-sm text-txt-primary' : 'text-txt-muted hover:text-txt-primary'}`}
                            >
                                WACC vs. TGR
                            </button>
                            <button
                                onClick={() => setActiveMatrix('mult')}
                                className={`px-3 py-1 rounded text-[11px] font-medium transition-colors ${activeMatrix === 'mult' ? 'bg-panel shadow-sm text-txt-primary' : 'text-txt-muted hover:text-txt-primary'}`}
                            >
                                WACC vs. Exit Mult
                            </button>
                        </div>
                    </div>

                    <div className="p-6 flex justify-center">
                        <div className="flex">
                            {/* Y-Axis Label */}
                            <div className="flex items-center justify-center mr-6">
                                <span className="transform -rotate-90 text-[12px] font-semibold text-txt-secondary tracking-widest uppercase">WACC</span>
                            </div>

                            <div>
                                {/* X-Axis Label */}
                                <div className="text-center mb-4 text-[12px] font-semibold text-txt-secondary tracking-widest uppercase">
                                    {activeMatrix === 'tgr' ? 'Terminal Growth Rate (TGR)' : 'Exit EBITDA Multiple'}
                                </div>

                                <div className="grid grid-cols-6 gap-1">
                                    {/* Corner empty block */}
                                    <div className="w-16 h-10"></div>

                                    {/* Col Headers */}
                                    {columnValues.map((val: number, idx: number) => (
                                        <div key={idx} className="w-20 h-10 flex items-center justify-center text-[13px] font-medium text-txt-secondary bg-surface rounded">
                                            {activeMatrix === 'tgr' ? `${(val * 100).toFixed(1)}%` : `${val.toFixed(1)}x`}
                                        </div>
                                    ))}

                                    {/* Rows */}
                                    {matrix.waccRange.map((wacc, rIdx) => (
                                        <React.Fragment key={rIdx}>
                                            <div className="w-16 h-12 flex items-center justify-center text-[13px] font-medium text-txt-secondary bg-surface rounded">
                                                {(wacc * 100).toFixed(1)}%
                                            </div>
                                            {matrix.data[rIdx].map((val, cIdx) => {
                                                const isBase = rIdx === 2 && cIdx === 2;
                                                return (
                                                    <div
                                                        key={cIdx}
                                                        className={`
                                                            w-20 h-12 flex items-center justify-center text-[14px] font-mono rounded transition-colors
                                                            ${getHeatmapColor(val, baseVal)}
                                                            ${isBase ? 'ring-2 ring-accent ring-inset font-bold shadow-md z-10' : ''}
                                                        `}
                                                        title={`WACC: ${(wacc * 100).toFixed(1)}%, ${activeMatrix === 'tgr' ? 'TGR' : 'Mult'}: ${activeMatrix === 'tgr' ? `${(columnValues[cIdx] * 100).toFixed(1)}%` : `${columnValues[cIdx].toFixed(1)}x`}`}
                                                    >
                                                        ${val.toFixed(1)}
                                                    </div>
                                                )
                                            })}
                                        </React.Fragment>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Bottom Section: Football Field */}
                <div className="bg-panel rounded-lg border border-border-subtle overflow-hidden">
                    <div className="px-4 py-3 border-b border-border-subtle flex justify-between items-center">
                        <h2 className="text-[14px] font-semibold text-txt-primary">Valuation Summary (Football Field)</h2>
                        <div className="flex items-center gap-2">
                            <span className="w-3 h-3 rounded-full bg-accent/80"></span>
                            <span className="text-[11px] text-txt-secondary mr-2">DCF</span>
                            <span className="w-3 h-3 rounded-full bg-pos-DEFAULT/80"></span>
                            <span className="text-[11px] text-txt-secondary">Relative</span>
                        </div>
                    </div>

                    <div className="p-6">
                        <div className="relative pt-6 pb-2">
                            {/* X-Axis Grid Lines */}
                            <div className="absolute top-0 bottom-0 left-[20%] right-0 border-l border-r border-border-subtle/50 flex justify-between -z-10 px-[10%]">
                                <div className="border-l border-border-subtle/50 h-full"></div>
                                <div className="border-l border-border-subtle/50 h-full"></div>
                                <div className="border-l border-border-subtle/50 h-full"></div>
                            </div>

                            {/* X-Axis Labels */}
                            <div className="absolute top-0 left-[20%] right-0 flex justify-between text-[11px] font-mono text-txt-muted -translate-y-6">
                                <span>${minPrice}</span>
                                <span>${minPrice + priceRange * 0.25}</span>
                                <span>${minPrice + priceRange * 0.5}</span>
                                <span>${minPrice + priceRange * 0.75}</span>
                                <span>${maxPrice}</span>
                            </div>

                            {/* Current Price Line */}
                            <div
                                className="absolute top-0 bottom-0 w-px bg-red-500/80 z-20 border-r border-red-500/80 border-dashed"
                                style={{ left: `calc(20% + ${((mockFootballField.currentPrice - minPrice) / priceRange) * 80}%)` }}
                            >
                                <div className="absolute -bottom-5 -translate-x-1/2 bg-red-500/10 text-red-500 px-2 py-0.5 rounded text-[10px] font-bold whitespace-nowrap">
                                    Current: ${mockFootballField.currentPrice}
                                </div>
                            </div>

                            {/* Chart Rows */}
                            <div className="space-y-6 w-full relative z-10">
                                {mockFootballField.ranges.map((range, idx) => {
                                    const leftPct = ((range.low - minPrice) / priceRange) * 100;
                                    const widthPct = ((range.high - range.low) / priceRange) * 100;

                                    return (
                                        <div key={idx} className="flex items-center h-8">
                                            {/* Y-Axis Label */}
                                            <div className="w-[20%] pr-4 text-right text-[12px] font-medium text-txt-secondary leading-tight flex-shrink-0">
                                                {range.label}
                                            </div>

                                            {/* Bar Track container */}
                                            <div className="w-[80%] relative h-full flex items-center group">
                                                {/* Bar */}
                                                <div
                                                    className={`absolute h-6 rounded ${range.color} border border-white/10 shadow-sm transition-all group-hover:brightness-110 flex items-center`}
                                                    style={{
                                                        left: `${leftPct}%`,
                                                        width: `${widthPct}%`
                                                    }}
                                                >
                                                    {/* Values inside/outside bar based on width */}
                                                    <div className="absolute -left-2 -translate-x-full text-[11px] font-mono text-txt-muted group-hover:text-txt-primary opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                                                        ${range.low.toFixed(0)}
                                                    </div>
                                                    <div className="absolute -right-2 translate-x-full text-[11px] font-mono text-txt-muted group-hover:text-txt-primary opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                                                        ${range.high.toFixed(0)}
                                                    </div>

                                                    {/* Central text if bar is wide enough */}
                                                    <div className="w-full text-center text-[10px] font-bold text-white/90 truncate px-1 drop-shadow-md">
                                                        ${range.low.toFixed(0)} - ${range.high.toFixed(0)}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>

                            {/* X-Axis Bottom labels repeat */}
                            <div className="relative mt-8 ml-[20%] flex justify-between text-[11px] font-mono text-txt-muted bg-base">
                                <span>${minPrice}</span>
                                <span>${maxPrice}</span>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
