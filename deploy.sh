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

# 4. Configuration des variables d'environnement
info "Vérification des variables d'environnement..."
if [ ! -f ".env" ]; then
    warn "Fichier .env non trouvé. Création depuis .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        error "⚠️  IMPORTANT: Modifiez le fichier .env avec vos valeurs de production!"
        exit 1
    else
        error "Fichier .env.example non trouvé!"
        exit 1
    fi
fi

# Mettre à jour ALLOWED_HOSTS si nécessaire
if grep -q "ALLOWED_HOSTS" .env; then
    if ! grep -q "dreamlabsadmin.strangernet.com" .env; then
        info "Mise à jour de ALLOWED_HOSTS avec le nouveau domaine..."
        sed -i 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=dreamlabsadmin.strangernet.com,localhost,127.0.0.1,216.218.216.165/' .env
        info "✅ ALLOWED_HOSTS mis à jour"
    fi
else
    # Ajouter ALLOWED_HOSTS s'il n'existe pas
    echo "ALLOWED_HOSTS=dreamlabsadmin.strangernet.com,localhost,127.0.0.1,216.218.216.165" >> .env
    info "✅ ALLOWED_HOSTS ajouté"
fi

# 5. Création du répertoire de logs (avant toute commande Django)
info "Création du répertoire de logs..."
mkdir -p logs
chmod 755 logs

# 6. Vérification et installation de PostgreSQL si nécessaire
info "Vérification de PostgreSQL..."

# Vérifier si PostgreSQL est installé
if ! command -v psql &> /dev/null; then
    warn "PostgreSQL n'est pas installé. Installation..."
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib libpq-dev
    info "✅ PostgreSQL installé"
fi

# Démarrer PostgreSQL (essayer différents noms de service)
PG_STARTED=false
for pg_service in postgresql postgresql@14-main postgresql@15-main postgresql@16-main; do
    if systemctl list-unit-files | grep -q "^${pg_service}"; then
        if ! systemctl is-active --quiet $pg_service 2>/dev/null; then
            warn "Démarrage de PostgreSQL ($pg_service)..."
            sudo systemctl start $pg_service 2>/dev/null && PG_STARTED=true
            sudo systemctl enable $pg_service 2>/dev/null
        else
            PG_STARTED=true
        fi
        break
    fi
done

# Si aucun service trouvé, essayer de démarrer postgresql directement
if [ "$PG_STARTED" = false ]; then
    warn "Tentative de démarrage de PostgreSQL..."
    sudo systemctl start postgresql 2>/dev/null && PG_STARTED=true || true
    sudo systemctl enable postgresql 2>/dev/null || true
fi

if [ "$PG_STARTED" = true ]; then
    sleep 3  # Attendre que PostgreSQL démarre
    info "✅ PostgreSQL est actif"
else
    warn "⚠️  Impossible de démarrer PostgreSQL automatiquement. Vérifiez manuellement."
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

# Vérifier si la base de données existe, sinon la créer
if [ -f ".env" ]; then
    DB_NAME=$(read_env_var "DB_NAME" "dreamslabs_db")
    DB_USER=$(read_env_var "DB_USER" "dreamslabs_user")
    DB_PASSWORD=$(read_env_var "DB_PASSWORD" "")
    
    # Vérifier si la base de données existe
    DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "0")
    
    if [ "$DB_EXISTS" != "1" ]; then
        warn "Base de données $DB_NAME n'existe pas. Création..."
        
        # Générer un mot de passe si nécessaire
        if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "your-secure-database-password-here" ]; then
            if command -v openssl &> /dev/null; then
                DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
            else
                DB_PASSWORD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 25 | head -n 1)
            fi
            sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
        fi
        
        # Créer l'utilisateur
        USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_user WHERE usename='$DB_USER'" 2>/dev/null || echo "0")
        if [ "$USER_EXISTS" != "1" ]; then
            sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null
        else
            sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null
        fi
        
        # Créer la base de données
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null
        
        # Configurer les privilèges
        sudo -u postgres psql -d $DB_NAME -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null
        sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null || true
        sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';" 2>/dev/null
        sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';" 2>/dev/null
        sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'America/Bogota';" 2>/dev/null
        
        info "✅ Base de données et utilisateur créés"
    fi
fi

# 7. Collecte des fichiers statiques
info "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --settings=dreamslabs_manager.settings_production

# 8. Création des migrations si nécessaire
info "Création des migrations..."
python manage.py makemigrations --settings=dreamslabs_manager.settings_production --noinput || true

# 9. Application des migrations
info "Application des migrations de base de données..."
python manage.py migrate --settings=dreamslabs_manager.settings_production

# 9.5. Initialisation des rôles (nécessaire avant de créer le superutilisateur)
info "Initialisation des rôles..."
python manage.py init_roles --settings=dreamslabs_manager.settings_production 2>/dev/null || true
info "✅ Rôles initialisés"

# 10. Création du superutilisateur admin/admin avec rôle GENERAL_MANAGER
info "Création du superutilisateur admin..."
DJANGO_SETTINGS_MODULE=dreamslabs_manager.settings_production python create_superuser.py || true
info "✅ Superutilisateur admin créé (username: admin, password: admin, rôle: GENERAL_MANAGER)"

# 11. Configuration du service Gunicorn (si nécessaire)
info "Configuration du service Gunicorn..."
if [ ! -f "/etc/systemd/system/${SERVICE_NAME}.service" ]; then
    if [ -f "deployment/gunicorn.service" ]; then
        warn "Service systemd non trouvé. Création..."
        sudo cp deployment/gunicorn.service /etc/systemd/system/${SERVICE_NAME}.service
        sudo systemctl daemon-reload
        sudo systemctl enable ${SERVICE_NAME}
        info "✅ Service systemd créé et activé"
    else
        warn "Fichier deployment/gunicorn.service non trouvé. Service non configuré."
    fi
fi

# 12. Installation et configuration de Nginx (si nécessaire)
info "Vérification de Nginx..."
if ! command -v nginx &> /dev/null; then
    warn "Nginx n'est pas installé. Installation..."
    sudo apt-get update
    sudo apt-get install -y nginx
    info "✅ Nginx installé"
fi

# Créer les répertoires s'ils n'existent pas
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

# Nettoyer les liens symboliques incorrects
info "Nettoyage des liens symboliques Nginx incorrects..."
sudo rm -f /etc/nginx/sites-enabled/sites-available 2>/dev/null || true
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

if [ ! -f "/etc/nginx/sites-available/${SERVICE_NAME}" ]; then
    if [ -f "deployment/nginx.conf" ]; then
        warn "Configuration Nginx non trouvée. Création..."
        sudo cp deployment/nginx.conf /etc/nginx/sites-available/${SERVICE_NAME}
        
        # Créer le lien symbolique correctement (vers le fichier, pas le répertoire)
        sudo rm -f /etc/nginx/sites-enabled/${SERVICE_NAME} 2>/dev/null || true
        sudo ln -sf /etc/nginx/sites-available/${SERVICE_NAME} /etc/nginx/sites-enabled/${SERVICE_NAME}
        
        # Démarrer Nginx s'il n'est pas actif
        if ! systemctl is-active --quiet nginx; then
            sudo systemctl start nginx
            sudo systemctl enable nginx
        fi
        
        # Test de la configuration
        if sudo nginx -t; then
            sudo systemctl reload nginx
            info "✅ Nginx configuré"
        else
            error "Erreur dans la configuration Nginx!"
            error "Exécutez: sudo ./deployment/fix_nginx_config.sh pour corriger"
        fi
    fi
else
    # Vérifier que le lien symbolique est correct
    if [ -L "/etc/nginx/sites-enabled/${SERVICE_NAME}" ]; then
        TARGET=$(readlink -f /etc/nginx/sites-enabled/${SERVICE_NAME} 2>/dev/null || echo "")
        if [ -d "$TARGET" ] || [ "$TARGET" != "/etc/nginx/sites-available/${SERVICE_NAME}" ]; then
            warn "Lien symbolique incorrect détecté. Correction..."
            sudo rm -f /etc/nginx/sites-enabled/${SERVICE_NAME}
            sudo ln -sf /etc/nginx/sites-available/${SERVICE_NAME} /etc/nginx/sites-enabled/${SERVICE_NAME}
        fi
    fi
fi

# 13. Redémarrage du service
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

# 14. Rechargement de Nginx
info "Rechargement de Nginx..."
sudo systemctl reload nginx 2>/dev/null || sudo systemctl restart nginx

info "✅ Déploiement terminé avec succès!"
info "🌐 L'application devrait être accessible sur http://dreamlabsadmin.strangernet.com"
