"""
Comparable company analysis engine — fetch data via yfinance, compute multiples & stats.
"""

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import numpy as np
from loguru import logger
from fmva.audit.trail import AuditTrail
from fmva.config import MIN_COMPARABLE_COMPANIES, OUTLIER_SIGMA_THRESHOLD, YFINANCE_CACHE_TTL_HOURS
from fmva.core.schemas import CompData, CompsResult, CompsStats


def _get_cache_path(ticker: str, cache_dir: str = None) -> Path:
    cache = Path(cache_dir or "data/cache/yfinance")
    cache.mkdir(parents=True, exist_ok=True)
    return cache / f"{ticker.upper()}.json"


def _load_cache(ticker: str, cache_dir: str = None) -> Optional[dict]:
    path = _get_cache_path(ticker, cache_dir)
    if path.exists():
        data = json.loads(path.read_text())
        cached_at = datetime.fromisoformat(data.get("_cached_at", "2000-01-01"))
        if datetime.utcnow() - cached_at < timedelta(hours=YFINANCE_CACHE_TTL_HOURS):
            return data
    return None


def _save_cache(ticker: str, data: dict, cache_dir: str = None):
    data["_cached_at"] = datetime.utcnow().isoformat()
    path = _get_cache_path(ticker, cache_dir)
    path.write_text(json.dumps(data, default=str))


def fetch_comp_data(
    tickers: list[str], cache_dir: str = None,
) -> list[CompData]:
    """Fetch financial data for comparable companies via yfinance with Drive caching."""
    comps = []
    for ticker in tickers:
        cached = _load_cache(ticker, cache_dir)
        if cached:
            info = cached
        else:
            try:
                import yfinance as yf
                stock = yf.Ticker(ticker)
                info = stock.info or {}
                _save_cache(ticker, info, cache_dir)
            except Exception as e:
                logger.warning(f"Failed to fetch {ticker}: {e}")
                continue

        mc = info.get("marketCap")
        ev = info.get("enterpriseValue")
        rev = info.get("totalRevenue")
        ebitda = info.get("ebitda")
        ni = info.get("netIncomeToCommon")

        if mc: mc = mc / 1e6
        if ev: ev = ev / 1e6
        if rev: rev = rev / 1e6
        if ebitda: ebitda = ebitda / 1e6
        if ni: ni = ni / 1e6

        ev_ebitda = ev / ebitda if ev and ebitda and ebitda > 0 else None
        ev_rev = ev / rev if ev and rev and rev > 0 else None
        pe = mc / ni if mc and ni and ni > 0 else None

        comps.append(CompData(
            ticker=ticker, company_name=info.get("shortName", ticker),
            market_cap=mc, enterprise_value=ev, revenue_ltm=rev,
            ebitda_ltm=ebitda, net_income_ltm=ni,
            ev_ebitda=ev_ebitda, ev_revenue=ev_rev, pe_ratio=pe,
        ))
    logger.info(f"Fetched comp data for {len(comps)}/{len(tickers)} companies")
    return comps


def calculate_comps_stats(
    comps: list[CompData], sigma: float = OUTLIER_SIGMA_THRESHOLD,
) -> CompsStats:
    """Calculate min, 25th, median, 75th, max for each multiple with outlier exclusion."""
    if len(comps) < MIN_COMPARABLE_COMPANIES:
        logger.warning(
            f"Peer set has {len(comps)} companies; recommended minimum is {MIN_COMPARABLE_COMPANIES}"
        )
    multiples_data = {"ev_ebitda": [], "ev_revenue": [], "pe_ratio": []}
    for c in comps:
        if c.ev_ebitda is not None: multiples_data["ev_ebitda"].append(c.ev_ebitda)
        if c.ev_revenue is not None: multiples_data["ev_revenue"].append(c.ev_revenue)
        if c.pe_ratio is not None: multiples_data["pe_ratio"].append(c.pe_ratio)

    stats = {}
    excluded = 0
    for name, values in multiples_data.items():
        if len(values) < 2:
            stats[name] = {"min": None, "p25": None, "median": None, "p75": None, "max": None}
            continue
        arr = np.array(values)
        mean, std = arr.mean(), arr.std()
        mask = np.abs(arr - mean) <= sigma * std
        excluded += int((~mask).sum())
        filtered = arr[mask]
        if len(filtered) == 0:
            filtered = arr
        stats[name] = {
            "min": float(np.min(filtered)), "p25": float(np.percentile(filtered, 25)),
            "median": float(np.median(filtered)), "p75": float(np.percentile(filtered, 75)),
            "max": float(np.max(filtered)),
        }
    return CompsStats(multiples=stats, n_companies=len(comps), n_excluded_outliers=excluded)


def apply_comps_multiples(
    stats: CompsStats, target_ebitda: float, target_revenue: float,
    comps: list[CompData] | None = None,
    audit: AuditTrail = None,
) -> CompsResult:
    """Apply median comp multiples to target company's EBITDA/revenue for implied EV range."""
    if audit is None:
        audit = AuditTrail()
    ev_ebitda = stats.multiples.get("ev_ebitda", {})
    ev_rev = stats.multiples.get("ev_revenue", {})

    def _implied(mult, metric, label):
        if mult:
            v = mult * metric
            audit.log(f"Implied EV ({label})", f"EV = {label}_mult × metric",
                      {"multiple": mult, "metric": metric}, v, "$M", "comps")
            return v
        return None

    return CompsResult(
        comps=comps or [],
        stats=stats,
        implied_ev_ebitda_low=_implied(ev_ebitda.get("p25"), target_ebitda, "EV/EBITDA_p25"),
        implied_ev_ebitda_median=_implied(ev_ebitda.get("median"), target_ebitda, "EV/EBITDA_med"),
        implied_ev_ebitda_high=_implied(ev_ebitda.get("p75"), target_ebitda, "EV/EBITDA_p75"),
        implied_ev_revenue_low=_implied(ev_rev.get("p25"), target_revenue, "EV/Rev_p25"),
        implied_ev_revenue_median=_implied(ev_rev.get("median"), target_revenue, "EV/Rev_med"),
        implied_ev_revenue_high=_implied(ev_rev.get("p75"), target_revenue, "EV/Rev_p75"),
    )
