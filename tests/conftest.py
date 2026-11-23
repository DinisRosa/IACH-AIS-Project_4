"""Torna o pacote src/phase1 importável nos testes (sem instalar o pacote)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
