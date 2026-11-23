"""Formatação dos números que vão para o LaTeX (ais.cli.build_final_results): só apresentação."""
from ais.cli.build_final_results import pct, pt, thousands


def test_decimal_comma_and_rounding():
    assert pt(0.9461, 3) == "0,946"
    assert pt(1234.5, 0) in ("1234", "1235")  # arredondamento do Python; só apresentação
    assert pt(75.4, 1) == "75,4"


def test_thousands_uses_thin_space_latex():
    assert thousands(1026279) == "1\\,026\\,279"
    assert thousands(713) == "713"


def test_percent_is_scaled_and_latex_safe():
    assert pct(0.9461) == "94,6\\,\\%"
    assert pct(0.99999, 4) == "99,9990\\,\\%"
