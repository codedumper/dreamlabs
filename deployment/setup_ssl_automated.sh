#!/bin/bash

# Script automatisé pour Let's Encrypt avec DNS-01 (nécessite un plugin DNS)
# Ce script utilise certbot avec un plugin DNS (ex: Cloudflare, Route53, etc.)
# Usage: ./setup_ssl_automated.sh

set -e

echo "🔒 Configuration automatisée de Let's Encrypt avec DNS-01..."

# Variables
DOMAIN="dreamlabsadmin.strangernet.com"
EMAIL="admin@dreamslabs.com"  # Changez cette adresse email
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

# 1. Installation de certbot et plugins DNS
info "Installation de certbot et plugins DNS..."
apt-get update

# Installer certbot de base
apt-get install -y certbot python3-pip

# Installer les plugins DNS courants
pip3 install certbot-dns-cloudflare certbot-dns-route53 certbot-dns-google || true

info "✅ Certbot et plugins installés"

# 2. Demander le type de DNS provider
echo ""
warn "Quel est votre fournisseur DNS?"
echo "1) Cloudflare"
echo "2) Route53 (AWS)"
echo "3) Google Cloud DNS"
echo "4) Autre (validation manuelle)"
read -p "Choix [1-4]: " dns_choice

case $dns_choice in
    1)
        DNS_PLUGIN="dns-cloudflare"
        warn "⚠️  Vous devrez créer un fichier /etc/letsencrypt/cloudflare.ini avec:"
        warn "   dns_cloudflare_api_token = VOTRE_TOKEN_API"
        read -p "Appuyez sur Entrée quand le fichier est créé..."
        ;;
    2)
        DNS_PLUGIN="dns-route53"
        warn "⚠️  Assurez-vous que les credentials AWS sont configurés"
        ;;
    3)
        DNS_PLUGIN="dns-google"
        warn "⚠️  Vous devrez configurer les credentials Google Cloud"
        ;;
    4)
        warn "Utilisation de la méthode manuelle..."
        exec "$(dirname "$0")/setup_ssl_dns01.sh"
        exit 0
        ;;
    *)
        error "Choix invalide"
        exit 1
        ;;
esac

# 3. Obtenir le certificat
info "Obtention du certificat avec DNS-01..."
if [ "$DNS_PLUGIN" = "dns-cloudflare" ]; then
    certbot certonly \
        --dns-cloudflare \
        --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN"
elif [ "$DNS_PLUGIN" = "dns-route53" ]; then
    certbot certonly \
        --dns-route53 \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN"
elif [ "$DNS_PLUGIN" = "dns-google" ]; then
    certbot certonly \
        --dns-google \
        --dns-google-credentials /etc/letsencrypt/google-credentials.json \
        --dns-google-propagation-seconds 60 \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN"
fi

if [ $? -eq 0 ]; then
    info "✅ Certificat obtenu avec succès!"
    
    # 4. Mettre à jour Nginx (même code que dans setup_ssl_dns01.sh)
    info "Mise à jour de la configuration Nginx..."
    
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
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

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

    error_page 500 502 503 504 /500.html;
    location = /500.html {
        root /var/www/dreamslabs_manager/templates;
    }
}
EOF

    if nginx -t; then
        systemctl reload nginx
        info "✅ Nginx configuré pour HTTPS"
    else
        error "Erreur dans la configuration Nginx!"
        exit 1
    fi
    
    # 5. Configurer le renouvellement
    info "Configuration du renouvellement automatique..."
    certbot renew --dry-run
    
    # 6. Mettre à jour .env
    if [ -f "$PROJECT_DIR/.env" ]; then
        sed -i 's/SECURE_SSL_REDIRECT=.*/SECURE_SSL_REDIRECT=True/' "$PROJECT_DIR/.env"
        sed -i 's/SESSION_COOKIE_SECURE=.*/SESSION_COOKIE_SECURE=True/' "$PROJECT_DIR/.env"
        sed -i 's/CSRF_COOKIE_SECURE=.*/CSRF_COOKIE_SECURE=True/' "$PROJECT_DIR/.env"
    fi
    
    info "✅ Configuration SSL terminée!"
    info "🌐 L'application est maintenant accessible sur https://$DOMAIN"
    
else
    error "❌ Échec de l'obtention du certificat"
    exit 1
fi
