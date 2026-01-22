#!/bin/bash

# Script de diagnostic pour vérifier l'état du déploiement
# Usage: ./check_status.sh

echo "🔍 Diagnostic du déploiement Dreamslabs Manager..."
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() {
    echo -e "${GREEN}[OK]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Vérifier les services
echo "1. Vérification des services..."
if systemctl is-active --quiet dreamslabs_manager; then
    info "Service dreamslabs_manager est actif"
else
    error "Service dreamslabs_manager n'est PAS actif"
    echo "   → sudo systemctl status dreamslabs_manager"
fi

if systemctl is-active --quiet nginx; then
    info "Service nginx est actif"
else
    error "Service nginx n'est PAS actif"
    echo "   → sudo systemctl status nginx"
fi

if systemctl is-active --quiet postgresql; then
    info "Service postgresql est actif"
else
    error "Service postgresql n'est PAS actif"
    echo "   → sudo systemctl status postgresql"
fi

echo ""

# 2. Vérifier les ports
echo "2. Vérification des ports..."
if netstat -tuln | grep -q ":80 "; then
    info "Port 80 est ouvert"
else
    warn "Port 80 n'est pas ouvert"
fi

if netstat -tuln | grep -q ":443 "; then
    info "Port 443 est ouvert"
else
    warn "Port 443 n'est pas ouvert"
fi

echo ""

# 3. Vérifier le socket Gunicorn
echo "3. Vérification du socket Gunicorn..."
if [ -S "/var/www/dreamslabs_manager/gunicorn.sock" ]; then
    info "Socket Gunicorn existe"
    ls -la /var/www/dreamslabs_manager/gunicorn.sock
else
    error "Socket Gunicorn n'existe pas"
fi

echo ""

# 4. Vérifier la configuration Nginx
echo "4. Vérification de la configuration Nginx..."
if [ -f "/etc/nginx/sites-available/dreamslabs_manager" ]; then
    info "Configuration Nginx existe"
    if nginx -t 2>&1 | grep -q "successful"; then
        info "Configuration Nginx est valide"
    else
        error "Configuration Nginx a des erreurs:"
        nginx -t
    fi
else
    error "Configuration Nginx n'existe pas"
fi

echo ""

# 5. Vérifier le certificat SSL
echo "5. Vérification du certificat SSL..."
if [ -f "/etc/letsencrypt/live/dreamlabsadmin.strangernet.com/fullchain.pem" ]; then
    info "Certificat SSL existe"
    certbot certificates 2>/dev/null | grep -A 5 "dreamlabsadmin.strangernet.com" || true
else
    warn "Certificat SSL n'existe pas"
    echo "   → Exécutez: sudo ./deployment/setup_ssl_dns01.sh"
fi

echo ""

# 6. Vérifier le DNS
echo "6. Vérification DNS..."
DOMAIN_IP=$(dig +short dreamlabsadmin.strangernet.com | tail -1)
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

if [ -n "$DOMAIN_IP" ]; then
    info "DNS résout vers: $DOMAIN_IP"
    if [ "$DOMAIN_IP" = "$SERVER_IP" ] || [ "$DOMAIN_IP" = "216.218.216.165" ]; then
        info "DNS pointe vers le bon serveur"
    else
        warn "DNS ne pointe peut-être pas vers ce serveur (IP serveur: $SERVER_IP)"
    fi
else
    error "DNS ne résout pas le domaine"
fi

echo ""

# 7. Vérifier les logs récents
echo "7. Dernières erreurs dans les logs..."
echo "--- Logs Gunicorn (dernières 5 lignes) ---"
journalctl -u dreamslabs_manager -n 5 --no-pager 2>/dev/null || echo "Aucun log"
echo ""
echo "--- Logs Nginx (dernières 5 lignes) ---"
tail -5 /var/log/nginx/dreamslabs_manager_error.log 2>/dev/null || echo "Aucun log"
echo ""

# 8. Test de connexion locale
echo "8. Test de connexion locale..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost/accounts/dashboard/ | grep -q "200\|301\|302"; then
    info "Application répond localement"
else
    error "Application ne répond pas localement"
    echo "   Code HTTP: $(curl -s -o /dev/null -w "%{http_code}" http://localhost/accounts/dashboard/)"
fi

echo ""
echo "✅ Diagnostic terminé"
