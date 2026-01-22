# Spécifications Fonctionnelles - Dreamslabs Manager

## Document de Conception - Plan de Production

**Date de création :** 19/01/2026  
**Version :** 1.0  
**Auteur :** Christophe Durieux

---

## 1. Introduction

### 1.1 Contexte
Dreamslabs est une entreprise composée de 2 agences, chacune dirigée par un manager. L'ensemble est supervisé par un manager général global. L'entreprise a besoin d'un outil de gestion financière pour suivre efficacement ses dépenses, les salaires de ses employés et ses revenus. L'entreprise travaille également avec des modèles associés à chaque agence, rémunérés sur une base variable selon le travail effectué. L'application doit permettre le suivi en temps réel de l'arrivée et du départ des modèles, ainsi que l'enregistrement quotidien de leurs gains. Cette application permettra une vision centralisée et détaillée de la santé financière de l'entreprise, tout en permettant une gestion décentralisée par agence.

### 1.2 Objectifs
- Permettre le suivi et la gestion des dépenses de l'entreprise
- Gérer le suivi des salaires des employés
- Suivre les revenus générés par l'entreprise
- Suivre en temps réel l'arrivée et le départ des modèles
- Gérer l'enregistrement quotidien des gains des modèles actifs
- Offrir une vue consolidée au manager général global
- Permettre une gestion autonome par agence pour chaque manager d'agence
- Fournir des rapports et analyses financières pour la prise de décision
- Conserver l'historique financier des modèles ayant quitté l'agence
- Offrir des rapports consolidés aux managers d'agence (Phase 2)
- Offrir des rapports consolidés au manager général global (Phase 2)

### 1.3 Portée du projet
**Phase 1 (Incluse) :**
- Gestion des dépenses, salaires et revenus
- Gestion des modèles (ajout, suivi quotidien, désactivation)
- Tableaux de bord de base
- Interfaces de saisie et consultation

**Phase 2 (Incluse) :**
- Rapports consolidés pour managers d'agence
- Rapports consolidés pour manager général global
- Analyses comparatives et indicateurs de performance

**Exclu du projet :**
- Gestion de la paie complète (calculs de charges sociales complexes)
- Système de facturation client
- Gestion de la comptabilité générale complète

---

## 2. Description Générale

### 2.1 Vue d'ensemble
Dreamslabs Manager est une application de gestion financière permettant de suivre les dépenses, les salaires et les revenus de l'entreprise Dreamslabs. L'application est structurée pour refléter l'organisation de l'entreprise avec 2 agences distinctes, chacune gérée par un manager, sous la supervision d'un manager général global. L'application gère également le suivi des modèles associés à chaque agence, avec enregistrement quotidien de leurs gains variables. L'application offre des fonctionnalités de saisie, consultation, analyse et reporting financier adaptées aux différents niveaux de responsabilité, tout en conservant l'intégrité des données historiques. L'interface utilisateur et tous les contenus seront en espagnol colombien.

### 2.2 Public cible

L'application gère trois types d'utilisateurs avec des rôles distincts :

- **General Manager (Manager Général Global)** : Accès à toutes les données consolidées des 2 agences, avec possibilité de consultation et d'analyse globale
- **Regional Manager (Manager Régional/Manager d'Agence)** : Accès aux données de leur agence respective pour la gestion des dépenses, salaires, revenus et modèles de leur périmètre. Responsables de l'ajout des nouveaux modèles, de l'enregistrement quotidien des gains et de la désactivation des modèles à leur départ
- **Modèle** : Accès limité à leurs propres données (consultation de leurs gains, historique personnel)

### 2.3 Contraintes
- **Linguistique** : L'application doit être entièrement en espagnol colombien (interface utilisateur, messages, rapports, documentation)
- [Autres contraintes techniques, budgétaires, temporelles, etc.]

---

## 3. Besoins Fonctionnels

### 3.1 Fonctionnalités principales

#### 3.1.1 Gestion des Dépenses
- Saisie et enregistrement des dépenses par agence
- Catégorisation des dépenses
- Suivi temporel des dépenses (mensuel, trimestriel, annuel)
- Consultation et filtrage des dépenses

#### 3.1.2 Gestion des Salaires
- Enregistrement des salaires des employés par agence
- Suivi des paiements de salaires
- Gestion des informations salariales par employé
- Calculs et totaux des charges salariales

#### 3.1.3 Gestion des Revenus
- Enregistrement des revenus par agence
- Suivi des revenus dans le temps
- Catégorisation des sources de revenus
- Consultation et analyse des revenus

#### 3.1.4 Gestion des Modèles
- Ajout de nouveaux modèles par le Regional Manager
- Association d'un modèle à une agence
- Création optionnelle d'un compte utilisateur pour un modèle (avec rôle "Modèle")
- Suivi en temps réel de l'état des modèles (actif/inactif)
- Enregistrement quotidien des gains pour chaque modèle actif (par le Regional Manager)
- Enregistrement quotidien des heures travaillées pour chaque modèle actif
- Désactivation des modèles à leur départ de l'agence
- Conservation des données historiques des modèles désactivés pour l'intégrité financière
- Masquage des modèles désactivés dans les parties opérationnelles de l'application
- Consultation de l'historique des modèles désactivés (pour les rapports financiers uniquement)
- Consultation par un modèle de ses propres gains et historique (si compte utilisateur créé)

#### 3.1.5 Gestion des Heures Travaillées
- **Page de saisie des heures** :
  - Affichage de tous les modèles actifs de l'agence
  - Sélection de la date (par défaut : jour courant)
  - Saisie des heures travaillées pour chaque modèle pour le jour sélectionné
  - Possibilité de saisir les heures pour tous les modèles en une seule page
  - Validation et enregistrement des heures

- **Fiche du modèle** :
  - Affichage des informations du modèle
  - Liste complète des heures travaillées avec dates
  - Consultation de l'historique des heures travaillées
  - Filtrage et recherche dans l'historique des heures

#### 3.1.6 Tableaux de Bord et Rapports
- Vue consolidée pour le manager général (toutes agences)
- Vue par agence pour les managers d'agence
- Rapports financiers (bilan, trésorerie, etc.)
- Analyses et statistiques
- Rapports incluant les données historiques des modèles désactivés

### 3.2 Fonctionnalités secondaires

#### 3.2.1 Rapports Consolidés (Phase 2)
- **Rapports consolidés pour Managers d'Agence** :
  - Vue consolidée de toutes les données financières de leur agence (dépenses, salaires, revenus, gains des modèles)
  - Rapports périodiques (quotidien, hebdomadaire, mensuel, trimestriel, annuel)
  - Analyses comparatives dans le temps
  - Indicateurs de performance de l'agence
  - Synthèse des gains des modèles actifs et historiques
  - Bilan financier de l'agence

- **Rapports consolidés pour Manager Général Global** :
  - Vue consolidée de toutes les données des 2 agences
  - Rapports comparatifs entre agences
  - Rapports périodiques globaux (quotidien, hebdomadaire, mensuel, trimestriel, annuel)
  - Indicateurs de performance globale de l'entreprise
  - Synthèse financière complète (dépenses, salaires, revenus, gains modèles)
  - Bilan financier consolidé de l'entreprise
  - Analyses de tendances et projections

### 3.3 Règles métier

#### 3.3.1 Gestion des Modèles
- Un modèle est associé à une et une seule agence
- Seul le Regional Manager peut ajouter, modifier ou désactiver les modèles de son agence
- Les modèles sont rémunérés sur une base variable selon le travail effectué
- Les gains doivent être enregistrés quotidiennement pour chaque modèle actif
- Les heures travaillées doivent être enregistrées quotidiennement pour chaque modèle actif
- Lorsqu'un modèle quitte l'agence, il doit être désactivé (et non supprimé)
- Les données financières liées à un modèle désactivé doivent être conservées pour garantir l'intégrité des rapports financiers
- Un modèle désactivé ne doit plus apparaître dans les interfaces opérationnelles (listes actives, saisie quotidienne, etc.)
- Les données historiques des modèles désactivés restent accessibles uniquement dans les rapports financiers et analyses historiques
- Un modèle ne peut pas être réactivé après désactivation (considéré comme départ définitif)

#### 3.3.4 Gestion des Heures Travaillées
- Les heures travaillées sont enregistrées par jour et par modèle
- Seul le Regional Manager peut saisir ou modifier les heures travaillées pour les modèles de son agence
- La page de saisie affiche par défaut le jour courant
- Il est possible de sélectionner une autre date pour la saisie
- Les heures travaillées sont associées à une date et un modèle
- Un modèle peut consulter ses propres heures travaillées via sa fiche (si compte utilisateur créé)
- Les heures travaillées des modèles désactivés restent consultables dans l'historique mais ne peuvent plus être modifiées

#### 3.3.2 Gestion des Agences
- Chaque agence est indépendante dans sa gestion opérationnelle
- Le General Manager a accès en lecture à toutes les données consolidées

#### 3.3.3 Gestion des Rôles et Permissions

**General Manager :**
- Accès en lecture seule à toutes les données des 2 agences
- Consultation des rapports consolidés globaux
- Accès aux analyses et statistiques globales
- Pas d'accès aux fonctions de saisie/modification des données opérationnelles

**Regional Manager :**
- Accès complet (lecture/écriture) aux données de son agence uniquement
- Gestion des dépenses, salaires et revenus de son agence
- Ajout, modification et désactivation des modèles de son agence
- Enregistrement quotidien des gains des modèles de son agence
- Enregistrement quotidien des heures travaillées des modèles de son agence
- Consultation des rapports de son agence
- Consultation des fiches des modèles de son agence avec leurs heures travaillées
- Pas d'accès aux données des autres agences

**Modèle :**
- Accès en lecture seule à ses propres données
- Consultation de ses gains personnels
- Consultation de son historique de gains
- Consultation de ses heures travaillées via sa fiche personnelle
- Consultation de son historique d'heures travaillées
- Pas d'accès aux données d'autres modèles ou aux données financières de l'agence

---

## 4. Besoins Non-Fonctionnels

### 4.1 Performance
[Exigences de performance]

### 4.2 Sécurité
- Système d'authentification et d'autorisation basé sur les rôles (RBAC)
- Gestion des rôles utilisateurs : General Manager, Regional Manager, Modèle
- Contrôle d'accès granulaire selon le rôle de l'utilisateur
- Isolation des données par agence pour les Regional Managers
- Protection des données sensibles financières
- Chiffrement des mots de passe
- Sessions sécurisées

### 4.3 Disponibilité
[Exigences de disponibilité]

### 4.4 Utilisabilité
- Interface utilisateur intuitive et ergonomique
- Tous les textes, labels, messages et rapports en espagnol colombien
- Formatage des dates, nombres et devises selon les conventions colombiennes
- Support des caractères spéciaux de l'espagnol (accents, ñ, etc.)

### 4.5 Compatibilité
- **Localisation** : Application entièrement localisée en espagnol colombien (es-CO)
- **Format de données** : 
  - Format de date : DD/MM/YYYY (format colombien)
  - Format de devise : COP (Peso colombien) avec séparateurs appropriés
  - Format de nombres : Utilisation des conventions colombiennes (point pour milliers, virgule pour décimales)
- Support UTF-8 pour les caractères accentués et spéciaux

---

## 5. Architecture et Technologies

### 5.1 Architecture proposée
[À compléter]

### 5.2 Stack technologique
- **Framework Backend** : Django (dernière version stable)
- **Base de données** : [À déterminer - PostgreSQL recommandé pour la production]
- **Frontend** : [À compléter]
- **Langage de programmation** : Python 3.x
- **Gestion des dépendances** : pip / requirements.txt
- **Localisation** : Support Django i18n pour l'espagnol colombien (es-CO)

### 5.3 Infrastructure
[À compléter]

---

## 6. Modèle de Données

### 6.1 Entités principales
- **Agence** : Représente une agence de l'entreprise (2 agences au total)
- **Utilisateur** : Compte utilisateur de l'application avec un rôle associé
- **Rôle** : Type d'utilisateur (General Manager, Regional Manager, Modèle)
- **Modèle** : Personne associée à une agence, avec statut actif/inactif. Peut avoir un compte utilisateur avec le rôle "Modèle"
- **Gain Modèle** : Enregistrement quotidien des gains d'un modèle actif
- **Heures Travaillées** : Enregistrement quotidien des heures travaillées d'un modèle pour une date donnée
- **Dépense** : Dépense enregistrée pour une agence
- **Salaire** : Salaire d'un employé associé à une agence
- **Revenu** : Revenu généré par une agence

### 6.2 Relations
- Un **Utilisateur** a un et un seul **Rôle** (General Manager, Regional Manager, ou Modèle)
- Un **Regional Manager** est associé à une et une seule **Agence**
- Un **Modèle** est associé à une et une seule **Agence**
- Un **Modèle** peut avoir un compte **Utilisateur** (optionnel, pour consultation de ses données)
- Un **Gain Modèle** est associé à un **Modèle** et une date
- Un enregistrement **Heures Travaillées** est associé à un **Modèle** et une date
- Une **Dépense** est associée à une **Agence**
- Un **Salaire** est associé à une **Agence**
- Un **Revenu** est associé à une **Agence**

### 6.3 Schéma de base de données
[À compléter]

---

## 7. Interfaces Utilisateur

### 7.1 Maquettes et wireframes
[À compléter]

### 7.2 Parcours utilisateur

#### 7.2.1 Parcours Regional Manager - Saisie des heures
1. Accès à la page "Saisie des heures"
2. Affichage par défaut du jour courant
3. Possibilité de sélectionner une autre date via un sélecteur de date
4. Affichage de la liste de tous les modèles actifs de l'agence
5. Saisie des heures travaillées pour chaque modèle dans un formulaire
6. Validation et enregistrement des heures pour tous les modèles
7. Confirmation de l'enregistrement

#### 7.2.2 Parcours Regional Manager - Consultation fiche modèle
1. Accès à la liste des modèles
2. Sélection d'un modèle
3. Affichage de la fiche du modèle avec ses informations
4. Consultation de la liste des heures travaillées avec dates
5. Filtrage et recherche dans l'historique des heures si nécessaire

#### 7.2.3 Parcours Modèle - Consultation de ses heures
1. Connexion avec compte utilisateur (rôle Modèle)
2. Accès à sa fiche personnelle
3. Consultation de la liste de ses heures travaillées avec dates
4. Filtrage et recherche dans son historique si nécessaire

---

## 8. Intégrations

### 8.1 APIs externes
[À compléter]

### 8.2 Services tiers
[À compléter]

---

## 9. Plan de Production

### 9.1 Vue d'ensemble

Le plan de production est structuré en 3 phases principales :
- **Phase 0** : Setup et infrastructure (2-3 semaines)
- **Phase 1** : Fonctionnalités de base (8-10 semaines)
- **Phase 2** : Rapports consolidés (4-6 semaines)

**Durée totale estimée :** 14-19 semaines (3,5-4,5 mois)

### 9.2 Phases de développement détaillées

#### Phase 0 : Setup et Infrastructure (2-3 semaines)

**Objectif :** Mettre en place l'environnement de développement, l'architecture de base et les fondations de l'application.

**Tâches :**
1. **Setup du projet Django** (2 jours)
   - Création du projet Django
   - Configuration de l'environnement virtuel
   - Configuration des settings (base de données, i18n pour es-CO)
   - Structure des apps Django

2. **Configuration de la base de données** (2 jours)
   - Choix et configuration de la base de données (PostgreSQL recommandé)
   - Configuration des migrations Django
   - Scripts de setup initial

3. **Système d'authentification et autorisation** (5 jours)
   - Configuration de Django Auth
   - Création du système de rôles (General Manager, Regional Manager, Modèle)
   - Middleware de contrôle d'accès par rôle
   - Système de permissions granulaire
   - Isolation des données par agence

4. **Modèle de données de base** (4 jours)
   - Modèles : Agence, Utilisateur, Rôle
   - Relations de base
   - Migrations initiales
   - Tests unitaires des modèles

5. **Interface utilisateur de base** (3 jours)
   - Template de base avec navigation
   - Système de layout responsive
   - Configuration de la localisation es-CO
   - Formatage des dates, nombres et devises (COP)

6. **Configuration CI/CD et déploiement** (2 jours)
   - Configuration de l'environnement de développement
   - Configuration de l'environnement de staging
   - Scripts de déploiement de base

**Livrables Phase 0 :**
- Application Django fonctionnelle avec authentification
- Base de données configurée avec modèles de base
- Interface utilisateur de base en espagnol colombien
- Système de rôles opérationnel

**Jalon Phase 0 :** Application de base accessible avec authentification fonctionnelle

---

#### Phase 1 : Fonctionnalités de base (8-10 semaines)

**Objectif :** Développer toutes les fonctionnalités opérationnelles de base permettant la gestion quotidienne.

##### Sprint 1.1 : Gestion des Agences et Utilisateurs (1 semaine)

**Tâches :**
1. **CRUD Agences** (2 jours)
   - Création, lecture, mise à jour des agences
   - Interface d'administration des agences
   - Validation et règles métier

2. **Gestion des utilisateurs et rôles** (3 jours)
   - CRUD utilisateurs avec attribution de rôles
   - Association Regional Manager ↔ Agence
   - Interface d'administration des utilisateurs
   - Gestion des comptes Modèle (optionnel)

**Livrables Sprint 1.1 :** Gestion complète des agences et utilisateurs opérationnelle

---

##### Sprint 1.2 : Gestion des Modèles (2 semaines)

**Tâches :**
1. **Modèle de données Modèle** (2 jours)
   - Modèle Modèle avec statut actif/inactif
   - Relation Modèle ↔ Agence
   - Relation Modèle ↔ Utilisateur (optionnel)

2. **CRUD Modèles** (3 jours)
   - Ajout de modèles par Regional Manager
   - Modification des informations des modèles
   - Désactivation des modèles (soft delete)
   - Filtrage des modèles actifs/inactifs
   - Interface de gestion des modèles

3. **Fiche du modèle** (2 jours)
   - Affichage des informations du modèle
   - Liste des gains (à venir dans sprint suivant)
   - Liste des heures travaillées (à venir dans sprint suivant)
   - Historique et filtres

4. **Règles métier et permissions** (1 jour)
   - Validation des permissions par rôle
   - Isolation par agence
   - Tests unitaires

**Livrables Sprint 1.2 :** Gestion complète des modèles avec CRUD et fiche détaillée

---

##### Sprint 1.3 : Gestion des Gains des Modèles (1,5 semaines)

**Tâches :**
1. **Modèle de données Gains** (1 jour)
   - Modèle GainModèle
   - Relation GainModèle ↔ Modèle ↔ Date
   - Validation des données

2. **Saisie quotidienne des gains** (3 jours)
   - Interface de saisie par modèle
   - Validation et enregistrement
   - Gestion des erreurs

3. **Historique et consultation** (2 jours)
   - Affichage dans la fiche du modèle
   - Filtres par date
   - Consultation par le modèle (si compte utilisateur)

4. **Masquage des modèles désactivés** (1 jour)
   - Filtrage automatique dans les interfaces opérationnelles
   - Conservation dans les rapports financiers

**Livrables Sprint 1.3 :** Système de gestion des gains opérationnel

---

##### Sprint 1.4 : Gestion des Heures Travaillées (1,5 semaines)

**Tâches :**
1. **Modèle de données Heures Travaillées** (1 jour)
   - Modèle HeuresTravaillées
   - Relation avec Modèle et Date
   - Validation

2. **Page de saisie groupée des heures** (4 jours)
   - Interface avec sélection de date (jour courant par défaut)
   - Affichage de tous les modèles actifs
   - Formulaire de saisie pour tous les modèles
   - Validation et enregistrement groupé
   - Gestion des erreurs

3. **Affichage dans la fiche du modèle** (2 jours)
   - Liste des heures travaillées avec dates
   - Filtrage et recherche
   - Consultation par le modèle (si compte utilisateur)

**Livrables Sprint 1.4 :** Système de gestion des heures travaillées opérationnel

---

##### Sprint 1.5 : Gestion des Dépenses (1 semaine)

**Tâches :**
1. **Modèle de données Dépenses** (1 jour)
   - Modèle Dépense
   - Catégorisation
   - Relation avec Agence

2. **CRUD Dépenses** (3 jours)
   - Création, modification, suppression
   - Catégorisation des dépenses
   - Filtres et recherche
   - Interface de gestion

3. **Consultation et rapports de base** (1 jour)
   - Liste des dépenses
   - Filtres par période, catégorie
   - Totaux et statistiques de base

**Livrables Sprint 1.5 :** Gestion complète des dépenses opérationnelle

---

##### Sprint 1.6 : Gestion des Salaires (1 semaine)

**Tâches :**
1. **Modèle de données Salaires** (1 jour)
   - Modèle Salaire
   - Relation avec Agence
   - Informations par employé

2. **CRUD Salaires** (3 jours)
   - Gestion des salaires par employé
   - Suivi des paiements
   - Calculs de totaux

3. **Consultation et rapports de base** (1 jour)
   - Liste des salaires
   - Totaux par agence
   - Statistiques de base

**Livrables Sprint 1.6 :** Gestion complète des salaires opérationnelle

---

##### Sprint 1.7 : Gestion des Revenus (1 semaine)

**Tâches :**
1. **Modèle de données Revenus** (1 jour)
   - Modèle Revenu
   - Catégorisation des sources
   - Relation avec Agence

2. **CRUD Revenus** (3 jours)
   - Création, modification, suppression
   - Catégorisation
   - Filtres et recherche

3. **Consultation et rapports de base** (1 jour)
   - Liste des revenus
   - Filtres par période, catégorie
   - Totaux et statistiques

**Livrables Sprint 1.7 :** Gestion complète des revenus opérationnelle

---

##### Sprint 1.8 : Tableaux de Bord de Base (1,5 semaines)

**Tâches :**
1. **Tableau de bord Regional Manager** (3 jours)
   - Vue consolidée de l'agence
   - Indicateurs clés (dépenses, revenus, salaires, gains modèles)
   - Graphiques de base
   - Filtres par période

2. **Tableau de bord General Manager** (3 jours)
   - Vue consolidée des 2 agences
   - Comparaisons entre agences
   - Indicateurs globaux
   - Graphiques comparatifs

3. **Tableau de bord Modèle** (1 jour)
   - Vue personnelle des gains et heures
   - Statistiques personnelles

**Livrables Sprint 1.8 :** Tableaux de bord de base opérationnels pour tous les rôles

---

##### Sprint 1.9 : Tests, Optimisation et Documentation (1 semaine)

**Tâches :**
1. **Tests d'intégration** (2 jours)
   - Tests end-to-end des parcours utilisateurs
   - Tests de permissions et sécurité
   - Tests de performance de base

2. **Optimisation et corrections** (2 jours)
   - Correction des bugs identifiés
   - Optimisation des requêtes
   - Amélioration de l'UX

3. **Documentation** (1 jour)
   - Documentation utilisateur de base
   - Guide d'administration
   - Documentation technique

**Livrables Sprint 1.9 :** Application Phase 1 testée, optimisée et documentée

**Jalon Phase 1 :** Application fonctionnelle avec toutes les fonctionnalités de base opérationnelles

---

#### Phase 2 : Rapports Consolidés (4-6 semaines)

**Objectif :** Développer les rapports consolidés avancés et les analyses pour les managers.

##### Sprint 2.1 : Rapports Consolidés Regional Manager (2 semaines)

**Tâches :**
1. **Rapports périodiques** (3 jours)
   - Rapports quotidiens, hebdomadaires, mensuels, trimestriels, annuels
   - Vue consolidée des données financières de l'agence
   - Export PDF/Excel

2. **Analyses comparatives temporelles** (3 jours)
   - Comparaisons période à période
   - Graphiques de tendances
   - Analyses de croissance

3. **Indicateurs de performance** (2 jours)
   - KPIs de l'agence
   - Tableaux de bord avancés
   - Alertes et seuils

4. **Synthèse des gains modèles** (2 jours)
   - Synthèse des gains actifs et historiques
   - Analyses par modèle
   - Statistiques de performance des modèles

5. **Bilan financier de l'agence** (2 jours)
   - Bilan complet
   - État des résultats
   - Analyse de trésorerie

**Livrables Sprint 2.1 :** Rapports consolidés complets pour Regional Manager

---

##### Sprint 2.2 : Rapports Consolidés General Manager (2 semaines)

**Tâches :**
1. **Vue consolidée globale** (3 jours)
   - Consolidation des données des 2 agences
   - Vue d'ensemble de l'entreprise
   - Indicateurs globaux

2. **Rapports comparatifs entre agences** (3 jours)
   - Comparaisons détaillées
   - Graphiques comparatifs
   - Analyses de performance relative

3. **Rapports périodiques globaux** (2 jours)
   - Rapports quotidiens, hebdomadaires, mensuels, trimestriels, annuels
   - Export PDF/Excel
   - Personnalisation des rapports

4. **Indicateurs de performance globale** (2 jours)
   - KPIs de l'entreprise
   - Tableaux de bord exécutifs
   - Alertes et seuils globaux

5. **Bilan financier consolidé** (2 jours)
   - Bilan consolidé de l'entreprise
   - État des résultats consolidé
   - Analyse de trésorerie globale

**Livrables Sprint 2.2 :** Rapports consolidés complets pour General Manager

---

##### Sprint 2.3 : Analyses Avancées et Projections (1 semaine)

**Tâches :**
1. **Analyses de tendances** (2 jours)
   - Détection de tendances
   - Prévisions basiques
   - Graphiques de tendances avancés

2. **Projections financières** (2 jours)
   - Projections basées sur l'historique
   - Scénarios de planification
   - Outils de simulation

3. **Export et partage** (1 jour)
   - Export avancé (PDF, Excel, CSV)
   - Partage de rapports
   - Planification d'envoi automatique

**Livrables Sprint 2.3 :** Analyses avancées et outils de projection opérationnels

---

##### Sprint 2.4 : Tests Finaux et Optimisation (1 semaine)

**Tâches :**
1. **Tests complets** (2 jours)
   - Tests de tous les rapports
   - Tests de performance avec volumes importants
   - Tests d'export

2. **Optimisation** (2 jours)
   - Optimisation des requêtes complexes
   - Mise en cache des rapports
   - Amélioration des performances

3. **Documentation finale** (1 jour)
   - Documentation utilisateur complète
   - Guide des rapports
   - Documentation technique finale

**Livrables Sprint 2.4 :** Application complète testée, optimisée et documentée

**Jalon Phase 2 :** Application complète avec tous les rapports consolidés opérationnels

---

### 9.3 Jalons principaux

| Jalon | Description | Date cible | Critères d'acceptation |
|-------|-------------|------------|------------------------|
| **M0** | Fin Phase 0 | Semaine 3 | Authentification fonctionnelle, base de données configurée, système de rôles opérationnel |
| **M1** | Fin Phase 1 | Semaine 11-13 | Toutes les fonctionnalités de base opérationnelles, tests passés, documentation de base |
| **M2** | Fin Phase 2 | Semaine 15-19 | Tous les rapports consolidés opérationnels, application complète et testée |

### 9.4 Estimation des ressources

#### Équipe recommandée :
- **1 Développeur Full-Stack Django** (lead)
- **1 Développeur Frontend** (si frontend séparé)
- **1 Designer UX/UI** (temps partiel, surtout Phase 1)
- **1 Testeur QA** (à partir de la fin Phase 1)

#### Estimation par phase :

**Phase 0 :** 2-3 semaines (1 développeur)
- Setup et infrastructure : 40-60 heures

**Phase 1 :** 8-10 semaines (1-2 développeurs)
- Développement fonctionnalités : 320-400 heures
- Tests et optimisation : 40-60 heures
- **Total :** 360-460 heures

**Phase 2 :** 4-6 semaines (1-2 développeurs)
- Développement rapports : 160-240 heures
- Tests et optimisation : 40-60 heures
- **Total :** 200-300 heures

**Total projet :** 600-820 heures (15-20 semaines-homme)

### 9.5 Dépendances et risques

#### Dépendances critiques :
- Choix définitif de la base de données (recommandé : PostgreSQL)
- Choix du frontend (Django templates ou framework séparé)
- Validation des besoins avec les utilisateurs finaux

#### Risques identifiés :
- **Complexité des rapports consolidés** : Peut nécessiter plus de temps que prévu
- **Performance avec volumes importants** : Nécessite optimisation continue
- **Localisation es-CO** : Vérification de tous les formats et traductions
- **Gestion des permissions** : Complexité de l'isolation par agence

### 9.6 Prochaines étapes

1. **Validation du plan** : Révision et ajustement avec l'équipe
2. **Affinement des estimations** : Ajustement basé sur l'expérience de l'équipe
3. **Définition des sprints détaillés** : Découpage en tâches plus granulaires
4. **Setup de l'environnement** : Démarrage de la Phase 0
5. **Itérations de documentation** : Mise à jour continue du document de spécifications

---

## 10. Risques et Mitigation

### 10.1 Risques identifiés
[À compléter]

### 10.2 Stratégies de mitigation
[À compléter]

---

## 11. Annexes

### 11.1 Glossaire
[Termes techniques et métier]

### 11.2 Références
[Documentation, standards, etc.]

---

**Note :** Ce document sera complété progressivement avec les informations fournies lors des prochaines étapes.
