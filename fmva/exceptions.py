"""
Custom exception hierarchy for the FMVA system.

All FMVA exceptions inherit from FMVAError.
Each module has its own exception type for precise error handling.
"""


class FMVAError(Exception):
    """Base exception for all FMVA errors."""

    def __init__(self, message: str, error_code: str = "FMVA_GENERIC", details: dict = None):
        self.error_code = error_code
        self.details = details or {}
        super().__init__(f"[{error_code}] {message}")


# ── Ingestion Errors ───────────────────────────────────────────────────────────


class IngestionError(FMVAError):
    """Raised when data cannot be loaded or parsed."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, error_code="INGESTION_ERROR", details=details)


class FileFormatError(IngestionError):
    """Raised for unsupported or malformed file formats."""

    def __init__(self, message: str, details: dict = None):
        FMVAError.__init__(self, message, error_code="FILE_FORMAT_ERROR", details=details)


# ── Normalization Errors ───────────────────────────────────────────────────────


class NormalizationError(FMVAError):
    """Raised when field mapping or normalization fails."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, error_code="NORMALIZATION_ERROR", details=details)


class FieldMappingError(NormalizationError):
    """Raised when a required field cannot be mapped to the canonical schema."""

    def __init__(self, field_name: str, available_fields: list[str] = None):
        details = {"field": field_name, "available": available_fields or []}
        FMVAError.__init__(
            self,
            f"Cannot map field: '{field_name}'",
            error_code="FIELD_MAPPING_ERROR",
            details=details,
        )


# ── Validation Errors ──────────────────────────────────────────────────────────


class ValidationError(FMVAError):
    """Raised when normalized data fails integrity checks."""

    def __init__(
        self,
        message: str,
        errors: list[str] = None,
        details: dict = None,
        error_code: str = "VALIDATION_ERROR",
    ):
        self.validation_errors = errors or []
        super().__init__(message, error_code=error_code, details=details)


class BalanceSheetError(ValidationError):
    """Raised when the balance sheet does not balance (A ≠ L + E)."""

    def __init__(self, delta: float, details: dict = None):
        self.delta = delta
        message = (
            f"Balance sheet imbalance: Assets - (Liabilities + Equity) = ${delta:,.2f}M. "
            f"This exceeds the $0.01M tolerance. Downstream computation is blocked."
        )
        super().__init__(message, details=details, error_code="BALANCE_SHEET_ERROR")


# ── Computation Errors ─────────────────────────────────────────────────────────


class ComputationError(FMVAError):
    """Raised for errors in the valuation computation pipeline."""

    def __init__(self, message: str, details: dict = None, error_code: str = "COMPUTATION_ERROR"):
        super().__init__(message, error_code=error_code, details=details)


class GordonGrowthError(ComputationError):
    """Raised when WACC ≤ Terminal Growth Rate (mathematically invalid)."""

    def __init__(self, wacc: float, tgr: float):
        message = (
            f"Gordon Growth Model invalid: WACC ({wacc:.2%}) must be strictly greater "
            f"than Terminal Growth Rate ({tgr:.2%})."
        )
        super().__init__(
            message,
            details={"wacc": wacc, "tgr": tgr},
            error_code="GORDON_GROWTH_ERROR",
        )


class WACCBoundsError(ComputationError):
    """Raised when WACC is outside valid bounds (5–25%)."""

    def __init__(self, wacc: float):
        message = f"WACC ({wacc:.2%}) is outside valid bounds (5%–25%)."
        super().__init__(message, details={"wacc": wacc}, error_code="WACC_BOUNDS_ERROR")


# ── Export Errors ──────────────────────────────────────────────────────────────


class ExportError(FMVAError):
    """Raised when export operations fail."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, error_code="EXPORT_ERROR", details=details)


# ── LLM Errors ─────────────────────────────────────────────────────────────────


class LLMError(FMVAError):
    """Raised when LLM loading or inference fails."""

    def __init__(self, message: str, details: dict = None, error_code: str = "LLM_ERROR"):
        super().__init__(message, error_code=error_code, details=details)


class HallucinationError(LLMError):
    """Raised when the LLM narrative contains numbers not in the model output."""

    def __init__(self, flagged_numbers: list[float], details: dict = None):
        self.flagged_numbers = flagged_numbers
        message = (
            f"Hallucination detected: {len(flagged_numbers)} number(s) in the narrative "
            f"do not match computed model outputs within ±5% tolerance."
        )
        super().__init__(message, details=details, error_code="HALLUCINATION_ERROR")
