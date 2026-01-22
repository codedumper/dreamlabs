#!/bin/bash

# Script pour configurer Let's Encrypt avec la méthode HTTP-01 (automatique)
# Usage: ./setup_ssl_http01.sh

set -e

echo "🔒 Configuration de Let's Encrypt avec HTTP-01..."

# Variables
DOMAIN="dreamlabsadmin.strangernet.com"
EMAIL="admin@dreamslabs.com"  # Changez cette adresse email si nécessaire
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

# 1. Vérifier que Nginx est configuré et fonctionne
info "Vérification de Nginx..."
if ! systemctl is-active --quiet nginx; then
    error "Nginx n'est pas actif. Démarrez-le d'abord: sudo systemctl start nginx"
    exit 1
fi

# Vérifier que la configuration Nginx existe
if [ ! -f "/etc/nginx/sites-available/dreamslabs_manager" ]; then
    error "Configuration Nginx n'existe pas. Déployez d'abord l'application."
    exit 1
fi

# S'assurer que Nginx écoute sur le port 80
if ! grep -q "listen 80" /etc/nginx/sites-available/dreamslabs_manager; then
    warn "La configuration Nginx doit écouter sur le port 80 pour HTTP-01"
    warn "Mise à jour de la configuration..."
    
    # Créer une configuration temporaire pour HTTP-01
    cat > /etc/nginx/sites-available/dreamslabs_manager <<'TEMP_CONFIG'
upstream dreamslabs_manager {
    server unix:/var/www/dreamslabs_manager/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name dreamlabsadmin.strangernet.com;

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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
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
TEMP_CONFIG
    
    if nginx -t; then
        systemctl reload nginx
        info "✅ Configuration Nginx mise à jour"
    else
        error "Erreur dans la configuration Nginx!"
        exit 1
    fi
fi

# 2. Installation de certbot
info "Installation de certbot..."
if ! command -v certbot &> /dev/null; then
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
    info "✅ Certbot installé"
else
    info "✅ Certbot déjà installé"
fi

# 3. Vérifier que le domaine pointe vers ce serveur
info "Vérification DNS..."
DOMAIN_IP=$(dig +short "$DOMAIN" | tail -1)
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

if [ -z "$DOMAIN_IP" ]; then
    error "Le domaine $DOMAIN ne résout pas. Vérifiez votre DNS."
    exit 1
fi

warn "DNS résout vers: $DOMAIN_IP"
warn "IP du serveur: $SERVER_IP"
if [ "$DOMAIN_IP" != "$SERVER_IP" ] && [ "$DOMAIN_IP" != "216.218.216.165" ]; then
    warn "⚠️  Le DNS ne semble pas pointer vers ce serveur"
    warn "⚠️  La validation HTTP-01 échouera si le DNS n'est pas correct"
    read -p "Continuer quand même? (o/N): " continue_choice
    if [[ ! "$continue_choice" =~ ^([oO][uU][iI]|[oO])$ ]]; then
        exit 1
    fi
fi

# 4. Nettoyer les anciennes autorisations en échec
info "Nettoyage des anciennes autorisations en échec..."
# Supprimer les certificats/renouvellements existants pour ce domaine si nécessaire
certbot delete --cert-name "$DOMAIN" --non-interactive 2>/dev/null || true

# 5. Nettoyer les anciennes autorisations en échec
info "Nettoyage des anciennes autorisations en échec..."
# Supprimer les certificats/renouvellements existants pour ce domaine si nécessaire
certbot delete --cert-name "$DOMAIN" --non-interactive 2>/dev/null || true

# Attendre un peu pour que Let's Encrypt nettoie les anciennes autorisations
sleep 5

# 6. Obtenir le certificat avec HTTP-01 (automatique)
info "Obtention du certificat avec HTTP-01..."
info "Certbot va automatiquement configurer Nginx pour la validation..."

# Utiliser --preferred-challenges http pour forcer HTTP-01
# Utiliser --force-renewal si un certificat existe déjà
certbot --nginx \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --no-eff-email \
    --preferred-challenges http \
    -d "$DOMAIN" \
    --redirect \
    --force-renewal 2>/dev/null || \
certbot --nginx \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --no-eff-email \
    --preferred-challenges http \
    -d "$DOMAIN" \
    --redirect

if [ $? -eq 0 ]; then
    info "✅ Certificat obtenu avec succès!"
    
    # 7. Vérifier la configuration Nginx mise à jour
    info "Vérification de la configuration Nginx..."
    if nginx -t; then
        systemctl reload nginx
        info "✅ Nginx rechargé avec la configuration HTTPS"
    else
        error "Erreur dans la configuration Nginx après certbot!"
        exit 1
    fi
    
    # 8. Configurer le renouvellement automatique
    info "Configuration du renouvellement automatique..."
    
    # Créer un hook de renouvellement
    mkdir -p /etc/letsencrypt/renewal-hooks/deploy
    cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh <<'RENEWAL_SCRIPT'
#!/bin/bash
systemctl reload nginx
RENEWAL_SCRIPT
    
    chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
    
    # Tester le renouvellement
    certbot renew --dry-run
    
    if [ $? -eq 0 ]; then
        info "✅ Renouvellement automatique configuré et testé"
    else
        warn "⚠️  Le test de renouvellement a échoué. Vérifiez la configuration."
    fi
    
    # 9. Mettre à jour le fichier .env pour activer les paramètres de sécurité
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
    info "✅ Configuration SSL terminée!"
    info "🌐 L'application est maintenant accessible sur https://$DOMAIN"
    info "🔄 La redirection HTTP → HTTPS est automatiquement configurée"
    info ""
    warn "⚠️  N'oubliez pas de redémarrer le service Django pour appliquer les nouveaux paramètres:"
    warn "   sudo systemctl restart dreamslabs_manager"
    
else
    error "❌ Échec de l'obtention du certificat"
    error "Vérifiez que:"
    error "  1. Le domaine pointe vers ce serveur (DNS)"
    error "  2. Le port 80 est accessible depuis Internet"
    error "  3. Nginx est correctement configuré"
    exit 1
fi
