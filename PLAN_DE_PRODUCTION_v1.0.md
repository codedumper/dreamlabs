# Plan de Production - Dreamslabs Manager
## Version 1.0

**Date de création :** 19/01/2026  
**Auteur :** Christophe Durieux  
**Basé sur :** SPECIFICATIONS_FONCTIONNELLES.md

---

## Vue d'ensemble

**Durée totale estimée :** 14-19 semaines (3,5-4,5 mois)  
**Équipe recommandée :** 1-2 développeurs full-stack Django

### Phases du projet

| Phase | Description | Durée | Statut |
|-------|-------------|-------|--------|
| **Phase 0** | Setup et Infrastructure | 2-3 semaines | En cours |
| **Phase 1** | Fonctionnalités de base | 8-10 semaines | Planifié |
| **Phase 2** | Rapports consolidés | 4-6 semaines | Planifié |

---

## Phase 0 : Setup et Infrastructure

**Durée :** 2-3 semaines  
**Objectif :** Mettre en place l'environnement de développement, l'architecture de base et les fondations de l'application.

### Sprint 0.1 : Configuration initiale (5 jours)

#### Jour 1-2 : Setup du projet Django
- [x] Créer le projet Django (`dreamslabs_manager`)
- [x] Configurer l'environnement virtuel Python
- [x] Installer Django (dernière version stable - 6.0.1)
- [x] Configurer les settings de base :
  - [x] Configuration de la base de données (SQLite pour dev, PostgreSQL pour prod)
  - [x] Configuration i18n pour espagnol colombien (es-CO)
  - [x] Configuration des timezones (America/Bogota)
  - [x] Configuration des formats de date/nombre/devise colombiens
- [x] Créer la structure des apps Django :
  - [x] `accounts` (authentification et utilisateurs)
  - [x] `agencies` (agences)
  - [x] `models_app` (modèles)
  - [x] `financial` (dépenses, salaires, revenus)
  - [x] `reports` (rapports - Phase 2)
- [x] Créer requirements.txt
- [x] Créer .gitignore
- [x] Créer README.md
- [x] Appliquer les migrations initiales

**Livrable :** Projet Django fonctionnel avec structure de base

#### Jour 3-4 : Configuration de la base de données
- [ ] Installer et configurer PostgreSQL
- [ ] Configurer les paramètres de connexion Django
- [ ] Créer le script de setup de la base de données
- [ ] Configurer les migrations Django
- [ ] Créer les scripts de backup/restore

**Livrable :** Base de données PostgreSQL configurée et accessible

#### Jour 5 : Système d'authentification de base
- [x] Configurer Django Auth (modèle User personnalisé)
- [x] Créer les modèles de base pour Utilisateur (User, Role)
- [x] Créer les modèles de base pour Agence (Agency)
- [x] Créer les vues de login/logout
- [x] Créer les templates de base pour l'authentification
- [x] Créer le template de base avec Bootstrap
- [x] Créer le dashboard de base
- [x] Créer la commande init_roles pour initialiser les rôles
- [x] Configurer l'admin Django pour User, Role et Agency
- [x] Tester le système d'authentification

**Livrable :** Système d'authentification fonctionnel ✓

---

### Sprint 0.2 : Système de rôles et permissions (5 jours)

#### Jour 1-2 : Modèle de rôles
- [x] Créer le modèle `Role` avec les 3 rôles :
  - [x] `GENERAL_MANAGER`
  - [x] `REGIONAL_MANAGER`
  - [x] `MODELE`
- [x] Créer la relation Utilisateur ↔ Rôle
- [x] Créer les migrations
- [x] Créer la commande de gestion pour initialiser les rôles
- [x] Initialiser les rôles en base de données

**Livrable :** Système de rôles en base de données ✓

#### Jour 3-4 : Middleware et contrôle d'accès
- [x] Créer un middleware pour vérifier les rôles (AgencyIsolationMiddleware)
- [x] Créer des décorateurs pour protéger les vues par rôle (role_required, general_manager_required, etc.)
- [x] Implémenter l'isolation des données par agence pour Regional Manager
- [x] Créer des helpers pour vérifier les permissions (utils.py)
- [x] Créer des tests unitaires de base
- [ ] Tests d'intégration complets (à compléter)

**Livrable :** Système de permissions et contrôle d'accès opérationnel ✓

#### Jour 5 : Modèles de base (Agence, Utilisateur)
- [x] Créer le modèle `Agency` (Agence)
- [x] Créer le modèle `User` étendu avec relation Agence
- [x] Créer les relations :
  - [x] Regional Manager ↔ Agence (via User.agency)
  - [ ] Modèle ↔ Agence (à venir dans models_app)
- [x] Créer les migrations
- [x] Configurer l'admin Django
- [ ] Créer les tests unitaires de base (à faire)

**Livrable :** Modèles Agence et Utilisateur fonctionnels ✓

---

### Sprint 0.3 : Interface utilisateur de base (5 jours)

#### Jour 1-2 : Template de base
- [x] Créer le template de base (`base.html`)
- [x] Intégrer un framework CSS (Bootstrap 5.3)
- [x] Créer la navigation principale avec menus conditionnels par rôle
- [x] Créer le système de layout responsive
- [x] Configurer les messages Django (success, error, etc.)
- [x] Navigation avec dropdowns pour agences, modèles, financier

**Livrable :** Template de base avec navigation ✓

#### Jour 3 : Localisation es-CO
- [ ] Configurer Django i18n pour es-CO
- [ ] Créer les fichiers de traduction de base
- [ ] Configurer les formats de date : DD/MM/YYYY
- [ ] Configurer les formats de nombre : point pour milliers, virgule pour décimales
- [ ] Configurer le format de devise : COP (Peso colombien)
- [ ] Tester l'affichage des formats

**Livrable :** Application localisée en espagnol colombien

#### Jour 4-5 : Pages de base
- [ ] Créer la page d'accueil (dashboard vide pour l'instant)
- [ ] Créer la page de profil utilisateur
- [ ] Créer les pages d'erreur (404, 403, 500)
- [ ] Créer le système de navigation conditionnelle selon le rôle
- [ ] Tester la navigation et l'affichage

**Livrable :** Interface utilisateur de base fonctionnelle

---

### Sprint 0.4 : Configuration déploiement et documentation (3 jours)

#### Jour 1 : Configuration environnement
- [ ] Configurer l'environnement de développement
- [ ] Créer le fichier `.env.example`
- [ ] Configurer les variables d'environnement
- [ ] Créer le script de setup pour nouveaux développeurs

#### Jour 2 : Configuration CI/CD de base
- [ ] Configurer Git et repository
- [ ] Créer le `.gitignore`
- [ ] Configurer les hooks Git de base
- [ ] Documenter le processus de déploiement

#### Jour 3 : Documentation initiale
- [ ] Créer le README.md du projet
- [ ] Documenter l'architecture de base
- [ ] Documenter les commandes de setup
- [ ] Créer un guide de contribution

**Livrable :** Projet prêt pour le développement collaboratif

---

## Phase 1 : Fonctionnalités de base

**Durée :** 8-10 semaines  
**Objectif :** Développer toutes les fonctionnalités opérationnelles de base.

### Sprint 1.1 : Gestion des Agences et Utilisateurs (1 semaine)

#### Tâches
- [x] **CRUD Agences** (2 jours)
  - [x] Vue liste des agences (avec permissions par rôle)
  - [x] Vue création agence (General Manager uniquement)
  - [x] Vue modification agence (General Manager uniquement)
  - [x] Vue détail agence (avec permissions)
  - [x] Validation et règles métier
  - [x] Templates Bootstrap créés
  - [ ] Tests unitaires (à compléter)

- [ ] **Gestion des utilisateurs et rôles** (3 jours)
  - [ ] Vue liste des utilisateurs
  - [ ] Vue création utilisateur avec attribution de rôle
  - [ ] Vue modification utilisateur
  - [ ] Association Regional Manager ↔ Agence
  - [ ] Gestion des comptes Modèle (optionnel)
  - [x] Interface d'administration Django (déjà fait)
  - [ ] Tests unitaires

**Livrable :** Gestion complète des agences opérationnelle ✓ (utilisateurs à venir)

---

### Sprint 1.2 : Gestion des Modèles (2 semaines)

#### Semaine 1 : Modèles et CRUD
- [x] **Modèle de données Modèle** (2 jours)
  - [x] Créer le modèle `Model` (Modèle)
  - [x] Champs : nom, prénom, email, téléphone, statut (actif/inactif)
  - [x] Relation Modèle ↔ Agence
  - [x] Relation Modèle ↔ User (optionnel)
  - [x] Méthode de désactivation avec timestamp
  - [x] Migrations
  - [ ] Tests unitaires du modèle (à compléter)

- [x] **CRUD Modèles** (3 jours)
  - [x] Vue liste des modèles (filtre actif/inactif)
  - [x] Vue création modèle (Regional Manager uniquement)
  - [x] Vue modification modèle
  - [x] Fonction de désactivation (soft delete avec conservation des données)
  - [x] Validation des permissions
  - [x] Isolation par agence
  - [x] Création optionnelle de compte utilisateur lors de la création
  - [x] Templates Bootstrap complets
  - [ ] Tests unitaires et d'intégration (à compléter)

#### Semaine 2 : Fiche du modèle
- [x] **Fiche du modèle** (2 jours)
  - [x] Vue détaillée du modèle
  - [x] Affichage des informations de base
  - [x] Section pour liste des gains (placeholder - à venir Sprint 1.3)
  - [x] Section pour liste des heures travaillées (placeholder - à venir Sprint 1.4)
  - [x] Affichage des informations de compte utilisateur si existe
  - [x] Design responsive

- [x] **Règles métier et permissions** (1 jour)
  - [x] Validation complète des permissions
  - [x] Isolation par agence fonctionnelle
  - [x] Masquage des modèles inactifs dans les listes opérationnelles
  - [ ] Tests de sécurité (accès non autorisé) (à compléter)
  - [x] Documentation des règles métier dans le code

**Livrable :** Gestion complète des modèles avec CRUD et fiche détaillée ✓

---

### Sprint 1.3 : Gestion des Gains des Modèles (1,5 semaines)

#### Tâches
- [x] **Modèle de données Gains** (1 jour)
  - [x] Créer le modèle `ModelGain` (GainModèle)
  - [x] Champs : modèle, date, montant, description (optionnel)
  - [x] Relation GainModèle ↔ Modèle
  - [x] Validation (montant > 0, date valide)
  - [x] Contrainte unique (modèle, date) pour éviter les doublons
  - [x] Champ created_by pour tracer qui a créé le gain
  - [x] Migrations
  - [ ] Tests unitaires (à compléter)

- [x] **Saisie quotidienne des gains** (3 jours)
  - [x] Vue de saisie par modèle
  - [x] Formulaire avec validation
  - [x] Enregistrement des gains (création ou mise à jour si existe déjà)
  - [x] Gestion des erreurs
  - [x] Messages de confirmation
  - [x] Template Bootstrap
  - [ ] Tests d'intégration (à compléter)

- [x] **Historique et consultation** (2 jours)
  - [x] Affichage dans la fiche du modèle
  - [x] Liste des gains avec dates
  - [x] Filtres par période (date_from, date_to)
  - [x] Tri par date (plus récent en premier)
  - [x] Affichage du total des gains
  - [x] Consultation par le modèle (si compte utilisateur) - via la fiche
  - [x] Template avec tableau responsive
  - [ ] Tests (à compléter)

- [x] **Masquage des modèles désactivés** (1 jour)
  - [x] Filtrage automatique dans les interfaces opérationnelles (déjà fait dans model_list)
  - [x] Conservation dans les rapports financiers (les gains restent accessibles)
  - [x] Admin Django configuré avec filtrage par agence
  - [ ] Tests de filtrage (à compléter)

**Livrable :** Système de gestion des gains opérationnel ✓

---

### Sprint 1.4 : Gestion des Heures Travaillées (1,5 semaines)

#### Tâches
- [x] **Modèle de données Heures Travaillées** (1 jour)
  - [x] Créer le modèle `WorkedHours` (HeuresTravaillées)
  - [x] Champs : modèle, date, heures (décimal)
  - [x] Relation avec Modèle et Date
  - [x] Validation (heures >= 0, date valide)
  - [x] Contrainte unique (modèle, date)
  - [x] Champ created_by pour tracer qui a créé
  - [x] Migrations
  - [ ] Tests unitaires (à compléter)

- [x] **Page de saisie groupée des heures** (4 jours)
  - [x] Vue avec sélecteur de date (jour courant par défaut)
  - [x] Affichage de tous les modèles actifs de l'agence
  - [x] Formulaire de saisie pour tous les modèles
  - [x] Validation côté serveur
  - [x] Enregistrement groupé (bulk create/update)
  - [x] Affichage des heures déjà enregistrées
  - [x] Indicateur visuel (badge) pour les heures déjà enregistrées
  - [x] Gestion des erreurs partielles
  - [x] Messages de confirmation
  - [x] Template Bootstrap avec tableau
  - [x] Template tag personnalisé pour accéder aux dictionnaires
  - [ ] Tests d'intégration (à compléter)

- [x] **Affichage dans la fiche du modèle** (2 jours)
  - [x] Liste des heures travaillées avec dates
  - [x] Filtrage par période (date_from, date_to)
  - [x] Statistiques (total heures, moyenne)
  - [x] Consultation par le modèle (si compte utilisateur) - via la fiche
  - [x] Template avec tableau responsive
  - [ ] Tests (à compléter)

**Livrable :** Système de gestion des heures travaillées opérationnel ✓

---

### Sprint 1.5 : Gestion des Dépenses (1 semaine)

#### Tâches
- [x] **Modèle de données Dépenses** (1 jour)
  - [x] Créer le modèle `Expense` (Dépense)
  - [x] Champs : agence, date, montant, catégorie, description
  - [x] Relation avec Agence
  - [x] Modèle `ExpenseCategory` pour catégorisation
  - [x] Migrations
  - [x] Commande d'initialisation des catégories
  - [ ] Tests unitaires (à compléter)

- [x] **CRUD Dépenses** (3 jours)
  - [x] Vue liste des dépenses
  - [x] Vue création dépense
  - [x] Vue modification dépense
  - [x] Vue suppression dépense
  - [x] Filtres : par période, catégorie, agence
  - [x] Validation des permissions (Regional Manager uniquement)
  - [x] Templates Bootstrap
  - [x] Statistiques (total des dépenses)
  - [ ] Tests (à compléter)

- [x] **Consultation et rapports de base** (1 jour)
  - [x] Totaux par période
  - [x] Totaux par catégorie (via filtres)
  - [ ] Graphiques de base (Phase 2)
  - [ ] Export CSV (Phase 2)

**Livrable :** Gestion complète des dépenses opérationnelle ✓

---

### Sprint 1.6 : Gestion des Salaires (1 semaine)

#### Tâches
- [x] **Modèle de données Salaires** (1 jour)
  - [x] Créer le modèle `Salary` (Salaire)
  - [x] Champs : agence, employé, date_paiement, montant, période (début/fin)
  - [x] Relation avec Agence
  - [x] Modèle `Employee` pour les employés
  - [x] Migrations
  - [ ] Tests unitaires (à compléter)

- [x] **CRUD Salaires** (3 jours)
  - [x] Vue liste des salaires
  - [x] Vue création salaire
  - [x] Filtres : par période, employé, agence
  - [x] Validation des permissions (Regional Manager uniquement)
  - [x] Templates Bootstrap
  - [x] Statistiques (total des salaires)
  - [ ] Vue modification salaire (à ajouter si nécessaire)
  - [ ] Vue suppression salaire (à ajouter si nécessaire)
  - [ ] Tests (à compléter)

- [x] **Consultation et rapports de base** (1 jour)
  - [x] Totaux par agence
  - [x] Totaux par période
  - [x] Statistiques de base
  - [ ] Export CSV (Phase 2)

**Livrable :** Gestion complète des salaires opérationnelle ✓

---

### Sprint 1.7 : Gestion des Revenus (1 semaine)

#### Tâches
- [x] **Modèle de données Revenus** (1 jour)
  - [x] Créer le modèle `Revenue` (Revenu)
  - [x] Champs : agence, date, montant, source, description
  - [x] Relation avec Agence
  - [x] Modèle `RevenueSource` pour catégorisation
  - [x] Migrations
  - [x] Commande d'initialisation des sources
  - [ ] Tests unitaires (à compléter)

- [x] **CRUD Revenus** (3 jours)
  - [x] Vue liste des revenus
  - [x] Vue création revenu
  - [x] Filtres : par période, source, agence
  - [x] Validation des permissions (Regional Manager uniquement)
  - [x] Templates Bootstrap
  - [x] Statistiques (total des revenus)
  - [ ] Vue modification revenu (à ajouter si nécessaire)
  - [ ] Vue suppression revenu (à ajouter si nécessaire)
  - [ ] Tests (à compléter)

- [x] **Consultation et rapports de base** (1 jour)
  - [x] Totaux par période
  - [x] Totaux par source (via filtres)
  - [ ] Graphiques de base (Phase 2)
  - [ ] Export CSV (Phase 2)

**Livrable :** Gestion complète des revenus opérationnelle ✓

---

### Sprint 1.8 : Tableaux de Bord de Base (1,5 semaines)

#### Tâches
- [x] **Tableau de bord Regional Manager** (3 jours)
  - [x] Vue consolidée de l'agence
  - [x] Indicateurs clés :
    - [x] Total dépenses (période)
    - [x] Total revenus (période)
    - [x] Total salaires (période)
    - [x] Total gains modèles (période)
    - [x] Bilan (revenus - dépenses - salaires)
  - [x] Filtres par période
  - [x] Activité récente (dépenses et revenus)
  - [x] Statistiques supplémentaires (modèles actifs, heures travaillées)
  - [x] Templates Bootstrap avec cartes
  - [ ] Graphiques de base (Phase 2)
  - [ ] Tests (à compléter)

- [x] **Tableau de bord General Manager** (3 jours)
  - [x] Vue consolidée des 2 agences
  - [x] Indicateurs globaux
  - [x] Comparaisons entre agences (tableau)
  - [x] Filtres par période
  - [x] Statistiques globales (total modèles actifs, agences)
  - [x] Templates Bootstrap avec cartes
  - [ ] Graphiques comparatifs (Phase 2)
  - [ ] Tests (à compléter)

- [x] **Tableau de bord Modèle** (1 jour)
  - [x] Vue personnelle des gains
  - [x] Vue personnelle des heures travaillées
  - [x] Statistiques personnelles (total gains, total heures, moyenne heures/jour)
  - [x] Filtres par période
  - [x] Historique récent (gains et heures)
  - [x] Templates Bootstrap avec cartes
  - [ ] Tests (à compléter)

**Livrable :** Tableaux de bord de base opérationnels pour tous les rôles ✓

---

### Sprint 1.9 : Tests, Optimisation et Documentation (1 semaine)

#### Tâches
- [ ] **Tests d'intégration** (2 jours)
  - [ ] Tests end-to-end des parcours utilisateurs
  - [ ] Tests de permissions et sécurité
  - [ ] Tests de performance de base
  - [ ] Tests de localisation es-CO

- [ ] **Optimisation et corrections** (2 jours)
  - [ ] Correction des bugs identifiés
  - [ ] Optimisation des requêtes (select_related, prefetch_related)
  - [ ] Optimisation des vues
  - [ ] Amélioration de l'UX
  - [ ] Vérification de l'accessibilité de base

- [ ] **Documentation** (1 jour)
  - [ ] Documentation utilisateur de base
  - [ ] Guide d'administration
  - [ ] Documentation technique
  - [ ] Mise à jour du README

**Livrable :** Application Phase 1 testée, optimisée et documentée

---

## Phase 2 : Rapports Consolidés

**Durée :** 4-6 semaines  
**Objectif :** Développer les rapports consolidés avancés et les analyses.

> **Note :** Les détails de la Phase 2 seront définis après validation de la Phase 1.

### Vue d'ensemble Phase 2

- **Sprint 2.1 :** Rapports consolidés Regional Manager (2 semaines)
- **Sprint 2.2 :** Rapports consolidés General Manager (2 semaines)
- **Sprint 2.3 :** Analyses avancées et projections (1 semaine)
- **Sprint 2.4 :** Tests finaux et optimisation (1 semaine)

---

## Jalons et Critères d'Acceptation

### Jalon M0 : Fin Phase 0
**Date cible :** Semaine 3  
**Critères :**
- [ ] Authentification fonctionnelle
- [ ] Base de données configurée et accessible
- [ ] Système de rôles opérationnel
- [ ] Interface utilisateur de base en es-CO
- [ ] Documentation de setup complète

### Jalon M1 : Fin Phase 1
**Date cible :** Semaine 11-13  
**Critères :**
- [ ] Toutes les fonctionnalités de base opérationnelles
- [ ] Tests unitaires et d'intégration passés (>80% coverage)
- [ ] Documentation utilisateur de base
- [ ] Application déployable en staging
- [ ] Performance acceptable (<2s temps de chargement)

### Jalon M2 : Fin Phase 2
**Date cible :** Semaine 15-19  
**Critères :**
- [ ] Tous les rapports consolidés opérationnels
- [ ] Tests complets passés
- [ ] Documentation complète
- [ ] Application prête pour production
- [ ] Formation utilisateurs effectuée

---

## Estimation des Ressources

### Équipe recommandée
- **1 Développeur Full-Stack Django** (lead) - Temps plein
- **1 Développeur Frontend** (optionnel) - Temps partiel si frontend séparé
- **1 Designer UX/UI** - Temps partiel (surtout Phase 1)
- **1 Testeur QA** - À partir de la fin Phase 1

### Estimation par phase

| Phase | Durée | Heures estimées | Développeurs |
|-------|-------|-----------------|--------------|
| Phase 0 | 2-3 semaines | 80-120h | 1 |
| Phase 1 | 8-10 semaines | 320-400h | 1-2 |
| Phase 2 | 4-6 semaines | 160-240h | 1-2 |
| **Total** | **14-19 semaines** | **560-760h** | **1-2** |

---

## Dépendances et Risques

### Dépendances critiques
- [ ] Choix définitif de la base de données (recommandé : PostgreSQL)
- [ ] Choix du frontend (Django templates ou framework séparé)
- [ ] Validation des besoins avec les utilisateurs finaux
- [ ] Accès aux données de test/exemples

### Risques identifiés

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Complexité des rapports consolidés | Élevé | Moyen | Prototypage précoce, validation itérative |
| Performance avec volumes importants | Moyen | Faible | Optimisation continue, tests de charge |
| Localisation es-CO complète | Moyen | Faible | Vérification systématique, tests utilisateurs |
| Gestion des permissions complexes | Moyen | Moyen | Tests de sécurité approfondis, revue de code |

---

## Prochaines Étapes Immédiates

1. [ ] **Validation du plan** : Révision et approbation du plan de production
2. [ ] **Setup de l'environnement** : Installation des outils de développement
3. [ ] **Démarrage Phase 0** : Commencer le Sprint 0.1
4. [ ] **Mise en place du suivi** : Configuration du système de suivi des tâches (Trello, Jira, etc.)
5. [ ] **Réunions de suivi** : Planification des réunions de suivi hebdomadaires

---

## Notes de Version

### Version 1.0 (19/01/2026)
- Plan de production initial basé sur les spécifications fonctionnelles
- Détail complet de la Phase 0 et Phase 1
- Structure de base pour la Phase 2
- Estimations initiales

**Prochaines itérations :**
- Affinement des estimations après premiers sprints
- Détail complet de la Phase 2 après validation Phase 1
- Ajustements basés sur les retours utilisateurs

---

**Document à mettre à jour régulièrement au fur et à mesure de l'avancement du projet.**
