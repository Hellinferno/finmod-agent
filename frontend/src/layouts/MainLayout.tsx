import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, FileUp, Database, Settings, BarChart3, TrendingUp, Activity, FileCheck, Download } from 'lucide-react';

export default function MainLayout() {
    return (
        <div className="bg-base text-txt-primary min-h-screen">
            {/* TOPBAR */}
            <header className="fixed top-0 left-0 right-0 z-50 h-14 bg-panel border-b border-border-subtle flex items-center px-4 gap-4">
                <div className="flex items-center gap-2 shrink-0 w-[220px]">
                    <div className="w-7 h-7 rounded bg-accent flex items-center justify-center">
                        <span className="mono text-white font-bold text-[11px]">FV</span>
                    </div>
                    <span className="font-semibold text-[13px] text-txt-primary">FMVA</span>
                    <span className="text-border-default text-[10px] mono ml-1">v1.0</span>
                </div>
                <div className="flex items-center gap-0 ml-6 flex-1">
                    <div className="flex items-center gap-0 text-[11px]">
                        <TopLink to="/ingest" label="Ingest" />
                        <TopDivider />
                        <TopLink to="/assumptions" label="Configure" />
                        <TopDivider />
                        <TopLink to="/dcf" label="DCF" />
                        <TopDivider />
                        <TopLink to="/sensitivity" label="Sensitivity" />
                        <TopDivider />
                        <TopLink to="/export" label="Export" />
                    </div>
                </div>
            </header>

            {/* LAYOUT */}
            <div className="flex pt-14 h-screen">
                {/* SIDEBAR */}
                <aside className="w-[240px] shrink-0 bg-panel border-r border-border-subtle flex flex-col pt-4 overflow-y-auto">
                    <div className="px-4 pb-4 border-b border-border-subtle">
                        <div className="text-[10px] text-txt-muted uppercase tracking-widest font-medium mb-1">FMVA Platform</div>
                        <div className="text-[14px] font-semibold text-txt-primary">Dashboard</div>
                        <div className="text-[11px] text-txt-muted mt-0.5">Overview & Quick Actions</div>
                    </div>

                    <nav className="px-2 py-4 space-y-1 flex-1">
                        <SidebarLink to="/" icon={<LayoutDashboard size={16} />} label="Dashboard" />
                        <SidebarLink to="/ingest" icon={<FileUp size={16} />} label="Data Ingestion" />
                        <SidebarLink to="/model" icon={<Database size={16} />} label="3-Statement Model" badge="Soon" />
                        <SidebarLink to="/assumptions" icon={<Settings size={16} />} label="Assumptions" />
                        <SidebarLink to="/dcf" icon={<BarChart3 size={16} />} label="DCF Valuation" />
                        <SidebarLink to="/comps" icon={<TrendingUp size={16} />} label="Trading Comps" badge="Soon" />
                        <SidebarLink to="/sensitivity" icon={<Activity size={16} />} label="Sensitivity" badge="Soon" />

                        <div className="border-t border-border-subtle my-2 mx-2"></div>
                        <div className="text-[10px] text-txt-muted uppercase tracking-widest font-medium px-2 mb-1 mt-2">Quality</div>

                        <SidebarLink to="/audit" icon={<FileCheck size={16} />} label="Audit Trail" badge="Soon" />
                        <SidebarLink to="/export" icon={<Download size={16} />} label="Export" badge="Soon" />
                    </nav>

                    {/* Session Footer */}
                    <div className="px-4 py-3 border-t border-border-subtle">
                        <div className="text-[10px] text-txt-muted mb-1.5">Session · <span className="mono">2026-02-23</span></div>
                        <div className="flex items-center justify-between">
                            <div className="text-[11px] text-txt-secondary">Status: <span className="text-pos-DEFAULT">Ready</span></div>
                            <div className="text-[10px] mono text-txt-muted">v1.0</div>
                        </div>
                    </div>
                </aside>

                {/* MAIN CONTENT AREA */}
                <main className="flex-1 overflow-y-auto bg-base">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}

const TopLink = ({ to, label }: { to: string; label: string }) => (
    <NavLink
        to={to}
        className={({ isActive }) =>
            `flex items-center gap-1.5 px-3 py-1 rounded-sm border transition-colors ${isActive
                ? 'bg-accent-subtle border-accent text-accent font-semibold'
                : 'bg-surface border-border-subtle text-txt-muted hover:bg-accent-subtle'
            }`
        }
    >
        <span className="w-1.5 h-1.5 rounded-full bg-border-default"></span>
        <span>{label}</span>
    </NavLink>
);

const TopDivider = () => <div className="w-6 h-px bg-border-subtle flex-shrink-0"></div>;

const SidebarLink = ({ to, icon, label, badge }: { to: string; icon: React.ReactNode; label: string; badge?: string }) => (
    <NavLink
        to={to}
        className={({ isActive }) =>
            `flex items-center gap-2.5 px-3 py-2 rounded text-[13px] transition-colors ${isActive
                ? 'bg-accent-subtle border-l-2 border-accent text-accent font-medium'
                : 'text-txt-secondary hover:bg-surface hover:text-txt-primary'
            }`
        }
    >
        <div className="shrink-0">{icon}</div>
        <span>{label}</span>
        {badge && (
            <span className="ml-auto px-1.5 py-0.5 rounded-full bg-accent-subtle text-accent text-[9px] mono">{badge}</span>
        )}
    </NavLink>
);
