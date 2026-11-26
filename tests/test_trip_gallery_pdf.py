"""Conversão da página da galeria para LaTeX (ais.cli.build_trip_gallery_pdf), só com dados sintéticos."""
import pytest

from ais.cli.build_trip_gallery import BASE, PP, SETS, markdown
from ais.cli.build_trip_gallery_pdf import to_latex


def _page() -> str:
    data = {}
    for split, trips in (("test", ("111-1", "222-2")), ("validation", ("333-3",))):
        values = {row: {t: {"accuracy": 0.5 + n / 10, "n_pred": 7, "n_ref": 2} for n, t in enumerate(trips)}
                  for row in SETS[split]["rows"]}
        data[split] = {"values": values, "points": {t: 1234 for t in trips}}
    return markdown(data)


def test_every_trip_image_and_value_reaches_the_latex():
    tex = to_latex(_page())
    for path in ("teste/111-1.png", "teste/222-2.png", "validacao/333-3.png"):
        assert rf"\includegraphics[width=0.9\linewidth]{{{path}}}" in tex
    assert tex.count(r"\begin{minipage}") == tex.count(r"\end{minipage}") == 3
    assert r"J0 & 60,0\,\% & 7 \\" in tex and f"{BASE} & 50,0\\,\\% & 7" in tex and PP in tex
    assert r"\hyperlink{222-2}{222-2}" in tex and r"\hypertarget{validacao}{}" in tex
    assert "](" not in tex and "**" not in tex and "Voltar ao topo" not in tex


def test_unknown_construction_is_refused():
    with pytest.raises(ValueError, match="não prevista"):
        to_latex("# T\n\n> uma citação\n")
