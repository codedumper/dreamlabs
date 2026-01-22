#!/bin/bash

# Script pour nettoyer les autorisations Let's Encrypt en échec
# Usage: sudo ./cleanup_certbot.sh

set -e

DOMAIN="dreamlabsadmin.strangernet.com"

echo "🧹 Nettoyage des autorisations Let's Encrypt en échec..."

# Supprimer les certificats existants pour ce domaine
echo "Suppression des certificats existants..."
certbot delete --cert-name "$DOMAIN" --non-interactive 2>/dev/null || true

# Supprimer les comptes/répertoires de renouvellement problématiques
echo "Nettoyage du répertoire Let's Encrypt..."
if [ -d "/etc/letsencrypt/renewal" ]; then
    rm -f /etc/letsencrypt/renewal/${DOMAIN}.conf 2>/dev/null || true
fi

# Attendre que Let's Encrypt nettoie côté serveur
echo "Attente de 10 secondes pour que Let's Encrypt nettoie les autorisations..."
sleep 10

echo "✅ Nettoyage terminé"
echo ""
echo "Vous pouvez maintenant réessayer:"
echo "  sudo ./deployment/setup_ssl_http01.sh"
