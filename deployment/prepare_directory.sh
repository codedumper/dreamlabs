#!/bin/bash

# Script à exécuter sur le serveur pour préparer le répertoire /var/www/dreamslabs_manager
# Usage: ./prepare_directory.sh
# Ce script doit être exécuté avec sudo ou par un utilisateur ayant les droits

set -e

PROJECT_DIR="/var/www/dreamslabs_manager"
TEMP_DIR="$HOME/dreamslabs_manager_temp"
USER="thestranger420"

echo "🔧 Préparation du répertoire de déploiement..."

# Vérifier si on a les droits sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Ce script doit être exécuté avec sudo"
    echo "Usage: sudo ./prepare_directory.sh"
    exit 1
fi

# Créer le répertoire
echo "Création du répertoire $PROJECT_DIR..."
mkdir -p $PROJECT_DIR
chown $USER:$USER $PROJECT_DIR
chmod 755 $PROJECT_DIR

# Si le répertoire temporaire existe, déplacer les fichiers
if [ -d "$TEMP_DIR" ]; then
    echo "Déplacement des fichiers depuis $TEMP_DIR..."
    if [ "$(ls -A $TEMP_DIR)" ]; then
        mv $TEMP_DIR/* $PROJECT_DIR/ 2>/dev/null || true
        mv $TEMP_DIR/.* $PROJECT_DIR/ 2>/dev/null || true
        rmdir $TEMP_DIR
        echo "✅ Fichiers déplacés vers $PROJECT_DIR"
    else
        rmdir $TEMP_DIR
    fi
fi

echo "✅ Répertoire $PROJECT_DIR prêt!"
echo ""
echo "Vous pouvez maintenant exécuter:"
echo "  cd $PROJECT_DIR"
echo "  chmod +x deployment/initial_setup.sh"
echo "  ./deployment/initial_setup.sh"
