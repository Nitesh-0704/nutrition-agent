#!/usr/bin/env bash
# =============================================================================
# import-all.sh — Import the Nutrition Agent into watsonx Orchestrate
# =============================================================================
# Usage:
#   chmod +x import-all.sh
#   ./import-all.sh
# =============================================================================

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "============================================="
echo "  Nutrition Agent — watsonx Orchestrate Import"
echo "============================================="

# --- 1. Import Python tools -------------------------------------------------
echo ""
echo "[1/2] Importing Python tools..."
for tool in nutrition_tools.py; do
  echo "  → Importing: tools/${tool}"
  orchestrate tools import -k python -f "${SCRIPT_DIR}/tools/${tool}"
done
echo "  ✓ Tools imported successfully."

# --- 2. Import Agent ---------------------------------------------------------
echo ""
echo "[2/2] Importing Agent..."
for agent in nutrition_agent.yaml; do
  echo "  → Importing: agents/${agent}"
  orchestrate agents import -f "${SCRIPT_DIR}/agents/${agent}"
done
echo "  ✓ Agent imported successfully."

echo ""
echo "============================================="
echo "  Import complete!"
echo "  Run: orchestrate chat start"
echo "  Then select: nutrition_agent"
echo "============================================="
