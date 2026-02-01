"""Tests for the LLM connector signal parser."""

from app.services.ai.llm_connector import _parse_signals


class TestParseSignals:
    def test_parses_valid_json_array(self):
        raw = '''[
            {
                "signal_id": "SIG-001",
                "title": "High Canadian Home Bias",
                "description": "Your portfolio is 65% Canadian.",
                "severity": "warning",
                "category": "home_bias",
                "affected_holdings": ["XIC.TO", "BNS.TO"],
                "recommendation": "Consider adding international exposure."
            }
        ]'''
        signals = _parse_signals(raw)
        assert len(signals) == 1
        assert signals[0].signal_id == "SIG-001"
        assert signals[0].severity == "warning"

    def test_parses_markdown_wrapped_json(self):
        raw = '''```json
[
    {
        "signal_id": "SIG-001",
        "title": "Test",
        "description": "Test description",
        "severity": "info",
        "category": "concentration",
        "affected_holdings": [],
        "recommendation": "No action needed."
    }
]
```'''
        signals = _parse_signals(raw)
        assert len(signals) == 1

    def test_handles_empty_response(self):
        signals = _parse_signals("")
        assert signals == []

    def test_handles_garbage(self):
        signals = _parse_signals("This is not JSON at all")
        assert signals == []

    def test_parses_json_with_surrounding_text(self):
        raw = '''Here are the signals:
[
    {
        "signal_id": "SIG-001",
        "title": "Test Signal",
        "description": "A test.",
        "severity": "info",
        "category": "concentration",
        "affected_holdings": ["VGRO.TO"],
        "recommendation": "Review."
    }
]
That concludes the analysis.'''
        signals = _parse_signals(raw)
        assert len(signals) == 1

    def test_multiple_signals(self):
        raw = '''[
            {
                "signal_id": "SIG-001",
                "title": "Signal 1",
                "description": "First signal.",
                "severity": "warning",
                "category": "concentration",
                "affected_holdings": ["A"],
                "recommendation": "Fix A."
            },
            {
                "signal_id": "SIG-002",
                "title": "Signal 2",
                "description": "Second signal.",
                "severity": "critical",
                "category": "correlation",
                "affected_holdings": ["B", "C"],
                "recommendation": "Fix B and C."
            }
        ]'''
        signals = _parse_signals(raw)
        assert len(signals) == 2
        assert signals[1].severity == "critical"
