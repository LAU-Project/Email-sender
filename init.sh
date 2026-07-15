#!/bin/bash

# ============================================================
#   SNAKE - Setup Script
#   LAU Project
# ============================================================

set -e

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

banner() {
    echo -e "${GREEN}"
    cat << "EOF"
EOF
    echo -e "${NC}${CYAN}${BOLD}LAU Project${NC}"
    echo -e "${CYAN}------------------------------------------------------------${NC}\n"
}

step() {
    echo -e "${YELLOW}➜ $1${NC}"
}

success() {
    echo -e "${GREEN}✔ $1${NC}\n"
}

error_exit() {
    echo -e "${RED}✘ $1${NC}"
    exit 1
}

banner

# --- Détection de l'OS ---
OS_TYPE="unknown"
case "$(uname -s)" in
    Linux*)     OS_TYPE="linux" ;;
    Darwin*)    OS_TYPE="macos" ;;
    CYGWIN*|MINGW*|MSYS*) OS_TYPE="windows" ;;
    *)          OS_TYPE="unknown" ;;
esac
step "Système détecté : ${OS_TYPE}"

# --- Détection de l'exécutable Python ---
if command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
elif command -v python &> /dev/null; then
    PYTHON_BIN="python"
else
    error_exit "Aucun interpréteur Python trouvé (python3/python)"
fi
success "Python détecté : $($PYTHON_BIN --version)"

step "Création de l'environnement virtuel..."
"$PYTHON_BIN" -m venv ./venv || error_exit "Échec de la création du venv"
success "Environnement virtuel prêt"

step "Activation de l'environnement virtuel..."
if [ "$OS_TYPE" = "windows" ]; then
    VENV_ACTIVATE="./venv/Scripts/activate"
else
    VENV_ACTIVATE="./venv/bin/activate"
fi

if [ ! -f "$VENV_ACTIVATE" ]; then
    error_exit "Script d'activation introuvable : $VENV_ACTIVATE"
fi

source "$VENV_ACTIVATE" || error_exit "Échec de l'activation du venv"
success "Environnement virtuel activé"

step "Installation des dépendances..."
"$PYTHON_BIN" -m pip install --upgrade pip > /dev/null
"$PYTHON_BIN" -m pip install -r requirements.txt || error_exit "Échec de l'installation des dépendances"
success "Dépendances installées"

step "Attribution des permissions à run.sh..."
if [ "$OS_TYPE" = "windows" ]; then
    echo -e "${YELLOW}⚠ chmod ignoré sous Windows (non applicable)${NC}\n"
else
    chmod 755 ./run.sh || error_exit "Échec du chmod sur run.sh"
    success "Permissions mises à jour"
fi

echo -e "${CYAN}------------------------------------------------------------${NC}"
echo -e "${GREEN}${BOLD}Setup terminé avec succès ! Prêt à lancer.${NC}"
echo -e "${CYAN}------------------------------------------------------------${NC}\n"