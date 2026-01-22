# Guide de Déploiement - Dreamslabs Manager

Ce guide vous explique comment déployer Dreamslabs Manager sur une VPS Ubuntu/Debian.

## Prérequis

- Accès SSH à la VPS (216.218.216.165)
- Utilisateur: thestranger420
- Python 3.8+
- PostgreSQL
- Nginx

## Étapes de Déploiement

### 1. Connexion au serveur

```bash
ssh thestranger420@216.218.216.165
```

### 2. Installation initiale (une seule fois)

Sur le serveur, exécutez le script d'installation:

```bash
# Téléchargez ou copiez le code sur le serveur
cd /var/www
sudo git clone <votre-repo> dreamslabs_manager
# OU copiez les fichiers via scp/rsync

# Exécutez le script d'installation
cd dreamslabs_manager
sudo chmod +x deployment/setup_server.sh
sudo ./deployment/setup_server.sh
```

**⚠️ IMPORTANT:** Après l'installation, modifiez le mot de passe PostgreSQL dans le fichier `.env`.

### 3. Configuration des variables d'environnement

Créez le fichier `.env` à la racine du projet:

```bash
cd /var/www/dreamslabs_manager
cp .env.example .env
nano .env
```

Modifiez les valeurs suivantes:
- `SECRET_KEY`: Générez une nouvelle clé secrète Django
- `DB_PASSWORD`: Le mot de passe PostgreSQL que vous avez configuré
- `ALLOWED_HOSTS`: Ajoutez votre domaine si vous en avez un

Pour générer une nouvelle SECRET_KEY:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Déploiement du code

```bash
cd /var/www/dreamslabs_manager
chmod +x deploy.sh
./deploy.sh
```

Le script va:
- Mettre à jour le code
- Installer les dépendances
- Appliquer les migrations
- Collecter les fichiers statiques
- Redémarrer les services

### 5. Initialisation des données

Après le premier déploiement, initialisez les rôles et données de base:

```bash
cd /var/www/dreamslabs_manager
source venv/bin/activate
python manage.py init_roles --settings=dreamslabs_manager.settings_production
python manage.py init_financial_data --settings=dreamslabs_manager.settings_production
python manage.py createsuperuser --settings=dreamslabs_manager.settings_production
```

## Commandes Utiles

### Vérifier le statut des services

```bash
# Statut de Gunicorn
sudo systemctl status dreamslabs_manager

# Statut de Nginx
sudo systemctl status nginx

# Statut de PostgreSQL
sudo systemctl status postgresql
```

### Voir les logs

```bash
# Logs de Gunicorn
sudo journalctl -u dreamslabs_manager -f

# Logs de Nginx
sudo tail -f /var/log/nginx/dreamslabs_manager_error.log

# Logs Django
tail -f /var/www/dreamslabs_manager/logs/django.log
```

### Redémarrer les services

```bash
# Redémarrer Gunicorn
sudo systemctl restart dreamslabs_manager

# Redémarrer Nginx
sudo systemctl restart nginx

# Recharger Nginx (sans interruption)
sudo systemctl reload nginx
```

### Mettre à jour le code

```bash
cd /var/www/dreamslabs_manager
./deploy.sh
```

## Structure des Fichiers

```
/var/www/dreamslabs_manager/
├── deployment/
│   ├── nginx.conf          # Configuration Nginx
│   ├── gunicorn.service    # Service systemd
│   ├── setup_server.sh     # Script d'installation initiale
│   └── README.md           # Ce fichier
├── .env                    # Variables d'environnement (à créer)
├── .env.example            # Exemple de variables d'environnement
├── deploy.sh               # Script de déploiement
├── manage.py
├── requirements.txt
└── ...
```

## Sécurité

### Firewall

Assurez-vous que le firewall est configuré:

```bash
sudo ufw status
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
```

### SSL/HTTPS (Optionnel mais recommandé)

Pour activer HTTPS avec Let's Encrypt:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

Puis modifiez `.env` pour activer les paramètres de sécurité:
```
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Dépannage

### Le service ne démarre pas

1. Vérifiez les logs: `sudo journalctl -u dreamslabs_manager -n 50`
2. Vérifiez que le fichier `.env` existe et est correct
3. Vérifiez que PostgreSQL est démarré: `sudo systemctl status postgresql`
4. Vérifiez les permissions: `ls -la /var/www/dreamslabs_manager`

### Erreur 502 Bad Gateway

1. Vérifiez que Gunicorn est actif: `sudo systemctl status dreamslabs_manager`
2. Vérifiez le socket: `ls -la /var/www/dreamslabs_manager/gunicorn.sock`
3. Vérifiez les logs Nginx: `sudo tail -f /var/log/nginx/dreamslabs_manager_error.log`

### Erreur de connexion à la base de données

1. Vérifiez que PostgreSQL est démarré
2. Vérifiez les identifiants dans `.env`
3. Testez la connexion: `sudo -u postgres psql -d dreamslabs_db -U dreamslabs_user`

## Configuration SSL/HTTPS avec Let's Encrypt

### Méthode HTTP-01 (Recommandée - Automatique)

La méthode HTTP-01 est plus simple et entièrement automatisée :

```bash
cd /var/www/dreamslabs_manager
sudo chmod +x deployment/setup_ssl_http01.sh
sudo ./deployment/setup_ssl_http01.sh
```

Ce script va :
1. Installer certbot
2. Obtenir automatiquement le certificat via HTTP-01
3. Configurer Nginx pour HTTPS avec redirection HTTP → HTTPS
4. Configurer le renouvellement automatique
5. Mettre à jour le fichier `.env` pour activer les paramètres de sécurité Django

**Prérequis :**
- Le domaine doit pointer vers le serveur (DNS configuré)
- Le port 80 doit être accessible depuis Internet
- Nginx doit être configuré et fonctionnel

### Méthode DNS-01 (Alternative - Manuelle)

Pour obtenir un certificat SSL avec la méthode DNS-01 (si HTTP-01 ne fonctionne pas) :

### Option 1 : Méthode manuelle (recommandée pour la première fois)

```bash
cd /var/www/dreamslabs_manager
sudo chmod +x deployment/setup_ssl_dns01.sh
sudo ./deployment/setup_ssl_dns01.sh
```

Ce script va :
1. Installer certbot
2. Vous guider pour ajouter un enregistrement TXT dans votre DNS
3. Obtenir le certificat
4. Configurer Nginx pour HTTPS
5. Configurer le renouvellement automatique

**Important :** Lors de la validation DNS, certbot vous donnera un enregistrement TXT à ajouter dans votre DNS pour `_acme-challenge.dreamlabsadmin.strangernet.com`.

### Option 2 : Méthode automatisée (nécessite un plugin DNS)

Si vous utilisez Cloudflare, Route53, ou Google Cloud DNS :

```bash
cd /var/www/dreamslabs_manager
sudo chmod +x deployment/setup_ssl_automated.sh
sudo ./deployment/setup_ssl_automated.sh
```

**Pour Cloudflare :**
1. Créez un token API dans Cloudflare
2. Créez `/etc/letsencrypt/cloudflare.ini` :
   ```
   dns_cloudflare_api_token = VOTRE_TOKEN_API
   ```
3. Exécutez le script

### Après l'installation SSL

Le script met automatiquement à jour :
- La configuration Nginx pour HTTPS
- Le fichier `.env` pour activer les paramètres de sécurité Django
- Le renouvellement automatique du certificat

Redémarrez le service Django :
```bash
sudo systemctl restart dreamslabs_manager
```

## Support

En cas de problème, vérifiez les logs et assurez-vous que tous les services sont actifs.
