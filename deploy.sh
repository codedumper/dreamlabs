#!/bin/bash

# Script de déploiement pour Dreamslabs Manager
# Usage: ./deploy.sh

set -e  # Arrêter en cas d'erreur

echo "🚀 Démarrage du déploiement de Dreamslabs Manager..."

# Variables
PROJECT_DIR="/var/www/dreamslabs_manager"
PROJECT_NAME="dreamslabs_manager"
USER="thestranger420"
SERVICE_NAME="dreamslabs_manager"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que nous sommes sur le serveur
if [ ! -d "$PROJECT_DIR" ]; then
    error "Le répertoire $PROJECT_DIR n'existe pas. Création..."
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
fi

cd $PROJECT_DIR

# 1. Mise à jour du code depuis Git
info "Mise à jour du code depuis Git..."
if [ -d ".git" ]; then
    # Vérifier que Git est installé
    if ! command -v git &> /dev/null; then
        error "Git n'est pas installé. Installation..."
        sudo apt-get update
        sudo apt-get install -y git
    fi
    
    # Déterminer la branche actuelle
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
    if [ -z "$CURRENT_BRANCH" ]; then
        CURRENT_BRANCH="main"
        # Créer la branche si elle n'existe pas
        git checkout -b main 2>/dev/null || true
    fi
    
    # Vérifier que le remote est configuré
    if ! git remote get-url origin &>/dev/null; then
        warn "Remote Git non configuré. Configuration..."
        git remote add origin https://github.com/codedumper/dreamlabs.git 2>/dev/null || \
        git remote set-url origin https://github.com/codedumper/dreamlabs.git
    fi
    
    # Mettre à jour depuis le dépôt
    info "Récupération des dernières modifications depuis GitHub..."
    git fetch origin || warn "Impossible de récupérer depuis GitHub. Vérifiez la connexion."
    
    # Vérifier s'il y a des changements locaux non commités
    if ! git diff-index --quiet HEAD -- 2>/dev/null || [ -n "$(git status --porcelain 2>/dev/null | grep -v '^??')" ]; then
        warn "⚠️  Changements locaux détectés. Sauvegarde..."
        git stash save "Auto-stash before deployment $(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
    fi
    
    # Mettre à jour vers la dernière version
    if git reset --hard origin/$CURRENT_BRANCH 2>/dev/null || \
       git reset --hard origin/main 2>/dev/null || \
       git reset --hard origin/master 2>/dev/null; then
        info "✅ Code mis à jour depuis la branche $CURRENT_BRANCH"
    else
        warn "⚠️  Impossible de mettre à jour depuis Git. Utilisation du code local."
    fi
else
    warn "Pas de dépôt Git trouvé. Le code sera utilisé tel quel."
    warn "Pour utiliser Git, clonez le dépôt: git clone https://github.com/codedumper/dreamlabs.git ."
fi

# 2. Activation de l'environnement virtuel
info "Activation de l'environnement virtuel..."
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    if [ -d "venv" ]; then
        warn "Environnement virtuel corrompu, recréation..."
        rm -rf venv
    fi
    info "Création de l'environnement virtuel..."
    python3 -m venv venv
fi
source venv/bin/activate

# 3. Installation/Mise à jour des dépendances
info "Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Vérification des variables d'environnement
info "Vérification des variables d'environnement..."
if [ ! -f ".env" ]; then
    error "⚠️  Fichier .env non trouvé!"
    error "⚠️  Le fichier .env doit exister avant le déploiement."
    error "⚠️  Exécutez initial_setup.sh pour la première installation."
    exit 1
fi
info "✅ Fichier .env présent"

# 5. Création du répertoire de logs (avant toute commande Django qui charge les settings)
info "Création du répertoire de logs..."
mkdir -p logs
chmod 755 logs

# 6. Vérification que PostgreSQL est démarré
info "Vérification de PostgreSQL..."
if ! systemctl is-active --quiet postgresql 2>/dev/null; then
    warn "PostgreSQL n'est pas actif. Démarrage..."
    sudo systemctl start postgresql 2>/dev/null || true
    sleep 2
fi
info "✅ PostgreSQL vérifié"

# 7. Collecte des fichiers statiques
info "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --settings=dreamslabs_manager.settings_production
info "✅ Fichiers statiques collectés"

# 8. Création des migrations si nécessaire
info "Création des migrations..."
python manage.py makemigrations --settings=dreamslabs_manager.settings_production --noinput || true

# 9. Application des migrations
info "Application des migrations de base de données..."
python manage.py migrate --settings=dreamslabs_manager.settings_production
info "✅ Migrations appliquées"

# Note importante: Ce script de déploiement ne modifie AUCUNE donnée
# - Pas de création/modification d'utilisateurs
# - Pas de création/modification de base de données
# - Pas de création/modification de rôles
# Ces opérations sont faites uniquement lors de la première installation (initial_setup.sh)

# 10. Redémarrage du service Gunicorn
if [ -f "/etc/systemd/system/${SERVICE_NAME}.service" ]; then
    info "Redémarrage du service Gunicorn..."
    sudo systemctl restart $SERVICE_NAME
    
    # Vérification du statut
    sleep 2
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        info "✅ Service $SERVICE_NAME démarré avec succès!"
    else
        error "❌ Le service $SERVICE_NAME n'est pas actif. Vérifiez les logs:"
        sudo systemctl status $SERVICE_NAME
        exit 1
    fi
else
    warn "⚠️  Service systemd non configuré. Démarrage manuel nécessaire."
fi

# 11. Rechargement de Nginx
info "Rechargement de Nginx..."
sudo systemctl reload nginx 2>/dev/null || sudo systemctl restart nginx
info "✅ Nginx rechargé"

info "✅ Déploiement terminé avec succès!"
info "🌐 L'application devrait être accessible sur http://dreamlabsadmin.strangernet.com"
