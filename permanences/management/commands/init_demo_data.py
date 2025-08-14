from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from permanences.models import HoraireOuverture, CreneauHoraire, Inscription
from datetime import datetime, time, date, timedelta


class Command(BaseCommand):
    help = 'Initialise les données de démonstration pour l\'application des permanences'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initialisation des données de démonstration...'))

        # Créer des horaires d'ouverture de base
        self.create_horaires_ouverture()
        
        # Créer quelques utilisateurs de test
        self.create_test_users()
        
        # Créer des créneaux pour les 2 prochaines semaines
        self.create_test_creneaux()
        
        self.stdout.write(self.style.SUCCESS('Données de démonstration créées avec succès !'))

    def create_horaires_ouverture(self):
        """Créer les horaires d'ouverture par défaut"""
        horaires_defaults = [
            (1, time(9, 0), time(17, 0)),   # Mardi
            (2, time(9, 0), time(17, 0)),   # Mercredi  
            (4, time(9, 0), time(17, 0)),   # Vendredi
            (5, time(8, 0), time(18, 0)),   # Samedi
        ]
        
        for jour, ouverture, fermeture in horaires_defaults:
            horaire, created = HoraireOuverture.objects.get_or_create(
                jour_semaine=jour,
                defaults={
                    'heure_ouverture': ouverture,
                    'heure_fermeture': fermeture,
                    'actif': True
                }
            )
            if created:
                self.stdout.write(f'Horaire créé pour le jour {jour}')
            else:
                self.stdout.write(f'Horaire existe déjà pour le jour {jour}')

    def create_test_users(self):
        """Créer des utilisateurs de test"""
        users_data = [
            ('marie', 'Marie', 'Dupont', 'marie@example.com'),
            ('jean', 'Jean', 'Martin', 'jean@example.com'),
            ('sophie', 'Sophie', 'Bernard', 'sophie@example.com'),
            ('pierre', 'Pierre', 'Moreau', 'pierre@example.com'),
            ('claire', 'Claire', 'Leroy', 'claire@example.com'),
        ]
        
        for username, first_name, last_name, email in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'is_active': True
                }
            )
            if created:
                user.set_password('motdepasse123')
                user.save()
                self.stdout.write(f'Utilisateur créé: {username}')
            else:
                self.stdout.write(f'Utilisateur existe déjà: {username}')

    def create_test_creneaux(self):
        """Créer des créneaux de test pour les 2 prochaines semaines"""
        today = date.today()
        
        # Créer des créneaux pour les 14 prochains jours
        for i in range(14):
            current_date = today + timedelta(days=i)
            day_of_week = current_date.weekday()
            
            # Vérifier s'il y a des horaires pour ce jour
            try:
                horaire = HoraireOuverture.objects.get(jour_semaine=day_of_week, actif=True)
            except HoraireOuverture.DoesNotExist:
                continue
            
            # Créer des créneaux d'une heure
            current_time = horaire.heure_ouverture
            while current_time < horaire.heure_fermeture:
                # Calculer l'heure de fin (1 heure plus tard)
                end_time = datetime.combine(current_date, current_time)
                end_time += timedelta(hours=1)
                end_time = end_time.time()
                
                # Vérifier que l'heure de fin ne dépasse pas l'heure de fermeture
                if end_time <= horaire.heure_fermeture:
                    creneau, created = CreneauHoraire.objects.get_or_create(
                        date=current_date,
                        heure_debut=current_time,
                        defaults={
                            'heure_fin': end_time,
                            'max_personnes': 3,
                            'actif': True
                        }
                    )
                    if created:
                        self.stdout.write(f'Créneau créé: {current_date} {current_time}-{end_time}')
                
                # Passer à l'heure suivante
                current_time = end_time

        # Créer quelques inscriptions de test pour les créneaux futurs
        self.create_test_inscriptions()

    def create_test_inscriptions(self):
        """Créer quelques inscriptions de test"""
        users = User.objects.filter(is_superuser=False)[:3]
        creneaux = CreneauHoraire.objects.filter(
            date__gte=date.today(),
            actif=True
        )[:5]
        
        for i, creneau in enumerate(creneaux):
            if users.exists() and i < len(users):
                user = users[i]
                inscription, created = Inscription.objects.get_or_create(
                    utilisateur=user,
                    creneau=creneau,
                    defaults={
                        'commentaire': f'Inscription de test pour {user.first_name}'
                    }
                )
                if created:
                    self.stdout.write(f'Inscription créée: {user.username} -> {creneau}')
