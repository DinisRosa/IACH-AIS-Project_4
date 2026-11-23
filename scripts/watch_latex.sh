#!/usr/bin/env bash
# Recompila latex/proposta_pt.tex sempre que o .tex ou o references.bib mudam.
# O PDF e os ficheiros auxiliares ficam em latex/build/ (ignorada pelo git).
# Uso (a partir da raiz do projeto): bash scripts/watch_latex.sh
# Parar com Ctrl+C. Abrir latex/build/proposta_pt.pdf num leitor que recarregue sozinho.

set -u
LATEX_DIR="$(cd "$(dirname "$0")/../latex" && pwd)"
BUILD_DIR="$LATEX_DIR/build"
MAIN="proposta_pt"
INTERVAL=2

mkdir -p "$BUILD_DIR"
cd "$LATEX_DIR" || exit 1

stamp() { cat "$LATEX_DIR/$MAIN.tex" "$LATEX_DIR/references.bib" | sha256sum | cut -d' ' -f1; }

build() {
    echo "[$(date +%H:%M:%S)] A compilar..."
    pdflatex -interaction=nonstopmode -output-directory="$BUILD_DIR" "$MAIN.tex" >/dev/null 2>&1
    (cd "$BUILD_DIR" && BIBINPUTS="$LATEX_DIR:" BSTINPUTS="$LATEX_DIR:" bibtex "$MAIN" >/dev/null 2>&1)
    pdflatex -interaction=nonstopmode -output-directory="$BUILD_DIR" "$MAIN.tex" >/dev/null 2>&1
    if pdflatex -interaction=nonstopmode -output-directory="$BUILD_DIR" "$MAIN.tex" 2>&1 | grep -q "^!"; then
        echo "[$(date +%H:%M:%S)] Erros de LaTeX. Ver $BUILD_DIR/$MAIN.log"
    else
        echo "[$(date +%H:%M:%S)] PDF atualizado: $BUILD_DIR/$MAIN.pdf"
    fi
}

last=""
while true; do
    current="$(stamp)"
    if [ "$current" != "$last" ]; then
        build
        last="$current"
    fi
    sleep "$INTERVAL"
done
