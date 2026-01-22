#!/bin/bash

# Script pour corriger la configuration Nginx
# Usage: sudo ./fix_nginx_config.sh

set -e

echo "🔧 Correction de la configuration Nginx..."

# Variables
PROJECT_NAME="dreamslabs_manager"
SITES_AVAILABLE="/etc/nginx/sites-available"
SITES_ENABLED="/etc/nginx/sites-enabled"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Vérifier que le script est exécuté avec sudo
if [ "$EUID" -ne 0 ]; then 
    error "Ce script doit être exécuté avec sudo"
    exit 1
fi

# 1. Nettoyer les liens symboliques incorrects dans sites-enabled
info "Nettoyage des liens symboliques incorrects..."
cd "$SITES_ENABLED"

# Supprimer tous les liens symboliques qui pointent vers des répertoires ou sont invalides
for link in *; do
    if [ -L "$link" ]; then
        TARGET=$(readlink -f "$link" 2>/dev/null || echo "")
        if [ -d "$TARGET" ] || [ -z "$TARGET" ] || [ "$link" = "sites-available" ]; then
            warn "Suppression du lien symbolique incorrect: $link"
            rm -f "$link"
        fi
    fi
done

# Supprimer spécifiquement le lien problématique
rm -f "$SITES_ENABLED/sites-available" 2>/dev/null || true
rm -f "$SITES_ENABLED/default" 2>/dev/null || true

info "✅ Liens symboliques nettoyés"

# 2. Vérifier que le fichier de configuration existe
if [ ! -f "$SITES_AVAILABLE/$PROJECT_NAME" ]; then
    error "Le fichier de configuration $SITES_AVAILABLE/$PROJECT_NAME n'existe pas!"
    error "Exécutez d'abord le script de configuration approprié."
    exit 1
fi

# 3. Créer le bon lien symbolique
info "Création du lien symbolique correct..."
ln -sf "$SITES_AVAILABLE/$PROJECT_NAME" "$SITES_ENABLED/$PROJECT_NAME"
info "✅ Lien symbolique créé: $SITES_ENABLED/$PROJECT_NAME -> $SITES_AVAILABLE/$PROJECT_NAME"

# 4. Vérifier la configuration
info "Vérification de la configuration Nginx..."
if nginx -t; then
    info "✅ Configuration Nginx valide"
    
    # 5. Recharger Nginx
    info "Rechargement de Nginx..."
    systemctl reload nginx
    info "✅ Nginx rechargé"
    
    echo ""
    info "✅ Configuration Nginx corrigée avec succès!"
else
    error "❌ Erreur dans la configuration Nginx!"
    nginx -t
    exit 1
fi
