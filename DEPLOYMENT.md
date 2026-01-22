# 🚀 Guide de Déploiement Rapide

Guide rapide pour déployer Dreamslabs Manager sur la VPS.

## Prérequis

1. **Initialiser Git dans le projet** (une seule fois):
```bash
./init_git.sh
```

Ce script va:
- Initialiser Git si nécessaire
- Configurer le remote GitHub (https://github.com/codedumper/dreamlabs.git)
- Créer un commit initial si nécessaire
- Optionnellement pousser vers GitHub

## Option 1: Déploiement Automatique via Git (Recommandé)

### Depuis votre machine locale:

```bash
# 1. S'assurer que vos changements sont commités et poussés
git add .
git commit -m "Votre message"
git push origin main

# 2. Déployer sur le serveur
./deploy_to_server.sh
```

Ce script va:
- Pousser vos changements vers GitHub
- Cloner ou mettre à jour le code sur le serveur via Git
- Exécuter le script de déploiement sur le serveur
- Redémarrer les services

## Option 2: Déploiement Manuel

### Étape 1: Première Installation (une seule fois)

Connectez-vous au serveur:
```bash
ssh thestranger420@216.218.216.165
```

Sur le serveur, clonez le dépôt Git dans `/var/www/dreamslabs_manager` puis exécutez:

```bash
# Cloner le dépôt
sudo mkdir -p /var/www/dreamslabs_manager
sudo chown thestranger420:thestranger420 /var/www/dreamslabs_manager
cd /var/www
git clone https://github.com/codedumper/dreamlabs.git dreamslabs_manager
cd dreamslabs_manager

# Exécuter l'installation
chmod +x deployment/initial_setup.sh
./deployment/initial_setup.sh
```

Ce script va:
- Installer toutes les dépendances système (PostgreSQL, Nginx, etc.)
- Créer l'environnement virtuel Python
- Configurer la base de données PostgreSQL
- Configurer Nginx et Gunicorn
- Initialiser l'application

### Étape 2: Déploiements Ultérieurs

À chaque fois que vous voulez mettre à jour le code:

**Depuis votre machine locale (recommandé):**
```bash
# 1. Committer et pousser vos changements
git add .
git commit -m "Description des changements"
git push origin main

# 2. Déployer
./deploy_to_server.sh
```

**Ou manuellement sur le serveur:**
```bash
cd /var/www/dreamslabs_manager
git pull origin main
./deploy.sh
```

## Vérification

Après le déploiement, vérifiez que tout fonctionne:

```bash
# Sur le serveur
sudo systemctl status dreamslabs_manager
sudo systemctl status nginx

# Ouvrez dans votre navigateur
http://216.218.216.165
```

## Commandes Utiles

### Voir les logs
```bash
# Logs de l'application
sudo journalctl -u dreamslabs_manager -f

# Logs Nginx
sudo tail -f /var/log/nginx/dreamslabs_manager_error.log

# Logs Django
tail -f /var/www/dreamslabs_manager/logs/django.log
```

### Redémarrer les services
```bash
sudo systemctl restart dreamslabs_manager
sudo systemctl restart nginx
```

### Créer un superutilisateur
```bash
cd /var/www/dreamslabs_manager
source venv/bin/activate
python manage.py createsuperuser --settings=dreamslabs_manager.settings_production
```

## Structure des Fichiers de Déploiement

```
.
├── deploy.sh                    # Script de déploiement (sur le serveur)
├── deploy_to_server.sh          # Script pour déployer depuis local
├── .env.example                 # Template des variables d'environnement
├── deployment/
│   ├── nginx.conf              # Configuration Nginx
│   ├── gunicorn.service        # Service systemd
│   ├── setup_server.sh         # Installation initiale (root)
│   ├── initial_setup.sh        # Configuration complète (user)
│   └── README.md               # Documentation détaillée
└── dreamslabs_manager/
    └── settings_production.py  # Settings Django pour production
```

## Dépannage

### Le service ne démarre pas
```bash
sudo journalctl -u dreamslabs_manager -n 50
```

### Erreur 502 Bad Gateway
- Vérifiez que Gunicorn est actif: `sudo systemctl status dreamslabs_manager`
- Vérifiez les logs Nginx: `sudo tail -f /var/log/nginx/dreamslabs_manager_error.log`

### Erreur de base de données
- Vérifiez que PostgreSQL est actif: `sudo systemctl status postgresql`
- Vérifiez le fichier `.env` dans `/var/www/dreamslabs_manager`

## Configuration SSL/HTTPS avec Let's Encrypt

### Méthode HTTP-01 (Recommandée - Automatique)

La méthode HTTP-01 est la plus simple et entièrement automatisée :

```bash
ssh thestranger420@216.218.216.165
cd /var/www/dreamslabs_manager
sudo chmod +x deployment/setup_ssl_http01.sh
sudo ./deployment/setup_ssl_http01.sh
```

Le script va automatiquement :
1. Installer certbot
2. Obtenir le certificat via HTTP-01 (sans intervention manuelle)
3. Configurer Nginx pour HTTPS avec redirection HTTP → HTTPS
4. Configurer le renouvellement automatique
5. Mettre à jour le fichier `.env` pour activer les paramètres de sécurité Django

**Prérequis :**
- Le domaine `dreamlabsadmin.strangernet.com` doit pointer vers `216.218.216.165`
- Le port 80 doit être accessible depuis Internet
- Nginx doit être configuré et fonctionnel

### Méthode DNS-01 (Alternative - Manuelle)

Si HTTP-01 ne fonctionne pas (par exemple si le port 80 n'est pas accessible), utilisez DNS-01 :

```bash
sudo chmod +x deployment/setup_ssl_dns01.sh
sudo ./deployment/setup_ssl_dns01.sh
```

**Important :** La méthode DNS-01 nécessite d'ajouter manuellement un enregistrement TXT dans votre DNS pour `_acme-challenge.dreamlabsadmin.strangernet.com`.

## Support

Pour plus de détails, consultez `deployment/README.md`.
