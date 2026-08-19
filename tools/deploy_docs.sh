#!/usr/bin/env bash
# deploy_docs.sh — Publiceert een gedocumenteerde versie via mike
#
# Gebruik: ./tools/deploy_docs.sh <versie> [<alias>]
#
# Voorbeelden:
#   ./tools/deploy_docs.sh v0.1 latest
#   ./tools/deploy_docs.sh v0.2
#
# Dit script publiceert de documentatie naar de gh-pages branch via mike.
# Zorg dat je write-toegang hebt tot het repository en dat de remote
# 'origin' correct geconfigureerd is.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Controleer argumenten
if [ $# -lt 1 ]; then
    echo "Gebruik: $0 <versie> [<alias>]"
    echo "Voorbeeld: $0 v0.1 latest"
    exit 1
fi

VERSION="${1}"
ALIAS="${2:-}"

echo "==> GBO-Semantiek: documentatie publiceren"
echo "    Versie:     ${VERSION}"
echo "    Alias:      ${ALIAS:-<geen>}"
echo "    Repository: ${REPO_ROOT}"
echo ""

cd "${REPO_ROOT}"

# Controleer of mike beschikbaar is
if ! command -v mike &>/dev/null; then
    echo "FOUT: mike is niet geïnstalleerd."
    echo "Installeer met: pip install mike"
    exit 1
fi

echo "==> mike versie: $(mike --version)"
echo ""

# Bouw en publiceer via mike
if [ -n "${ALIAS}" ]; then
    echo "==> Publiceren versie '${VERSION}' met alias '${ALIAS}'..."
    mike deploy --push --update-aliases "${VERSION}" "${ALIAS}"
else
    echo "==> Publiceren versie '${VERSION}'..."
    mike deploy --push "${VERSION}"
fi

echo ""
echo "==> Publicatie geslaagd."
echo "    URL: https://ictu.github.io/GBO-Semantiek/${VERSION}/"
