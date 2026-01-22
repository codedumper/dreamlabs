#!/bin/bash

# Script pour configurer Nginx avec un certificat SSL existant
# Usage: sudo ./configure_nginx_ssl.sh

set -e

DOMAIN="dreamlabsadmin.strangernet.com"
PROJECT_DIR="/var/www/dreamslabs_manager"

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

# 1. Vérifier que le certificat existe
info "Vérification du certificat SSL..."
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    error "Certificat SSL non trouvé dans /etc/letsencrypt/live/$DOMAIN/"
    error "Exécutez d'abord: sudo ./deployment/setup_ssl_http01.sh"
    exit 1
fi

info "✅ Certificat SSL trouvé"

# 2. Créer la configuration Nginx avec HTTPS
info "Configuration de Nginx pour HTTPS..."

cat > /etc/nginx/sites-available/dreamslabs_manager <<EOF
# Redirection HTTP vers HTTPS
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# Configuration HTTPS
upstream dreamslabs_manager {
    server unix:/var/www/dreamslabs_manager/gunicorn.sock fail_timeout=0;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Configuration SSL recommandée
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    client_max_body_size 4G;

    access_log /var/log/nginx/dreamslabs_manager_access.log;
    error_log /var/log/nginx/dreamslabs_manager_error.log;

    location /static/ {
        alias /var/www/dreamslabs_manager/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/dreamslabs_manager/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$http_host;
        proxy_redirect off;
        proxy_pass http://dreamslabs_manager;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Gestion des erreurs
    error_page 500 502 503 504 /500.html;
    location = /500.html {
        root /var/www/dreamslabs_manager/templates;
    }
}
EOF

# 3. Nettoyer les liens symboliques incorrects et créer le bon
info "Nettoyage des liens symboliques Nginx incorrects..."
rm -f /etc/nginx/sites-enabled/sites-available 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/dreamslabs_manager 2>/dev/null || true

# Créer le lien symbolique correct (vers le fichier, pas le répertoire)
ln -sf /etc/nginx/sites-available/dreamslabs_manager /etc/nginx/sites-enabled/dreamslabs_manager
info "✅ Lien symbolique créé"

# 4. Vérifier la configuration
info "Vérification de la configuration Nginx..."
if nginx -t; then
    info "✅ Configuration Nginx valide"
else
    error "❌ Erreur dans la configuration Nginx!"
    nginx -t
    exit 1
fi

# 5. Recharger Nginx
info "Rechargement de Nginx..."
systemctl reload nginx
info "✅ Nginx rechargé"

# 6. Mettre à jour le fichier .env pour activer les paramètres de sécurité
if [ -f "$PROJECT_DIR/.env" ]; then
    info "Mise à jour du fichier .env pour activer HTTPS..."
    sed -i 's/SECURE_SSL_REDIRECT=.*/SECURE_SSL_REDIRECT=True/' "$PROJECT_DIR/.env" || \
    echo "SECURE_SSL_REDIRECT=True" >> "$PROJECT_DIR/.env"
    
    sed -i 's/SESSION_COOKIE_SECURE=.*/SESSION_COOKIE_SECURE=True/' "$PROJECT_DIR/.env" || \
    echo "SESSION_COOKIE_SECURE=True" >> "$PROJECT_DIR/.env"
    
    sed -i 's/CSRF_COOKIE_SECURE=.*/CSRF_COOKIE_SECURE=True/' "$PROJECT_DIR/.env" || \
    echo "CSRF_COOKIE_SECURE=True" >> "$PROJECT_DIR/.env"
    
    info "✅ Paramètres de sécurité HTTPS activés dans .env"
fi

echo ""
info "✅ Configuration terminée!"
info "🌐 L'application est maintenant accessible sur https://$DOMAIN"
info "🔄 La redirection HTTP → HTTPS est configurée"
info ""
warn "⚠️  N'oubliez pas de redémarrer le service Django pour appliquer les nouveaux paramètres:"
warn "   sudo systemctl restart dreamslabs_manager"
