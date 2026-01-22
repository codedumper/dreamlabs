#!/bin/bash

# Script pour initialiser Git dans le projet
# Usage: ./init_git.sh

set -e

echo "🔧 Initialisation de Git pour Dreamslabs Manager..."

# Variables
GIT_REPO="https://github.com/codedumper/dreamlabs.git"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Vérifier que Git est installé
if ! command -v git &> /dev/null; then
    error "Git n'est pas installé. Installez-le d'abord."
    exit 1
fi

# Initialiser Git si nécessaire
if [ ! -d ".git" ]; then
    info "Initialisation de Git..."
    git init
    info "✅ Git initialisé"
else
    info "✅ Git déjà initialisé"
fi

# Configurer le remote
if ! git remote get-url origin &>/dev/null; then
    info "Ajout du remote GitHub..."
    git remote add origin "$GIT_REPO"
    info "✅ Remote ajouté"
else
    CURRENT_REMOTE=$(git remote get-url origin)
    if [ "$CURRENT_REMOTE" != "$GIT_REPO" ]; then
        warn "Le remote actuel est: $CURRENT_REMOTE"
        read -p "Voulez-vous le remplacer par $GIT_REPO? (o/N): " replace_choice
        if [[ "$replace_choice" =~ ^([oO][uU][iI]|[oO])$ ]]; then
            git remote set-url origin "$GIT_REPO"
            info "✅ Remote mis à jour"
        fi
    else
        info "✅ Remote déjà configuré correctement"
    fi
fi

# Vérifier la branche
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ -z "$CURRENT_BRANCH" ]; then
    info "Création de la branche main..."
    git checkout -b main
    CURRENT_BRANCH="main"
else
    info "Branche actuelle: $CURRENT_BRANCH"
fi

# Ajouter tous les fichiers
info "Ajout des fichiers au dépôt..."
git add .

# Vérifier s'il y a des changements à committer
if [ -n "$(git status --porcelain)" ]; then
    warn "Il y a des fichiers non suivis ou modifiés."
    read -p "Voulez-vous faire un commit initial? (o/N): " commit_choice
    if [[ "$commit_choice" =~ ^([oO][uU][iI]|[oO])$ ]]; then
        read -p "Message de commit [Initial commit]: " commit_msg
        commit_msg=${commit_msg:-"Initial commit"}
        git commit -m "$commit_msg"
        info "✅ Commit créé"
        
        read -p "Voulez-vous pousser vers GitHub maintenant? (o/N): " push_choice
        if [[ "$push_choice" =~ ^([oO][uU][iI]|[oO])$ ]]; then
            git push -u origin "$CURRENT_BRANCH"
            info "✅ Code poussé vers GitHub"
        fi
    fi
else
    info "✅ Tous les fichiers sont déjà suivis"
fi

echo ""
info "✅ Initialisation Git terminée!"
info ""
info "Commandes utiles:"
info "  - Voir le statut: git status"
info "  - Ajouter des fichiers: git add ."
info "  - Committer: git commit -m 'message'"
info "  - Pousser: git push origin $CURRENT_BRANCH"
info "  - Déployer: ./deploy_to_server.sh"
