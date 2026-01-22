#!/bin/bash

# Script pour configurer Let's Encrypt avec la méthode DNS-01
# Usage: ./setup_ssl_dns01.sh

set -e

echo "🔒 Configuration de Let's Encrypt avec DNS-01..."

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

# 1. Installation de certbot
info "Installation de certbot..."
if ! command -v certbot &> /dev/null; then
    apt-get update
    apt-get install -y certbot python3-certbot-nginx python3-certbot-dns-cloudflare || \
    apt-get install -y certbot python3-certbot-nginx
    info "✅ Certbot installé"
else
    info "✅ Certbot déjà installé"
fi

# 2. Obtenir le certificat avec DNS-01 (méthode manuelle)
info "Obtention du certificat avec DNS-01..."
warn "⚠️  La méthode DNS-01 nécessite une validation manuelle via DNS"
warn "⚠️  Certbot va vous demander d'ajouter un enregistrement TXT dans votre DNS"

# Utiliser certbot avec le plugin manual et DNS-01
certbot certonly \
    --manual \
    --preferred-challenges dns \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    --manual-public-ip-logging-ok

if [ $? -eq 0 ]; then
    info "✅ Certificat obtenu avec succès!"
    
    # 3. Mettre à jour la configuration Nginx pour HTTPS
    info "Mise à jour de la configuration Nginx..."
    
    # Créer la configuration HTTPS
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

    # Test de la configuration
    if nginx -t; then
        systemctl reload nginx
        info "✅ Nginx configuré pour HTTPS"
    else
        error "Erreur dans la configuration Nginx!"
        exit 1
    fi
    
    # 4. Configurer le renouvellement automatique
    info "Configuration du renouvellement automatique..."
    
    # Créer un script de renouvellement
    cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh <<'RENEWAL_SCRIPT'
#!/bin/bash
systemctl reload nginx
RENEWAL_SCRIPT
    
    chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
    
    # Tester le renouvellement
    certbot renew --dry-run
    
    if [ $? -eq 0 ]; then
        info "✅ Renouvellement automatique configuré"
    else
        warn "⚠️  Le test de renouvellement a échoué. Vérifiez la configuration."
    fi
    
    # 5. Mettre à jour le fichier .env pour activer les paramètres de sécurité
    if [ -f "$PROJECT_DIR/.env" ]; then
        info "Mise à jour du fichier .env pour activer HTTPS..."
        sed -i 's/SECURE_SSL_REDIRECT=.*/SECURE_SSL_REDIRECT=True/' "$PROJECT_DIR/.env"
        sed -i 's/SESSION_COOKIE_SECURE=.*/SESSION_COOKIE_SECURE=True/' "$PROJECT_DIR/.env"
        sed -i 's/CSRF_COOKIE_SECURE=.*/CSRF_COOKIE_SECURE=True/' "$PROJECT_DIR/.env"
        info "✅ Paramètres de sécurité HTTPS activés dans .env"
    fi
    
    echo ""
    info "✅ Configuration SSL terminée!"
    info "🌐 L'application est maintenant accessible sur https://$DOMAIN"
    info ""
    warn "⚠️  N'oubliez pas de redémarrer le service Django pour appliquer les nouveaux paramètres:"
    warn "   sudo systemctl restart dreamslabs_manager"
    
else
    error "❌ Échec de l'obtention du certificat"
    exit 1
fi
