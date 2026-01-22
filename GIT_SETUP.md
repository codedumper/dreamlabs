# 🔧 Configuration Git pour Dreamslabs Manager

Guide pour configurer Git et utiliser le workflow de déploiement basé sur Git.

## Initialisation Git (une seule fois)

### 1. Initialiser Git dans le projet

```bash
./init_git.sh
```

Ce script va :
- Initialiser Git si nécessaire
- Configurer le remote GitHub (https://github.com/codedumper/dreamlabs.git)
- Créer la branche `main`
- Vous proposer de faire un commit initial
- Optionnellement pousser vers GitHub

### 2. Ou manuellement

```bash
# Initialiser Git
git init

# Ajouter le remote
git remote add origin https://github.com/codedumper/dreamlabs.git

# Créer la branche main
git checkout -b main

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit"

# Pousser vers GitHub
git push -u origin main
```

## Workflow de Déploiement

### Déploiement Standard

1. **Faire vos modifications** dans le code

2. **Committer vos changements** :
```bash
git add .
git commit -m "Description de vos changements"
```

3. **Pousser vers GitHub** :
```bash
git push origin main
```

4. **Déployer sur le serveur** :
```bash
./deploy_to_server.sh
```

Le script `deploy_to_server.sh` va automatiquement :
- Pousser vos changements vers GitHub (si nécessaire)
- Mettre à jour le code sur le serveur via `git pull`
- Exécuter les migrations
- Redémarrer les services

### Déploiement Direct sur le Serveur

Si vous êtes directement sur le serveur :

```bash
cd /var/www/dreamslabs_manager
git pull origin main
./deploy.sh
```

## Structure Git

- **Branche principale** : `main`
- **Remote** : `origin` → https://github.com/codedumper/dreamlabs.git
- **Fichiers ignorés** : Voir `.gitignore`

## Commandes Utiles

```bash
# Voir le statut
git status

# Voir les différences
git diff

# Voir l'historique
git log --oneline

# Créer une nouvelle branche
git checkout -b feature/nom-feature

# Revenir à la branche main
git checkout main

# Annuler des changements non commités
git checkout -- fichier.py
git reset --hard HEAD

# Voir les remotes
git remote -v
```

## Dépannage

### Le remote n'est pas configuré
```bash
git remote add origin https://github.com/codedumper/dreamlabs.git
```

### Changer l'URL du remote
```bash
git remote set-url origin https://github.com/codedumper/dreamlabs.git
```

### Le serveur ne peut pas accéder à GitHub
Assurez-vous que :
- Le serveur a accès à Internet
- Git est installé sur le serveur : `sudo apt-get install git`
- Les credentials GitHub sont configurés (si le repo est privé)

Pour un repo privé, utilisez SSH ou un token :
```bash
# SSH
git remote set-url origin git@github.com:codedumper/dreamlabs.git

# HTTPS avec token
git remote set-url origin https://TOKEN@github.com/codedumper/dreamlabs.git
```
