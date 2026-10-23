#!/usr/bin/env bash
# End-to-end reproducible pipeline for C9orf72-Nature2Agent.
#
#   ./run.sh setup      create the venv and install pinned dependencies
#   ./run.sh fetch      download + checksum the Zenodo ICS data and PMC supplementary
#   ./run.sh datasets   build the machine-readable datasets
#   ./run.sh analyses   reproduce claims + exploratory analyses
#   ./run.sh figures    regenerate the major + discovery figures
#   ./run.sh discovery  run the agentic discovery loop (24 Q, >=5 observations)
#   ./run.sh evaluate   run the scientific + AI evaluation framework
#   ./run.sh test       run the test suite
#   ./run.sh all        everything above, in order (default)
#   ./run.sh mcp        start the MCP server (Paper2Agent)
set -euo pipefail
cd "$(dirname "$0")"
PY=".venv/bin/python"
STAGE="${1:-all}"

setup()    { python3 -m venv .venv && $PY -m pip install -q --upgrade pip && $PY -m pip install -q -r requirements.txt && $PY -m pip install -q -e .; }
fetch()    { $PY scripts/fetch_data.py --records ics --pmc; }
datasets() { $PY scripts/build_datasets.py; }
analyses() { $PY scripts/run_analyses.py; }
figures()  { $PY scripts/reproduce_figures.py; }
discovery(){ $PY scripts/run_discovery.py; }
evaluate() { $PY scripts/run_evaluation.py; }
test_()    { $PY -m pytest -q; }
report()   { $PY scripts/make_report_assets.py && cd reports && \
             pdflatex -interaction=nonstopmode main.tex >/dev/null && bibtex main >/dev/null && \
             pdflatex -interaction=nonstopmode main.tex >/dev/null && pdflatex -interaction=nonstopmode main.tex >/dev/null && \
             cd .. && echo "reports/main.pdf built"; }
mcp()      { $PY model/mcp_server.py; }

case "$STAGE" in
  setup) setup ;;
  fetch) fetch ;;
  datasets) datasets ;;
  analyses) analyses ;;
  figures) figures ;;
  discovery) discovery ;;
  evaluate) evaluate ;;
  test) test_ ;;
  report) report ;;
  mcp) mcp ;;
  all)
    [ -d .venv ] || setup
    [ -f data/raw/supplementary/41586_2025_9588_MOESM3_ESM.xlsx ] || fetch
    datasets; analyses; figures; discovery; evaluate; test_
    echo "Pipeline complete. See results/ , evaluation/ and reports/." ;;
  *) echo "unknown stage: $STAGE"; grep '^#   ' "$0"; exit 1 ;;
esac
