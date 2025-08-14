# Instructions Copilot

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

Ce projet est une application Django pour la gestion des inscriptions aux permanences d'un stand de marché.

## Architecture du projet

- **inscription/** : Configuration principale du projet Django
- **permanences/** : Application principale gérant les créneaux et inscriptions
- **accounts/** : Application pour l'authentification des utilisateurs
- **templates/** : Templates HTML avec Bootstrap pour l'interface

## Modèles principaux

1. **HoraireOuverture** : Définit les horaires d'ouverture par jour de la semaine
2. **CreneauHoraire** : Représente un créneau d'une heure avec un nombre maximum de personnes (3)
3. **Inscription** : Lie un utilisateur à un créneau avec possibilité d'annulation

## Fonctionnalités

- Système d'authentification complet (connexion, inscription, profil)
- Calendrier interactif pour visualiser et s'inscrire aux créneaux
- Interface d'administration Django pour gérer les horaires et créneaux
- Limitation automatique du nombre d'inscriptions par créneau
- Gestion des annulations d'inscription
- Interface responsive avec Bootstrap 5

## Bonnes pratiques à suivre

- Utiliser les messages Django pour les notifications utilisateur
- Valider les données dans les modèles avec `clean()`
- Utiliser les décorateurs `@login_required` pour protéger les vues
- Respecter le format français pour les dates et heures
- Utiliser les propriétés des modèles pour les calculs dynamiques
