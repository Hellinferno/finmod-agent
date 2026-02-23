# FMVA — UI/UX Design Specification
**Version:** 1.0 | **Date:** 2026-02-23 | **Owner:** Product Design

---

## 1. Design Direction

**Aesthetic:** Clean Professional — Minimalist
**Tone:** Industry-grade, functional UI with White/Black/Light Blue palette. Maximum information density served with surgical precision. Every pixel earns its place.
**Target Persona:** Investment banking analyst who lives in Excel, Bloomberg, and pitch decks. Expects density, speed, and zero tolerance for ambiguity.

---

## 2. Design Token Table

### 2.1 Color Palette

| Token Name                | Hex       | Usage                                   |
|---------------------------|-----------|-----------------------------------------|
| `--color-bg-base`         | `#FFFFFF` | App background (root)                   |
| `--color-bg-panel`        | `#F8FAFC` | Sidebar, card backgrounds               |
| `--color-bg-surface`      | `#F1F5F9` | Inputs, table rows                      |
| `--color-bg-elevated`     | `#FFFFFF` | Modals, dropdowns, tooltips             |
| `--color-border-subtle`   | `#E2E8F0` | Default borders                         |
| `--color-border-default`  | `#CBD5E1` | Focused borders, dividers               |
| `--color-text-primary`    | `#0F172A` | Headings, primary labels                |
| `--color-text-secondary`  | `#475569` | Subtext, descriptions                   |
| `--color-text-muted`      | `#94A3B8` | Placeholder, timestamps                 |
| `--color-accent-primary`  | `#3B82F6` | CTA buttons, active states, highlights  |
| `--color-accent-hover`    | `#2563EB` | Accent on hover                         |
| `--color-accent-subtle`   | `#EFF6FF` | Accent backgrounds (tinted)             |
| `--color-positive`        | `#22C55E` | Positive values, gains, pass states     |
| `--color-positive-bg`     | `#F0FDF4` | Positive value backgrounds              |
| `--color-negative`        | `#EF4444` | Negative values, losses, errors         |
| `--color-negative-bg`     | `#FEF2F2` | Error backgrounds                       |
| `--color-warning`         | `#F59E0B` | Warning states, flags                   |
| `--color-warning-bg`      | `#FFFBEB` | Warning backgrounds                     |
| `--color-info`            | `#3B82F6` | Informational elements                  |
| `--color-info-bg`         | `#EFF6FF` | Info backgrounds                        |
| `--color-input-blue`      | `#2563EB` | Hard-coded input cells (IB convention)  |
| `--color-formula-black`   | `#0F172A` | Formula-driven cells                    |
| `--color-output-green`    | `#16A34A` | Output/result cells                     |

### 2.2 Typography Scale

| Token                      | Font                 | Size    | Weight | Line Height | Usage                         |
|----------------------------|----------------------|---------|--------|-------------|-------------------------------|
| `--type-display-xl`        | JetBrains Mono       | 32px    | 700    | 1.2         | Hero numbers, EV/Share Price  |
| `--type-display-lg`        | JetBrains Mono       | 24px    | 600    | 1.3         | Section totals, key metrics   |
| `--type-heading-xl`        | IBM Plex Sans        | 20px    | 600    | 1.4         | Page titles                   |
| `--type-heading-lg`        | IBM Plex Sans        | 16px    | 600    | 1.4         | Card headers, section titles  |
| `--type-heading-sm`        | IBM Plex Sans        | 13px    | 600    | 1.4         | Table headers, labels         |
| `--type-body-md`           | IBM Plex Sans        | 14px    | 400    | 1.6         | Body text, descriptions       |
| `--type-body-sm`           | IBM Plex Sans        | 12px    | 400    | 1.5         | Secondary text, helper text   |
| `--type-data-lg`           | JetBrains Mono       | 14px    | 400    | 1.4         | Table cell values             |
| `--type-data-md`           | JetBrains Mono       | 12px    | 400    | 1.4         | Dense table data              |
| `--type-data-sm`           | JetBrains Mono       | 11px    | 400    | 1.4         | Micro labels, unit suffixes   |
| `--type-label`             | IBM Plex Sans        | 11px    | 500    | 1.0         | Tags, badges, status pills    |
| `--type-code`              | JetBrains Mono       | 12px    | 400    | 1.6         | Formulas, audit trail         |

### 2.3 Spacing Scale (8px Base System)

| Token        | Value | Usage                                       |
|--------------|-------|---------------------------------------------|
| `--space-1`  | 4px   | Icon padding, tight gaps                    |
| `--space-2`  | 8px   | Component internal padding (compact)        |
| `--space-3`  | 12px  | Form element padding, cell padding          |
| `--space-4`  | 16px  | Standard card padding, section spacing      |
| `--space-5`  | 20px  | Generous internal spacing                   |
| `--space-6`  | 24px  | Between cards, section gaps                 |
| `--space-8`  | 32px  | Major section breaks                        |
| `--space-10` | 40px  | Page section vertical rhythm                |
| `--space-12` | 48px  | Hero/header areas                           |

### 2.4 Grid System

- **Columns:** 12
- **Gutter:** 16px
- **Margin (Desktop):** 24px
- **Max Content Width:** 1440px
- **Breakpoints:** sm=640, md=768, lg=1024, xl=1280, 2xl=1440

### 2.5 Border Radius Scale

| Token      | Value | Usage                                    |
|------------|-------|------------------------------------------|
| `--r-sm`   | 4px   | Inputs, table cells, tags                |
| `--r-md`   | 6px   | Cards, panels, buttons                   |
| `--r-lg`   | 8px   | Modals, drawers                          |
| `--r-xl`   | 12px  | Sheets, overlays                         |
| `--r-full` | 9999px| Pills, status badges                     |

---

## 3. Sitemap / Page Architecture

```
FMVA Application
│
├── / — Dashboard (Overview)
│   ├── Recent Valuations
│   ├── Active Session Summary
│   └── Quick Actions
│
├── /ingest — Data Ingestion
│   ├── File Upload Zone
│   ├── Raw Data Preview
│   ├── Normalization Review
│   └── Balance Sheet Check
│
├── /assumptions — Assumption Engine
│   ├── Scenario Manager (Bear/Base/Bull)
│   ├── Driver Sliders
│   └── Saved Assumption Sets
│
├── /model — 3-Statement Model
│   ├── Income Statement
│   ├── Balance Sheet
│   ├── Cash Flow Statement
│   └── Integrity Check Status
│
├── /dcf — DCF Valuation
│   ├── UFCF Projections Table
│   ├── Terminal Value (GG + EM)
│   ├── EV / Equity Bridge
│   └── Key Metrics Summary
│
├── /comps — Comparable Companies
│   ├── Comp Set Input
│   ├── Trading Multiples Table
│   └── Implied Valuation Range
│
├── /sensitivity — Sensitivity Analysis
│   ├── WACC vs. TGR Matrix
│   ├── WACC vs. Exit Multiple Matrix
│   └── Football Field Chart
│
├── /audit — Audit Trail
│   ├── Calculation Log
│   ├── Integrity Check Results
│   └── Error/Warning Log
│
└── /export — Export & Reports
    ├── Excel Export
    ├── JSON Export
    ├── PDF Report
    └── Executive Summary (LLM)
```

---

## 4. Layout Grid Specifications

### 4.1 App Shell Layout

```
┌─────────────────────────────────────────────────┐
│ TOPBAR (56px fixed)                             │
├───────────────┬─────────────────────────────────┤
│               │                                 │
│  SIDEBAR      │  MAIN CONTENT AREA              │
│  (240px fixed)│  (fluid, 16px padding)          │
│               │                                 │
│  Primary Nav  │  ┌──────────────────────────┐   │
│  Pipeline     │  │ PAGE HEADER (64px)        │   │
│  Steps        │  ├──────────────────────────┤   │
│               │  │                          │   │
│  ─────────    │  │ CONTENT GRID (12-col)    │   │
│               │  │                          │   │
│  Help         │  │                          │   │
│  Settings     │  └──────────────────────────┘   │
│               │                                 │
└───────────────┴─────────────────────────────────┘
```

### 4.2 DCF Screen Layout (Key screen — high density)

```
┌──────────────────────────────────────────────────────┐
│ PAGE HEADER: "DCF Valuation — TechCorp Inc."         │
│ [Scenario: Base ▼]  [Periods: 5yr ▼]  [Run DCF ▶]   │
├─────────────────────────────────────────────────────┤
│ METRIC SUMMARY BAR (full width)                      │
│ [EV $1,102M] [Equity Value $952M] [$/Share $9.52]    │
│ [TV% 71.4%] [WACC 10%] [TGR 2.5%]                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────────────┐ ┌────────────────────┐  │
│  │ UFCF PROJECTION TABLE   │ │ TERMINAL VALUE     │  │
│  │ (9 cols × 10 rows)      │ │ GG: $931.7M        │  │
│  │ Year | Rev | EBITDA...  │ │ EM: $2,206.8M      │  │
│  └─────────────────────────┘ └────────────────────┘  │
│                                                      │
│  ┌─────────────────────────────────────────────────┐  │
│  │ EV / EQUITY VALUE BRIDGE (waterfall chart)      │  │
│  └─────────────────────────────────────────────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 5. Component Library (Figma Components Needed)

### 5.1 Navigation Components
- `Topbar` — Logo, breadcrumb, session status, export button, user menu
- `Sidebar` — Nav item (default/active/hover), section divider, pipeline step indicator
- `PipelineProgress` — Horizontal step tracker (Ingest → Normalize → Configure → Compute → Export)

### 5.2 Data Display Components
- `MetricCard` — Label, value (large mono), delta, unit badge [States: default, positive, negative, warning]
- `MetricBar` — Full-width row of 4–6 MetricCards
- `DataTable` — Header row, data row (default/hover/selected), sticky header, sortable columns
- `DataTableCell` — type: input (blue), formula (white), output (green), error (red)
- `SensitivityMatrix` — Grid cell with gradient fill (green/red), base case highlight
- `FootballFieldBar` — Horizontal bar with min/max/base range
- `AuditRow` — step name, formula (monospace), inputs, output, timestamp

### 5.3 Input Components
- `TextInput` — Default, Focus, Error, Disabled states
- `NumberInput` — With unit suffix (%, $, x), increment arrows
- `SliderInput` — Track, thumb, value tooltip, range labels
- `DropdownSelect` — Default, open, selected states
- `FileDropzone` — Idle, dragover, success, error states
- `ScenarioToggle` — Bear/Base/Bull segmented control

### 5.4 Feedback Components
- `StatusPill` — PASS (green), FAIL (red), WARNING (amber), PENDING (blue) [with icon]
- `AlertBanner` — Error, Warning, Info, Success variants
- `ProgressBar` — Pipeline execution progress
- `TooltipFormula` — Appears on hover of computed cell, shows formula + source values

### 5.5 Layout Components
- `PageHeader` — Title, subtitle, action bar (right-aligned CTAs)
- `SectionCard` — Title, subtitle, content slot, optional footer
- `SectionDivider` — Label + horizontal rule
- `EmptyState` — Icon, heading, description, CTA button
- `LoadingOverlay` — Spinner, status message for long operations

### 5.6 Action Components
- `ButtonPrimary` — Light Blue fill, white text [Default, Hover, Loading, Disabled]
- `ButtonSecondary` — Outlined, light blue border [Default, Hover, Disabled]
- `ButtonGhost` — Text only, subtle hover background
- `IconButton` — Icon only, 32px/36px variants
- `ExportButton` — With format selector (XLSX/JSON/PDF)

---

## 6. Visual Hierarchy Rules

### 6.1 Primary Information (High Contrast — `--color-text-primary`)
- Enterprise Value, Equity Value, Implied Share Price
- Balance sheet totals (Assets, Liabilities+Equity)
- Pass/Fail status of integrity checks
- Current scenario name
- Error messages

### 6.2 Secondary Information (`--color-text-secondary`)
- Column headers in data tables
- Section labels
- Intermediate calculation values
- Comp company names

### 6.3 Tertiary Information (`--color-text-muted`)
- Timestamps, version numbers
- Formula strings in audit trail
- Placeholder text
- Currency units (e.g., "$M")

### 6.4 Color Encoding (IB Convention — Never Deviate)
- **Blue text (#2563EB):** Hard-coded user inputs
- **Black text (#0F172A):** Formula-driven cells
- **Green text (#16A34A):** Output/summary values
- **Red text (#EF4444):** Errors, negative values, balance sheet failures
- **Light Blue text (#3B82F6):** Accent, active states, user attention

---

## 7. Interaction Patterns

### 7.1 Inline Editing
- Click any input cell to edit in-place
- Tab/Enter to confirm and advance
- Escape to cancel
- Real-time downstream recalculation on blur

### 7.2 Assumption Propagation
- Changing any driver shows a "Recalculating..." pulse animation on dependent sections
- Changed cells briefly highlight in amber before returning to normal

### 7.3 Error States
- Balance sheet errors: entire BS table row highlighted in `--color-negative-bg`
- Blocking errors: red banner with specific resolution instructions
- Non-blocking warnings: amber inline badge next to affected value

### 7.4 Audit Trail Tooltips
- Hover any computed value → tooltip shows formula, source inputs, result
- Tooltip background: `--color-bg-elevated`
- Monospace formula display
