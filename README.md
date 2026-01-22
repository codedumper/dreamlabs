# Dreamslabs Manager

Application de gestion financière pour Dreamslabs - Suivi des dépenses, salaires, revenus et modèles.

## Technologies

- **Framework :** Django 6.0.1
- **Langage :** Python 3.14+
- **Base de données :** SQLite (développement) / PostgreSQL (production)
- **Localisation :** Espagnol colombien (es-CO)

## Installation

### Prérequis

- Python 3.14 ou supérieur
- pip
- Git (pour le déploiement)

### Setup

1. **Initialiser Git** (si ce n'est pas déjà fait) :
```bash
./init_git.sh
```

2. Cloner le repository (ou créer le projet)

2. Créer un environnement virtuel :
```bash
python3 -m venv venv
```

3. Activer l'environnement virtuel :
```bash
# Sur macOS/Linux
source venv/bin/activate

# Sur Windows
venv\Scripts\activate
```

4. Installer les dépendances :
```bash
pip install -r requirements.txt
```

5. Appliquer les migrations :
```bash
python manage.py migrate
```

6. Créer un superutilisateur :
```bash
# Option 1 : Utiliser le script fourni
python create_superuser.py

# Option 2 : Utiliser la commande Django (interactive)
python manage.py createsuperuser
```

**Compte par défaut créé par le script :**
- Username: `admin`
- Password: `admin`
- Email: `admin@dreamslabs.com`

7. Lancer le serveur de développement :
```bash
python manage.py runserver
```

L'application sera accessible sur http://127.0.0.1:8000/

## Structure du projet

```
dreamslabs_manager/
├── accounts/          # Authentification et gestion des utilisateurs
├── agencies/          # Gestion des agences
├── models_app/        # Gestion des modèles
├── financial/         # Dépenses, salaires, revenus
├── reports/           # Rapports consolidés (Phase 2)
└── dreamslabs_manager/ # Configuration du projet
```

## Configuration

### Localisation

L'application est configurée pour l'espagnol colombien (es-CO) :
- Format de date : DD/MM/YYYY
- Format de nombres : point pour milliers, virgule pour décimales
- Devise : COP (Peso colombien)
- Timezone : America/Bogota

### Variables d'environnement

Créer un fichier `.env` à la racine du projet avec :
```
SECRET_KEY=votre_secret_key_ici
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## Développement

### Commandes utiles

- Créer une migration : `python manage.py makemigrations`
- Appliquer les migrations : `python manage.py migrate`
- Créer un superutilisateur : `python manage.py createsuperuser`
- Lancer les tests : `python manage.py test`
- Collecter les fichiers statiques : `python manage.py collectstatic`

### Rôles utilisateurs

- **General Manager** : Accès en lecture à toutes les données
- **Regional Manager** : Gestion complète de son agence
- **Modèle** : Consultation de ses propres données

## Documentation

- [Spécifications Fonctionnelles](SPECIFICATIONS_FONCTIONNELLES.md)
- [Plan de Production](PLAN_DE_PRODUCTION_v1.0.md)

## Statut du projet

**Phase actuelle :** Phase 0 - Setup et Infrastructure

## Auteur

Christophe Durieux - 2026
