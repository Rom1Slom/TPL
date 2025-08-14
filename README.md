# Système d'Inscription aux Permanences

Application Django pour gérer les inscriptions aux créneaux de permanence d'un stand de marché.

## Fonctionnalités

- 📅 **Calendrier interactif** : Visualisation des créneaux disponibles par semaine
- 👥 **Gestion des utilisateurs** : Inscription, connexion et profil utilisateur
- ⏰ **Créneaux d'une heure** : Maximum 3 personnes par créneau
- 🔧 **Interface d'administration** : Gestion des horaires et créneaux
- 📱 **Interface responsive** : Compatible mobile et desktop
- ✅ **Inscriptions/Annulations** : Système simple et intuitif

## Installation et configuration

1. **Cloner le projet** (si applicable) ou utiliser le code existant

2. **Installer les dépendances** :
   ```bash
   pip install django python-dotenv
   ```

3. **Appliquer les migrations** :
   ```bash
   python manage.py migrate
   ```

4. **Créer un superutilisateur** :
   ```bash
   python manage.py createsuperuser
   ```

5. **Initialiser les données de démonstration** (optionnel) :
   ```bash
   python manage.py init_demo_data
   ```

6. **Lancer le serveur de développement** :
   ```bash
   python manage.py runserver
   ```

7. **Accéder à l'application** :
   - Site principal : http://127.0.0.1:8000/
   - Administration : http://127.0.0.1:8000/admin/

## Comptes de test

Après avoir exécuté `init_demo_data`, vous disposez de :

**Super utilisateur** : Celui que vous avez créé avec `createsuperuser`

**Utilisateurs de test** (mot de passe : `motdepasse123`) :
- marie (Marie Dupont)
- jean (Jean Martin) 
- sophie (Sophie Bernard)
- pierre (Pierre Moreau)
- claire (Claire Leroy)

## Structure du projet

```
inscription/              # Configuration principale Django
├── settings.py          # Paramètres du projet
├── urls.py             # URLs principales
└── wsgi.py             # Configuration WSGI

permanences/             # Application des permanences
├── models.py           # Modèles (HoraireOuverture, CreneauHoraire, Inscription)
├── views.py            # Vues principales
├── admin.py            # Interface d'administration
└── urls.py             # URLs de l'application

accounts/                # Application d'authentification
├── views.py            # Vues d'authentification
└── urls.py             # URLs d'authentification

templates/               # Templates HTML
├── base.html           # Template de base
├── permanences/        # Templates des permanences
├── accounts/           # Templates des comptes
└── registration/       # Templates d'authentification
```

## Utilisation

### Pour les utilisateurs normaux

1. **Se connecter** : Utiliser ses identifiants (voir comptes de test ci-dessus)
2. **Consulter le calendrier** : Voir les créneaux disponibles et ses propres inscriptions
3. **Consulter ses inscriptions** : Via "Mes inscriptions" dans le menu
4. **Voir son profil** : Statistiques personnelles d'inscription

### Pour les super utilisateurs (administrateurs)

1. **Accéder à l'administration** : `/admin/` avec un compte super utilisateur
2. **Gérer les inscriptions** : Via le bouton "Gestion" dans le menu principal
3. **Inscrire des utilisateurs** : Dans la vue de gestion, sélectionner un utilisateur et un créneau
4. **Annuler des inscriptions** : Bouton d'annulation dans la vue de gestion
5. **Définir les horaires d'ouverture** : Via l'interface d'administration Django
6. **Créer des créneaux** : Ajouter des créneaux horaires selon les besoins

## Modèles de données

### HoraireOuverture
- Jour de la semaine (Lundi = 0, Dimanche = 6)
- Heure d'ouverture et de fermeture
- Statut actif/inactif

### CreneauHoraire
- Date et heures de début/fin (durée = 1 heure)
- Nombre maximum de personnes (par défaut : 3)
- Statut actif/inactif
- Propriétés calculées : places disponibles, complet, passé

### Inscription
- Utilisateur et créneau associés
- Date d'inscription
- Statut annulé avec date d'annulation
- Commentaire optionnel

## Technologies utilisées

- **Backend** : Django 5.2, Python 3.11
- **Frontend** : Bootstrap 5, Font Awesome
- **Base de données** : SQLite (par défaut)
- **Authentification** : Système Django intégré

## Fonctionnalités avancées

- Validation automatique des créneaux (durée d'une heure)
- Vérification du nombre maximum d'inscriptions
- Empêche les inscriptions sur des créneaux passés
- Interface d'administration enrichie avec filtres et statistiques
- Messages de feedback utilisateur
- Navigation par semaine dans le calendrier

## Licence

Projet développé pour la gestion des permanences de stand de marché.
