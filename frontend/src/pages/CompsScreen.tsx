import { useState } from 'react';

interface ComparableRow {
    id: string;
    ticker: string;
    name: string;
    ev: number;
    rev: number;
    ebitda: number;
    pe: number;
}

interface SubjectCompany {
    ticker: string;
    name: string;
    rev: number;
    ebitda: number;
    shares: number;
    netDebt: number;
}

interface NewCompForm {
    ticker: string;
    name: string;
    ev: string;
    rev: string;
    ebitda: string;
    pe: string;
}

type CompNumericField = 'ev' | 'rev' | 'ebitda' | 'pe';
type SubjectNumericField = 'rev' | 'ebitda' | 'shares' | 'netDebt';

const sampleComps: Array<Omit<ComparableRow, 'id'>> = [
    { ticker: 'WDAY', name: 'Workday, Inc.', ev: 62450, rev: 7250, ebitda: 1450, pe: 65.2 },
    { ticker: 'NOW', name: 'ServiceNow, Inc.', ev: 145200, rev: 8970, ebitda: 2150, pe: 82.5 },
    { ticker: 'CRM', name: 'Salesforce, Inc.', ev: 285400, rev: 34850, ebitda: 8710, pe: 45.8 },
    { ticker: 'ADBE', name: 'Adobe Inc.', ev: 235100, rev: 19410, ebitda: 7760, pe: 42.1 },
    { ticker: 'TEAM', name: 'Atlassian Corp.', ev: 48900, rev: 4100, ebitda: 610, pe: 85.0 },
];

const sampleSubject: SubjectCompany = {
    ticker: 'TECH',
    name: 'TechCorp Inc.',
    rev: 500,
    ebitda: 125,
    shares: 100,
    netDebt: 25,
};

const emptyNewComp: NewCompForm = {
    ticker: '',
    name: '',
    ev: '',
    rev: '',
    ebitda: '',
    pe: '',
};

const buildComp = (comp: Omit<ComparableRow, 'id'>): ComparableRow => ({
    ...comp,
    id: `${comp.ticker}-${Math.random().toString(36).slice(2, 9)}`,
});

const buildSampleComps = () => sampleComps.map(buildComp);

export default function CompsScreen() {
    const [comps, setComps] = useState<ComparableRow[]>(() => buildSampleComps());
    const [subject, setSubject] = useState<SubjectCompany>(sampleSubject);
    const [newComp, setNewComp] = useState<NewCompForm>(emptyNewComp);
    const [formError, setFormError] = useState<string | null>(null);

    const compsWithMultiples = comps.map((c) => ({
        ...c,
        evRev: c.rev !== 0 ? c.ev / c.rev : 0,
        evEbitda: c.ebitda !== 0 ? c.ev / c.ebitda : 0,
    }));

    const evRevSorted = compsWithMultiples.map((c) => c.evRev).sort((a, b) => a - b);
    const evEbitdaSorted = compsWithMultiples.map((c) => c.evEbitda).sort((a, b) => a - b);
    const compCount = compsWithMultiples.length;

    const calcMedian = (arr: number[]) => {
        if (arr.length === 0) return 0;
        const mid = Math.floor(arr.length / 2);
        return arr.length % 2 !== 0 ? arr[mid] : (arr[mid - 1] + arr[mid]) / 2;
    };

    const stats = {
        mean: {
            evRev: compCount > 0 ? compsWithMultiples.reduce((sum, c) => sum + c.evRev, 0) / compCount : 0,
            evEbitda: compCount > 0 ? compsWithMultiples.reduce((sum, c) => sum + c.evEbitda, 0) / compCount : 0,
        },
        median: {
            evRev: calcMedian(evRevSorted),
            evEbitda: calcMedian(evEbitdaSorted),
        },
        min: {
            evRev: evRevSorted[0] ?? 0,
            evEbitda: evEbitdaSorted[0] ?? 0,
        },
        max: {
            evRev: evRevSorted[evRevSorted.length - 1] ?? 0,
            evEbitda: evEbitdaSorted[evEbitdaSorted.length - 1] ?? 0,
        },
    };

    const impliedEv = subject.ebitda * stats.median.evEbitda;
    const impliedEq = impliedEv - subject.netDebt;
    const impliedPrice = subject.shares !== 0 ? impliedEq / subject.shares : 0;

    const handleCompTextChange = (id: string, field: 'ticker' | 'name', value: string) => {
        setComps((prev) =>
            prev.map((c) =>
                c.id === id
                    ? { ...c, [field]: field === 'ticker' ? value.toUpperCase() : value }
                    : c
            )
        );
    };

    const handleCompNumberChange = (id: string, field: CompNumericField, value: string) => {
        const parsed = Number.parseFloat(value);
        setComps((prev) =>
            prev.map((c) =>
                c.id === id
                    ? { ...c, [field]: Number.isFinite(parsed) ? parsed : 0 }
                    : c
            )
        );
    };

    const handleSubjectTextChange = (field: 'ticker' | 'name', value: string) => {
        setSubject((prev) => ({
            ...prev,
            [field]: field === 'ticker' ? value.toUpperCase() : value,
        }));
    };

    const handleSubjectNumberChange = (field: SubjectNumericField, value: string) => {
        const parsed = Number.parseFloat(value);
        setSubject((prev) => ({
            ...prev,
            [field]: Number.isFinite(parsed) ? parsed : 0,
        }));
    };

    const handleAddPeer = () => {
        const ticker = newComp.ticker.trim().toUpperCase();
        const name = newComp.name.trim();
        const ev = Number.parseFloat(newComp.ev);
        const rev = Number.parseFloat(newComp.rev);
        const ebitda = Number.parseFloat(newComp.ebitda);
        const pe = Number.parseFloat(newComp.pe);

        if (!ticker || !name) {
            setFormError('Ticker and company name are required.');
            return;
        }

        if (![ev, rev, ebitda, pe].every((n) => Number.isFinite(n))) {
            setFormError('EV, revenue, EBITDA, and P/E must be numeric.');
            return;
        }

        if (rev <= 0 || ebitda <= 0) {
            setFormError('Revenue and EBITDA must be greater than 0.');
            return;
        }

        setComps((prev) => [...prev, buildComp({ ticker, name, ev, rev, ebitda, pe })]);
        setNewComp(emptyNewComp);
        setFormError(null);
    };

    const handleRemovePeer = (id: string) => {
        setComps((prev) => prev.filter((c) => c.id !== id));
    };

    const handleLoadSample = () => {
        setComps(buildSampleComps());
        setSubject(sampleSubject);
        setNewComp(emptyNewComp);
        setFormError(null);
    };

    return (
        <div className="flex-1 overflow-y-auto bg-base h-full">
            <div className="sticky top-0 z-10 bg-base/95 backdrop-blur-sm border-b border-border-subtle px-6 py-4 flex items-center justify-between">
                <div>
                    <h1 className="text-[18px] font-semibold text-txt-primary">Comparable Company Analysis</h1>
                    <p className="text-[12px] text-txt-muted">Manual input enabled for your own test data.</p>
                </div>
                <button
                    onClick={handleLoadSample}
                    className="px-4 py-1.5 rounded bg-surface border border-border-default text-[12px] text-txt-secondary hover:bg-elevated transition-colors"
                >
                    Load Sample Data
                </button>
            </div>

            <div className="px-6 py-5 space-y-5">
                <div className="bg-panel rounded-lg border border-border-subtle p-4">
                    <h2 className="text-[13px] font-semibold text-txt-primary mb-3">Add Peer</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-2">
                        <input
                            type="text"
                            placeholder="Ticker"
                            value={newComp.ticker}
                            onChange={(e) => setNewComp((prev) => ({ ...prev, ticker: e.target.value.toUpperCase() }))}
                            className="bg-surface border border-border-default rounded px-3 py-2 text-[12px] text-txt-primary focus:outline-none focus:border-accent uppercase"
                        />
                        <input
                            type="text"
                            placeholder="Name"
                            value={newComp.name}
                            onChange={(e) => setNewComp((prev) => ({ ...prev, name: e.target.value }))}
                            className="bg-surface border border-border-default rounded px-3 py-2 text-[12px] text-txt-primary focus:outline-none focus:border-accent"
                        />
                        <input
                            type="number"
                            step="0.1"
                            placeholder="EV"
                            value={newComp.ev}
                            onChange={(e) => setNewComp((prev) => ({ ...prev, ev: e.target.value }))}
                            className="bg-surface border border-border-default rounded px-3 py-2 text-[12px] text-txt-primary focus:outline-none focus:border-accent mono"
                        />
                        <input
                            type="number"
                            step="0.1"
                            placeholder="Revenue"
                            value={newComp.rev}
                            onChange={(e) => setNewComp((prev) => ({ ...prev, rev: e.target.value }))}
                            className="bg-surface border border-border-default rounded px-3 py-2 text-[12px] text-txt-primary focus:outline-none focus:border-accent mono"
                        />
                        <input
                            type="number"
                            step="0.1"
                            placeholder="EBITDA"
                            value={newComp.ebitda}
                            onChange={(e) => setNewComp((prev) => ({ ...prev, ebitda: e.target.value }))}
                            className="bg-surface border border-border-default rounded px-3 py-2 text-[12px] text-txt-primary focus:outline-none focus:border-accent mono"
                        />
                        <input
                            type="number"
                            step="0.1"
                            placeholder="P/E"
                            value={newComp.pe}
                            onChange={(e) => setNewComp((prev) => ({ ...prev, pe: e.target.value }))}
                            className="bg-surface border border-border-default rounded px-3 py-2 text-[12px] text-txt-primary focus:outline-none focus:border-accent mono"
                        />
                    </div>
                    <div className="mt-3 flex items-center gap-3">
                        <button
                            onClick={handleAddPeer}
                            className="px-4 py-1.5 rounded bg-accent text-white text-[12px] font-semibold hover:bg-accent-hover transition-colors"
                        >
                            Add Peer
                        </button>
                        {formError && <span className="text-[11px] text-neg-DEFAULT">{formError}</span>}
                    </div>
                </div>

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
                                {compsWithMultiples.map((c) => (
                                    <tr key={c.id} className="border-b border-border-subtle/50 hover:bg-surface/20 transition-colors">
                                        <td className="px-4 py-2">
                                            <input
                                                type="text"
                                                value={c.name}
                                                onChange={(e) => handleCompTextChange(c.id, 'name', e.target.value)}
                                                className="w-52 bg-surface border border-border-default rounded px-2 py-1 text-[12px] text-txt-primary focus:outline-none focus:border-accent"
                                            />
                                        </td>
                                        <td className="px-4 py-2">
                                            <input
                                                type="text"
                                                value={c.ticker}
                                                onChange={(e) => handleCompTextChange(c.id, 'ticker', e.target.value)}
                                                className="w-20 bg-surface border border-border-default rounded px-2 py-1 text-[12px] text-txt-secondary focus:outline-none focus:border-accent uppercase mono"
                                            />
                                        </td>
                                        <td className="px-4 py-2">
                                            <input
                                                type="number"
                                                step="0.1"
                                                value={c.ev}
                                                onChange={(e) => handleCompNumberChange(c.id, 'ev', e.target.value)}
                                                className="w-28 bg-surface border border-border-default rounded px-2 py-1 text-[12px] text-right text-txt-secondary focus:outline-none focus:border-accent mono"
                                            />
                                        </td>
                                        <td className="px-4 py-2">
                                            <input
                                                type="number"
                                                step="0.1"
                                                value={c.rev}
                                                onChange={(e) => handleCompNumberChange(c.id, 'rev', e.target.value)}
                                                className="w-28 bg-surface border border-border-default rounded px-2 py-1 text-[12px] text-right text-txt-secondary focus:outline-none focus:border-accent mono"
                                            />
                                        </td>
                                        <td className="px-4 py-2">
                                            <input
                                                type="number"
                                                step="0.1"
                                                value={c.ebitda}
                                                onChange={(e) => handleCompNumberChange(c.id, 'ebitda', e.target.value)}
                                                className="w-28 bg-surface border border-border-default rounded px-2 py-1 text-[12px] text-right text-txt-secondary focus:outline-none focus:border-accent mono"
                                            />
                                        </td>
                                        <td className="px-4 py-2 mono text-right text-txt-primary font-medium border-l border-border-subtle bg-accent/5">
                                            {c.evRev.toFixed(1)}x
                                        </td>
                                        <td className="px-4 py-2 mono text-right text-txt-primary font-medium bg-accent/5">
                                            {c.evEbitda.toFixed(1)}x
                                        </td>
                                        <td className="px-4 py-2">
                                            <input
                                                type="number"
                                                step="0.1"
                                                value={c.pe}
                                                onChange={(e) => handleCompNumberChange(c.id, 'pe', e.target.value)}
                                                className="w-24 bg-surface border border-border-default rounded px-2 py-1 text-[12px] text-right text-txt-primary font-medium focus:outline-none focus:border-accent mono"
                                            />
                                        </td>
                                        <td className="px-4 py-2 text-right">
                                            <button
                                                onClick={() => handleRemovePeer(c.id)}
                                                className="text-[11px] text-txt-muted hover:text-neg-DEFAULT transition-colors"
                                            >
                                                Remove
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {compsWithMultiples.length === 0 && (
                                    <tr>
                                        <td colSpan={9} className="px-4 py-6 text-center text-[12px] text-txt-muted">
                                            No peers available. Add one above to start testing.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
                    <div className="bg-panel rounded-lg border border-border-subtle p-6">
                        <h2 className="text-[14px] font-semibold text-txt-primary mb-4">Summary Statistics</h2>
                        <table className="w-full text-[12px] whitespace-nowrap">
                            <thead>
                                <tr className="border-b border-border-subtle bg-surface/50">
                                    <th className="text-left px-4 py-2 font-semibold text-txt-secondary uppercase tracking-wider text-[10px]">Metric</th>
                                    <th className="text-right px-4 py-2 font-semibold text-txt-secondary uppercase tracking-wider text-[10px]">EV / Rev</th>
                                    <th className="text-right px-4 py-2 font-semibold text-txt-secondary uppercase tracking-wider text-[10px]">EV / EBITDA</th>
                                </tr>
                            </thead>
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

                    <div className="bg-panel rounded-lg border border-border-subtle overflow-hidden">
                        <div className="px-4 py-3 border-b border-border-subtle flex justify-between items-center">
                            <h2 className="text-[13px] font-semibold text-txt-primary">Implied Valuation (Subject Co)</h2>
                            <span className="text-[10px] text-txt-muted uppercase tracking-wider">Using median EV / EBITDA</span>
                        </div>
                        <div className="p-4 space-y-4">
                            <div className="grid grid-cols-2 gap-2">
                                <input
                                    type="text"
                                    value={subject.ticker}
                                    onChange={(e) => handleSubjectTextChange('ticker', e.target.value)}
                                    className="bg-surface border border-border-default rounded px-3 py-1.5 text-[12px] text-txt-primary focus:outline-none focus:border-accent uppercase mono"
                                    placeholder="Ticker"
                                />
                                <input
                                    type="text"
                                    value={subject.name}
                                    onChange={(e) => handleSubjectTextChange('name', e.target.value)}
                                    className="bg-surface border border-border-default rounded px-3 py-1.5 text-[12px] text-txt-primary focus:outline-none focus:border-accent"
                                    placeholder="Company Name"
                                />
                                <input
                                    type="number"
                                    step="0.1"
                                    value={subject.rev}
                                    onChange={(e) => handleSubjectNumberChange('rev', e.target.value)}
                                    className="bg-surface border border-border-default rounded px-3 py-1.5 text-[12px] text-txt-primary focus:outline-none focus:border-accent mono"
                                    placeholder="LTM Revenue ($M)"
                                />
                                <input
                                    type="number"
                                    step="0.1"
                                    value={subject.ebitda}
                                    onChange={(e) => handleSubjectNumberChange('ebitda', e.target.value)}
                                    className="bg-surface border border-border-default rounded px-3 py-1.5 text-[12px] text-txt-primary focus:outline-none focus:border-accent mono"
                                    placeholder="LTM EBITDA ($M)"
                                />
                                <input
                                    type="number"
                                    step="0.1"
                                    value={subject.shares}
                                    onChange={(e) => handleSubjectNumberChange('shares', e.target.value)}
                                    className="bg-surface border border-border-default rounded px-3 py-1.5 text-[12px] text-txt-primary focus:outline-none focus:border-accent mono"
                                    placeholder="Diluted Shares (M)"
                                />
                                <input
                                    type="number"
                                    step="0.1"
                                    value={subject.netDebt}
                                    onChange={(e) => handleSubjectNumberChange('netDebt', e.target.value)}
                                    className="bg-surface border border-border-default rounded px-3 py-1.5 text-[12px] text-txt-primary focus:outline-none focus:border-accent mono"
                                    placeholder="Net Debt ($M)"
                                />
                            </div>

                            <div className="flex justify-between items-center pb-2 border-b border-border-subtle/50">
                                <span className="text-[12px] text-txt-secondary">Subject LTM EBITDA</span>
                                <span className="mono text-[13px] text-txt-primary">${subject.ebitda.toFixed(1)}M</span>
                            </div>
                            <div className="flex justify-between items-center pb-2 border-b border-border-subtle/50">
                                <span className="text-[12px] text-txt-secondary">x Peer Median Multiple</span>
                                <span className="mono text-[13px] text-accent font-semibold">{stats.median.evEbitda.toFixed(1)}x</span>
                            </div>
                            <div className="flex justify-between items-center pb-2 border-b border-border-subtle/50">
                                <span className="text-[12px] font-medium text-txt-primary">Implied Enterprise Value</span>
                                <span className="mono text-[14px] font-bold text-txt-primary">${impliedEv.toLocaleString()}M</span>
                            </div>
                            <div className="flex justify-between items-center pb-2 border-b border-border-subtle/50">
                                <span className="text-[12px] text-txt-secondary">- Net Debt</span>
                                <span className="mono text-[13px] text-neg-DEFAULT">(${subject.netDebt.toFixed(1)}M)</span>
                            </div>
                            <div className="flex justify-between items-center pt-2">
                                <div className="flex flex-col">
                                    <span className="text-[13px] font-bold text-txt-primary">Implied Share Price</span>
                                    <span className="text-[10px] text-txt-muted">{subject.shares.toFixed(1)}M diluted shares</span>
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
