"""Tests for the data normalizer service."""

from app.services.aggregator.normalizer import normalize_ticker


class TestNormalizeTicker:
    def test_tsx_exchange(self):
        assert normalize_ticker("VGRO", "TSX") == "VGRO.TO"
        assert normalize_ticker("XIC", "TSE") == "XIC.TO"

    def test_us_exchange_no_suffix(self):
        assert normalize_ticker("AAPL", "NASDAQ") == "AAPL"
        assert normalize_ticker("JPM", "NYSE") == "JPM"

    def test_known_tsx_without_exchange(self):
        assert normalize_ticker("VGRO", None) == "VGRO.TO"
        assert normalize_ticker("VEQT", None) == "VEQT.TO"
        assert normalize_ticker("XGRO", None) == "XGRO.TO"

    def test_already_has_suffix(self):
        assert normalize_ticker("VGRO.TO", "TSX") == "VGRO.TO"
        assert normalize_ticker("BNS.TO", None) == "BNS.TO"

    def test_unknown_ticker_no_suffix(self):
        assert normalize_ticker("UNKNOWN", None) == "UNKNOWN"

    def test_empty_symbol(self):
        assert normalize_ticker("", None) == ""

    def test_neo_exchange(self):
        assert normalize_ticker("BTCC", "NEO") == "BTCC.TO"
