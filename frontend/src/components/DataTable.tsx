import React from 'react';

interface DataTableProps {
    title?: string;
    subtitle?: string;
    headers: string[];
    children: React.ReactNode;
}

export default function DataTable({ title, subtitle, headers, children }: DataTableProps) {
    return (
        <div className="bg-panel rounded-lg border border-border-subtle overflow-hidden">
            {(title || subtitle) && (
                <div className="px-4 py-3 border-b border-border-subtle">
                    {title && <h2 className="text-[13px] font-semibold text-txt-primary">{title}</h2>}
                    {subtitle && <div className="text-[11px] text-txt-muted mt-0.5">{subtitle}</div>}
                </div>
            )}
            <div className="overflow-x-auto">
                <table className="w-full text-[11px]">
                    <thead className="bg-surface/50 border-b border-border-subtle">
                        <tr>
                            {headers.map((header, idx) => (
                                <th key={idx} className={`px-4 py-2 font-medium text-txt-secondary ${idx === 0 ? 'text-left' : 'text-right'}`}>
                                    {header}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border-subtle/50">
                        {children}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
