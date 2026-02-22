"""
Precedent transactions analysis engine.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import numpy as np
from loguru import logger
from fmva.audit.trail import AuditTrail
from fmva.core.schemas import Transaction, TransactionResult


def parse_transaction_table(filepath: str) -> list[Transaction]:
    """Load precedent transactions from JSON or CSV."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Transaction file not found: {filepath}")

    if path.suffix.lower() == ".json":
        with open(path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            txns = data
        elif isinstance(data, dict) and "transactions" in data:
            txns = data["transactions"]
        else:
            raise ValueError("JSON must be a list of transactions or have a 'transactions' key")
    elif path.suffix.lower() == ".csv":
        import pandas as pd
        df = pd.read_csv(path)
        txns = df.to_dict(orient="records")
    else:
        raise ValueError(f"Unsupported format: {path.suffix}")

    transactions = []
    for t in txns:
        ev = float(t.get("enterprise_value", t.get("ev", 0)))
        rev = t.get("target_revenue", t.get("revenue"))
        ebitda = t.get("target_ebitda", t.get("ebitda"))
        ev_ebitda = ev / float(ebitda) if ebitda and float(ebitda) > 0 else None
        ev_rev = ev / float(rev) if rev and float(rev) > 0 else None

        transactions.append(Transaction(
            target=t.get("target", "Unknown"),
            acquirer=t.get("acquirer"),
            date=t.get("date"),
            enterprise_value=ev,
            target_revenue=float(rev) if rev else None,
            target_ebitda=float(ebitda) if ebitda else None,
            ev_ebitda=ev_ebitda,
            ev_revenue=ev_rev,
            premium_to_unaffected=t.get("premium"),
        ))
    logger.info(f"Parsed {len(transactions)} precedent transactions from {filepath}")
    return transactions


def calculate_transaction_stats(transactions: list[Transaction]) -> dict[str, dict[str, float | None]]:
    """Calculate min, median, mean, max for transaction multiples."""
    ev_ebitda = [t.ev_ebitda for t in transactions if t.ev_ebitda is not None]
    ev_rev = [t.ev_revenue for t in transactions if t.ev_revenue is not None]

    def _stats(vals):
        if not vals:
            return {"min": None, "median": None, "mean": None, "max": None}
        a = np.array(vals)
        return {"min": float(a.min()), "median": float(np.median(a)),
                "mean": float(a.mean()), "max": float(a.max())}

    return {"ev_ebitda": _stats(ev_ebitda), "ev_revenue": _stats(ev_rev)}


def apply_transaction_multiples(
    transactions: list[Transaction],
    target_ebitda: float, target_revenue: float,
    audit: AuditTrail = None,
) -> TransactionResult:
    """Apply precedent transaction median multiples to target metrics."""
    if audit is None:
        audit = AuditTrail()
    stats = calculate_transaction_stats(transactions)
    med_ebitda = stats["ev_ebitda"].get("median")
    med_rev = stats["ev_revenue"].get("median")

    implied_ev_ebitda = med_ebitda * target_ebitda if med_ebitda else None
    implied_ev_rev = med_rev * target_revenue if med_rev else None

    if implied_ev_ebitda:
        audit.log("Implied EV (Txn EV/EBITDA)", "EV = med_mult × EBITDA",
                  {"mult": med_ebitda, "EBITDA": target_ebitda}, implied_ev_ebitda, "$M", "transactions")
    if implied_ev_rev:
        audit.log("Implied EV (Txn EV/Rev)", "EV = med_mult × Rev",
                  {"mult": med_rev, "Rev": target_revenue}, implied_ev_rev, "$M", "transactions")

    return TransactionResult(
        transactions=transactions, stats=stats,
        implied_ev_ebitda_median=implied_ev_ebitda,
        implied_ev_revenue_median=implied_ev_rev,
    )
