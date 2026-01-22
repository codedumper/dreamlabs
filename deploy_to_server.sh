#!/bin/bash

# Script pour déployer le code sur la VPS via Git
# Usage: ./deploy_to_server.sh

set -e

echo "🚀 Déploiement de Dreamslabs Manager sur la VPS via Git..."

# Variables
SERVER="thestranger420@216.218.216.165"
PROJECT_DIR="/var/www/dreamslabs_manager"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_USER="thestranger420"
GIT_REPO="https://github.com/codedumper/dreamlabs.git"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Vérifier que Git est initialisé localement
info "Vérification de Git local..."
if [ ! -d ".git" ]; then
    warn "Git n'est pas initialisé. Initialisation..."
    git init
    git remote add origin "$GIT_REPO" 2>/dev/null || git remote set-url origin "$GIT_REPO"
    info "✅ Git initialisé"
else
    # Vérifier que le remote est configuré
    if ! git remote get-url origin &>/dev/null; then
        git remote add origin "$GIT_REPO"
    else
        git remote set-url origin "$GIT_REPO"
    fi
    info "✅ Git configuré"
fi

# 2. Vérifier s'il y a des changements non commités
if ! git diff-index --quiet HEAD -- 2>/dev/null || [ -n "$(git status --porcelain)" ]; then
    warn "⚠️  Il y a des changements non commités"
    read -p "Voulez-vous les committer maintenant? (o/N): " commit_choice
    if [[ "$commit_choice" =~ ^([oO][uU][iI]|[oO])$ ]]; then
        git add .
        read -p "Message de commit: " commit_msg
        commit_msg=${commit_msg:-"Deployment update"}
        git commit -m "$commit_msg"
        info "✅ Changements commités"
    fi
fi

# 3. Pousser vers GitHub
info "Poussage vers GitHub..."
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
if [ -z "$CURRENT_BRANCH" ]; then
    git checkout -b main
    CURRENT_BRANCH="main"
fi

# Créer la branche si elle n'existe pas sur le remote
git push -u origin "$CURRENT_BRANCH" 2>&1 | grep -v "Everything up-to-date" || true
info "✅ Code poussé vers GitHub"

# 4. Vérifier la connexion SSH
info "Vérification de la connexion SSH..."
if ! ssh -o ConnectTimeout=5 $SERVER "echo 'Connexion OK'" > /dev/null 2>&1; then
    error "⚠️  Impossible de se connecter au serveur. Vérifiez votre connexion SSH."
    exit 1
fi

# 5. Vérifier si c'est la première installation
info "Vérification si c'est la première installation..."
FIRST_INSTALL=$(ssh $SERVER "[ ! -d '$PROJECT_DIR/.git' ] && echo 'yes' || echo 'no'")

if [ "$FIRST_INSTALL" = "yes" ]; then
    warn "⚠️  Première installation détectée"
    info "Clonage du dépôt sur le serveur..."
    ssh $SERVER "sudo -n mkdir -p $PROJECT_DIR && sudo -n chown $SERVER_USER:$SERVER_USER $PROJECT_DIR"
    ssh $SERVER "cd $PROJECT_DIR && git clone $GIT_REPO . || (rm -rf * .[^.]* 2>/dev/null; git clone $GIT_REPO .)"
    warn "Exécution du script d'initialisation..."
    ssh -t $SERVER "cd $PROJECT_DIR && chmod +x deployment/initial_setup.sh && ./deployment/initial_setup.sh"
else
    # Mise à jour via Git
    info "Mise à jour du code sur le serveur via Git..."
    ssh $SERVER "cd $PROJECT_DIR && git fetch origin && git reset --hard origin/$CURRENT_BRANCH"
    
    # Exécuter le script de déploiement sur le serveur
    info "Exécution du script de déploiement sur le serveur..."
    ssh -t $SERVER "cd $PROJECT_DIR && chmod +x deploy.sh && ./deploy.sh"
fi

info "✅ Déploiement terminé!"
info "🌐 L'application devrait être accessible sur https://dreamlabsadmin.strangernet.com"
