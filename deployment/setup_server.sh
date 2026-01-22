#!/bin/bash

# Script d'installation initiale du serveur
# À exécuter une seule fois sur la VPS pour configurer l'environnement
# Usage: ./setup_server.sh

set -e

echo "🔧 Configuration initiale du serveur pour Dreamslabs Manager..."

# Variables
PROJECT_DIR="/var/www/dreamslabs_manager"
PROJECT_NAME="dreamslabs_manager"
USER="thestranger420"
DB_NAME="dreamslabs_db"
DB_USER="dreamslabs_user"

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

# Vérifier que le script est exécuté en tant que root ou avec sudo
if [ "$EUID" -ne 0 ]; then 
    error "Ce script doit être exécuté avec sudo"
    exit 1
fi

# 1. Mise à jour du système
info "Mise à jour du système..."
apt-get update
apt-get upgrade -y

# 2. Installation des dépendances système
info "Installation des dépendances système..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    build-essential \
    libpq-dev \
    curl

# 3. Création de l'utilisateur et du répertoire du projet
info "Configuration de l'utilisateur et des répertoires..."
if ! id "$USER" &>/dev/null; then
    warn "L'utilisateur $USER n'existe pas. Création..."
    useradd -m -s /bin/bash $USER
fi

mkdir -p $PROJECT_DIR
chown $USER:$USER $PROJECT_DIR

# 4. Démarrage de PostgreSQL
info "Démarrage de PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql
info "✅ PostgreSQL démarré et activé"

# Note: La création de la base de données et de l'utilisateur sera faite par initial_setup.sh
# qui a accès au fichier .env avec le mot de passe correct
info "ℹ️  La base de données et l'utilisateur seront créés par initial_setup.sh"

# 5. Configuration de Nginx
info "Configuration de Nginx..."
if [ -f "$PROJECT_DIR/deployment/nginx.conf" ]; then
    cp $PROJECT_DIR/deployment/nginx.conf /etc/nginx/sites-available/$PROJECT_NAME
    ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
    
    # Supprimer la configuration par défaut si elle existe
    rm -f /etc/nginx/sites-enabled/default
    
    # Test de la configuration Nginx
    nginx -t
    
    # Redémarrage de Nginx
    systemctl restart nginx
    systemctl enable nginx
else
    warn "Fichier nginx.conf non trouvé. Configuration manuelle nécessaire."
fi

# 6. Configuration du service Gunicorn
info "Configuration du service Gunicorn..."
if [ -f "$PROJECT_DIR/deployment/gunicorn.service" ]; then
    cp $PROJECT_DIR/deployment/gunicorn.service /etc/systemd/system/$PROJECT_NAME.service
    systemctl daemon-reload
    systemctl enable $PROJECT_NAME
    warn "Le service sera démarré après le déploiement du code."
else
    warn "Fichier gunicorn.service non trouvé. Configuration manuelle nécessaire."
fi

# 7. Configuration du firewall (si UFW est installé)
if command -v ufw &> /dev/null; then
    info "Configuration du firewall..."
    ufw allow 'Nginx Full'
    ufw allow ssh
    ufw --force enable
fi

# 8. Création du répertoire de logs
info "Création du répertoire de logs..."
mkdir -p $PROJECT_DIR/logs
chown $USER:$USER $PROJECT_DIR/logs

info "✅ Configuration initiale terminée!"
info ""
warn "⚠️  PROCHAINES ÉTAPES:"
warn "1. Copiez votre code dans $PROJECT_DIR"
warn "2. Créez le fichier .env avec les bonnes valeurs"
warn "3. Exécutez ./deploy.sh pour déployer l'application"
