"""
Shared test fixtures for the FMVA test suite.
"""

import json
import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent.parent / "data" / "fixtures"


@pytest.fixture
def techcorp_path():
    return str(FIXTURES_DIR / "techcorp.json")


@pytest.fixture
def manufactureco_path():
    return str(FIXTURES_DIR / "manufactureco.json")


@pytest.fixture
def retailchain_path():
    return str(FIXTURES_DIR / "retailchain.json")


@pytest.fixture
def imbalanced_bs_path():
    return str(FIXTURES_DIR / "imbalanced_bs.json")


@pytest.fixture
def techcorp_raw(techcorp_path):
    with open(techcorp_path, "r") as f:
        return json.load(f)


@pytest.fixture
def base_assumptions():
    from fmva.engines.assumptions import get_preset
    return get_preset("base")


@pytest.fixture
def techcorp_normalized(techcorp_raw):
    from fmva.core.normalization import normalize
    return normalize(techcorp_raw)
