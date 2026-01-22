#!/bin/bash

# Script d'initialisation complète - À exécuter sur le serveur après avoir copié le code
# Usage: ./initial_setup.sh

set -e

echo "🔧 Configuration initiale complète de Dreamslabs Manager..."

# Variables
PROJECT_DIR="/var/www/dreamslabs_manager"
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

cd $PROJECT_DIR

# 0. Vérifier que Git est configuré (si le code vient de Git)
if [ -d ".git" ]; then
    info "Dépôt Git détecté"
    
    # Vérifier que Git est installé
    if ! command -v git &> /dev/null; then
        warn "Git n'est pas installé. Installation..."
        sudo apt-get update
        sudo apt-get install -y git
    fi
    
    # S'assurer que le remote est configuré
    if ! git remote get-url origin &>/dev/null; then
        warn "Remote Git non configuré. Configuration..."
        git remote add origin https://github.com/codedumper/dreamlabs.git 2>/dev/null || \
        git remote set-url origin https://github.com/codedumper/dreamlabs.git
    fi
    
    # S'assurer qu'on est sur la bonne branche
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
    if [ -z "$CURRENT_BRANCH" ]; then
        git checkout -b main 2>/dev/null || git checkout main 2>/dev/null || true
    fi
fi

# Fonction pour lire une variable depuis .env de manière sécurisée
read_env_var() {
    local var_name=$1
    local default_value=$2
    if [ -f ".env" ]; then
        grep "^${var_name}=" .env 2>/dev/null | cut -d '=' -f2- | sed "s/^['\"]//; s/['\"]$//" || echo "$default_value"
    else
        echo "$default_value"
    fi
}

# 1. Création de l'environnement virtuel
info "Création de l'environnement virtuel..."
if [ -d "venv" ]; then
    warn "Suppression de l'environnement virtuel existant..."
    rm -rf venv
fi
python3 -m venv venv
info "✅ Environnement virtuel créé"

source venv/bin/activate

# 2. Création du répertoire de logs (avant toute commande Django)
info "Création du répertoire de logs..."
mkdir -p logs
chmod 755 logs
info "✅ Répertoire de logs créé"

# 3. Installation des dépendances
info "Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt
info "✅ Dépendances installées"

# 4. Configuration du fichier .env
info "Configuration du fichier .env..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        info "✅ Fichier .env créé depuis .env.example"
        
        # Générer une SECRET_KEY
        SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        info "✅ SECRET_KEY générée automatiquement"
        
        # Le mot de passe PostgreSQL sera généré automatiquement plus tard
        info "✅ Le mot de passe PostgreSQL sera généré automatiquement"
    else
        error "Fichier .env.example non trouvé!"
        exit 1
    fi
else
    warn "Fichier .env déjà présent"
fi

# 5. Installation et configuration de PostgreSQL
info "Vérification de PostgreSQL..."

# Vérifier si PostgreSQL est installé
if ! command -v psql &> /dev/null; then
    warn "PostgreSQL n'est pas installé. Installation..."
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib libpq-dev
    info "✅ PostgreSQL installé"
fi

# Démarrer et activer PostgreSQL
if ! systemctl is-active --quiet postgresql; then
    info "Démarrage de PostgreSQL..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    info "✅ PostgreSQL démarré"
else
    info "✅ PostgreSQL est actif"
fi

# 6. Création de la base de données et de l'utilisateur
info "Configuration de la base de données..."

# Lire le mot de passe depuis .env (ou générer un mot de passe sécurisé)
if [ -f ".env" ]; then
    DB_PASSWORD=$(read_env_var "DB_PASSWORD" "")
else
    DB_PASSWORD=""
fi

# Si pas de mot de passe dans .env, en générer un
if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "your-secure-database-password-here" ]; then
    warn "Génération d'un mot de passe sécurisé pour PostgreSQL..."
    # Essayer openssl, sinon utiliser /dev/urandom
    if command -v openssl &> /dev/null; then
        DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    else
        DB_PASSWORD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 25 | head -n 1)
    fi
    if [ -f ".env" ]; then
        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
        info "✅ Mot de passe sauvegardé dans .env"
    fi
fi

# Vérifier si la base de données existe
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "0")

# Vérifier si l'utilisateur existe
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_user WHERE usename='$DB_USER'" 2>/dev/null || echo "0")

if [ "$DB_EXISTS" != "1" ] || [ "$USER_EXISTS" != "1" ]; then
    info "Création de l'utilisateur et de la base de données..."
    
    # Créer l'utilisateur s'il n'existe pas
    if [ "$USER_EXISTS" != "1" ]; then
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || \
        sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        info "✅ Utilisateur $DB_USER créé/mis à jour"
    fi
    
    # Créer la base de données si elle n'existe pas
    if [ "$DB_EXISTS" != "1" ]; then
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null
        info "✅ Base de données $DB_NAME créée"
    fi
    
    # Configurer les privilèges et paramètres
    sudo -u postgres psql -d $DB_NAME <<EOF
-- Attribution des privilèges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'America/Bogota';
\q
EOF
    
    # Donner les privilèges sur le schéma public
    sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null || true
    
    info "✅ Configuration de la base de données terminée"
else
    warn "Base de données et utilisateur existent déjà"
    # Mettre à jour le mot de passe quand même
    sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
    info "✅ Mot de passe mis à jour"
fi

# 7. Création des migrations
info "Création des migrations..."
python manage.py makemigrations --settings=dreamslabs_manager.settings_production --noinput || true

# 8. Application des migrations
info "Application des migrations..."
python manage.py migrate --settings=dreamslabs_manager.settings_production
info "✅ Migrations appliquées"

# 8.5. Initialisation des rôles (nécessaire avant de créer le superutilisateur)
info "Initialisation des rôles..."
python manage.py init_roles --settings=dreamslabs_manager.settings_production 2>/dev/null || true
info "✅ Rôles initialisés"

# 8.6. Création du superutilisateur admin/admin avec rôle GENERAL_MANAGER
info "Création du superutilisateur admin..."
DJANGO_SETTINGS_MODULE=dreamslabs_manager.settings_production python create_superuser.py || true
info "✅ Superutilisateur admin créé (username: admin, password: admin, rôle: GENERAL_MANAGER)"

# 9. Collecte des fichiers statiques
info "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --settings=dreamslabs_manager.settings_production
info "✅ Fichiers statiques collectés"

# 10. Initialisation des données de base
info "Initialisation des données de base..."
if python manage.py init_roles --settings=dreamslabs_manager.settings_production 2>/dev/null; then
    info "✅ Rôles initialisés"
else
    warn "Commande init_roles non disponible ou déjà exécutée"
fi

if python manage.py init_financial_data --settings=dreamslabs_manager.settings_production 2>/dev/null; then
    info "✅ Données financières initialisées"
else
    warn "Commande init_financial_data non disponible ou déjà exécutée"
fi

# 11. Configuration de Nginx
info "Configuration de Nginx..."
if [ -f "deployment/nginx.conf" ]; then
    sudo cp deployment/nginx.conf /etc/nginx/sites-available/$PROJECT_NAME
    sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test de la configuration
    if sudo nginx -t; then
        sudo systemctl restart nginx
        sudo systemctl enable nginx
        info "✅ Nginx configuré et démarré"
    else
        error "Erreur dans la configuration Nginx!"
        exit 1
    fi
else
    warn "Fichier nginx.conf non trouvé"
fi

# 12. Configuration du service Gunicorn
info "Configuration du service Gunicorn..."
if [ -f "deployment/gunicorn.service" ]; then
    sudo cp deployment/gunicorn.service /etc/systemd/system/$PROJECT_NAME.service
    sudo systemctl daemon-reload
    sudo systemctl enable $PROJECT_NAME
    sudo systemctl start $PROJECT_NAME
    
    sleep 2
    if sudo systemctl is-active --quiet $PROJECT_NAME; then
        info "✅ Service Gunicorn démarré"
    else
        error "Le service Gunicorn n'a pas démarré. Vérifiez les logs:"
        sudo systemctl status $PROJECT_NAME
        exit 1
    fi
else
    warn "Fichier gunicorn.service non trouvé"
fi

# Note: Le superutilisateur admin/admin a déjà été créé automatiquement à l'étape 8.5

echo ""
info "✅ Configuration initiale terminée!"
info ""
info "🌐 L'application devrait être accessible sur http://dreamlabsadmin.strangernet.com"
info ""
info "Commandes utiles:"
info "  - Voir les logs: sudo journalctl -u $PROJECT_NAME -f"
info "  - Redémarrer: sudo systemctl restart $PROJECT_NAME"
info "  - Statut: sudo systemctl status $PROJECT_NAME"
