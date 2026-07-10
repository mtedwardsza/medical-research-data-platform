"""
tests/test_etl.py
=================
Unit tests for the ETL cleaning pipeline (process_data.py).

WHAT IS A UNIT TEST?
    A unit test verifies that one small, isolated function works correctly.
    It calls the function with a known input and asserts the output matches
    what we expect. If the function ever breaks (e.g. someone changes the
    logic), the test catches it immediately.

WHY THESE FUNCTIONS?
    parse_date, parse_bool, parse_currency and normalise_gender are the
    core transformation functions that clean the raw data. If any of them
    have a bug, thousands of records get corrupted silently. Tests prevent that.

HOW TO RUN:
    pip install pytest --break-system-packages
    pytest tests/test_etl.py -v

COVERAGE:
    - parse_date        : 6 test cases (3 valid formats + null + empty + invalid)
    - parse_bool        : 9 test cases (all True/False variants + null + invalid)
    - parse_currency    : 5 test cases (normal + comma + null + empty + invalid)
    - normalise_gender  : 8 test cases (all variants + null + invalid)
    - Total             : 28 unit tests
"""

import sys
import os
import pytest

# ── Add project root to path so we can import process_data ───────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from process_data import parse_date, parse_bool, parse_currency, normalise_gender


# ═══════════════════════════════════════════════════════════════════════════════
# parse_date
# ═══════════════════════════════════════════════════════════════════════════════

class TestParseDate:
    """Tests for parse_date() — handles 3 input date formats."""

    def test_iso_format(self):
        """Standard ISO date (YYYY-MM-DD) should be returned as-is."""
        assert parse_date("2023-05-20") == "2023-05-20"

    def test_australian_format(self):
        """Australian date format (DD/MM/YYYY) should be converted to ISO."""
        assert parse_date("20/05/2023") == "2023-05-20"

    def test_us_abbreviated_format(self):
        """US abbreviated format (Mon-DD-YYYY) should be converted to ISO."""
        assert parse_date("May-20-2023") == "2023-05-20"

    def test_null_value_returns_none(self):
        """A null/NaN value should return None (not raise an exception)."""
        import pandas as pd
        assert parse_date(pd.NaT) is None
        assert parse_date(None) is None

    def test_empty_string_returns_none(self):
        """An empty string should return None."""
        assert parse_date("") is None
        assert parse_date("   ") is None

    def test_invalid_date_returns_none(self):
        """An unrecognised date format should return None, not crash."""
        assert parse_date("32-13-2023") is None
        assert parse_date("not-a-date") is None


# ═══════════════════════════════════════════════════════════════════════════════
# parse_bool
# ═══════════════════════════════════════════════════════════════════════════════

class TestParseBool:
    """Tests for parse_bool() — normalises all boolean-like representations."""

    # ── True variants ─────────────────────────────────────────────────────────
    def test_yes_returns_true(self):
        assert parse_bool("Yes") is True

    def test_y_returns_true(self):
        assert parse_bool("Y") is True

    def test_string_1_returns_true(self):
        assert parse_bool("1") is True

    def test_string_true_uppercase_returns_true(self):
        assert parse_bool("TRUE") is True

    def test_python_true_returns_true(self):
        assert parse_bool(True) is True

    # ── False variants ────────────────────────────────────────────────────────
    def test_no_returns_false(self):
        assert parse_bool("No") is False

    def test_string_0_returns_false(self):
        assert parse_bool("0") is False

    def test_python_false_returns_false(self):
        assert parse_bool(False) is False

    # ── Edge cases ────────────────────────────────────────────────────────────
    def test_null_returns_none(self):
        import pandas as pd
        assert parse_bool(pd.NA) is None
        assert parse_bool(None) is None

    def test_invalid_value_returns_none(self):
        """An unrecognised value should return None, not raise an exception."""
        assert parse_bool("maybe") is None
        assert parse_bool("unknown") is None


# ═══════════════════════════════════════════════════════════════════════════════
# parse_currency
# ═══════════════════════════════════════════════════════════════════════════════

class TestParseCurrency:
    """Tests for parse_currency() — strips $ and commas, returns float."""

    def test_simple_currency_string(self):
        """$793.00 should become 793.0"""
        assert parse_currency("$793.00") == 793.0

    def test_currency_with_thousands_comma(self):
        """$1,234.56 should become 1234.56"""
        assert parse_currency("$1,234.56") == 1234.56

    def test_large_amount(self):
        """$2,500,000.00 should become 2500000.0"""
        assert parse_currency("$2,500,000.00") == 2500000.0

    def test_null_returns_none(self):
        import pandas as pd
        assert parse_currency(pd.NA) is None
        assert parse_currency(None) is None

    def test_empty_string_returns_none(self):
        assert parse_currency("") is None

    def test_invalid_returns_none(self):
        """Non-numeric strings should return None, not raise an exception."""
        assert parse_currency("N/A") is None
        assert parse_currency("unknown") is None


# ═══════════════════════════════════════════════════════════════════════════════
# normalise_gender
# ═══════════════════════════════════════════════════════════════════════════════

class TestNormaliseGender:
    """Tests for normalise_gender() — standardises to Male / Female / Non-binary."""

    # ── Male variants ─────────────────────────────────────────────────────────
    def test_male_lowercase(self):
        assert normalise_gender("male") == "Male"

    def test_male_uppercase(self):
        assert normalise_gender("MALE") == "Male"

    def test_male_initial(self):
        assert normalise_gender("M") == "Male"

    # ── Female variants ───────────────────────────────────────────────────────
    def test_female_mixed_case(self):
        assert normalise_gender("Female") == "Female"

    def test_female_initial(self):
        assert normalise_gender("F") == "Female"

    # ── Non-binary variants ───────────────────────────────────────────────────
    def test_nonbinary_hyphenated(self):
        assert normalise_gender("Non-binary") == "Non-binary"

    def test_nonbinary_abbreviation(self):
        assert normalise_gender("NB") == "Non-binary"

    def test_other_maps_to_nonbinary(self):
        assert normalise_gender("Other") == "Non-binary"

    # ── Edge cases ────────────────────────────────────────────────────────────
    def test_null_returns_none(self):
        import pandas as pd
        assert normalise_gender(pd.NA) is None
        assert normalise_gender(None) is None

    def test_unrecognised_returns_none(self):
        """An unrecognised value should return None, not raise."""
        assert normalise_gender("alien") is None
        assert normalise_gender("X") is None
