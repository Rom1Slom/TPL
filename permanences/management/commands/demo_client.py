from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from permanences.models import HoraireOuverture, CreneauHoraire, Inscription
from datetime import datetime, time, date, timedelta

class Command(BaseCommand):
    help = 'Crée des données de démonstration complètes pour la présentation client'
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 Création des données de démonstration...')
        
        # 1. Créer les horaires d'ouverture
        self.stdout.write('📅 Configuration des horaires...')
        horaires = [
            (0, time(8, 0), time(18, 0)),   # Lundi
            (1, time(8, 0), time(18, 0)),   # Mardi  
            (2, time(8, 0), time(18, 0)),   # Mercredi
            (3, time(8, 0), time(18, 0)),   # Jeudi
            (4, time(8, 0), time(18, 0)),   # Vendredi
            (5, time(7, 0), time(19, 0)),   # Samedi
            (6, time(8, 0), time(17, 0)),   # Dimanche
        ]
        
        for jour, ouverture, fermeture in horaires:
            HoraireOuverture.objects.update_or_create(
                jour_semaine=jour,
                defaults={
                    'heure_ouverture': ouverture,
                    'heure_fermeture': fermeture,
                    'actif': True
                }
            )
        
        # 2. Créer des utilisateurs de test
        self.stdout.write('👥 Création des utilisateurs...')
        utilisateurs = [
            ('marie.dupont', 'Marie', 'Dupont', 'marie@example.com'),
            ('jean.martin', 'Jean', 'Martin', 'jean@example.com'),
            ('sophie.bernard', 'Sophie', 'Bernard', 'sophie@example.com'),
            ('pierre.moreau', 'Pierre', 'Moreau', 'pierre@example.com'),
            ('claire.rousseau', 'Claire', 'Rousseau', 'claire@example.com'),
            ('lucas.petit', 'Lucas', 'Petit', 'lucas@example.com'),
        ]
        
        users = []
        for username, prenom, nom, email in utilisateurs:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': prenom,
                    'last_name': nom,
                    'email': email,
                    'is_active': True
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
            users.append(user)
        
        # 3. Créer des créneaux pour les 2 prochaines semaines
        self.stdout.write('⏰ Génération des créneaux...')
        today = date.today()
        
        for i in range(14):  # 2 semaines
            current_date = today + timedelta(days=i)
            jour_semaine = current_date.weekday()
            
            try:
                horaire = HoraireOuverture.objects.get(jour_semaine=jour_semaine, actif=True)
                
                # Créer des créneaux d'1 heure
                heure_courante = horaire.heure_ouverture
                while heure_courante < horaire.heure_fermeture:
                    heure_fin = datetime.combine(date.today(), heure_courante)
                    heure_fin = (heure_fin + timedelta(hours=1)).time()
                    
                    if heure_fin <= horaire.heure_fermeture:
                        creneau, created = CreneauHoraire.objects.get_or_create(
                            date=current_date,
                            heure_debut=heure_courante,
                            defaults={
                                'heure_fin': heure_fin,
                                'max_personnes': 3,
                                'actif': True
                            }
                        )
                    
                    # Passer à l'heure suivante
                    heure_courante = heure_fin
            except HoraireOuverture.DoesNotExist:
                pass
        
        # 4. Créer des inscriptions réalistes
        self.stdout.write('📝 Génération des inscriptions...')
        import random
        
        creneaux = CreneauHoraire.objects.filter(date__gte=today)
        for creneau in creneaux:
            # 60% de chance d'avoir au moins une inscription
            if random.random() < 0.6:
                nb_inscriptions = random.randint(1, min(3, len(users)))
                utilisateurs_sample = random.sample(users, nb_inscriptions)
                
                for user in utilisateurs_sample:
                    # Éviter les doublons
                    if not Inscription.objects.filter(
                        utilisateur=user, 
                        creneau=creneau, 
                        annulee=False
                    ).exists():
                        Inscription.objects.create(
                            utilisateur=user,
                            creneau=creneau,
                            commentaire=random.choice([
                                '', 
                                'Première permanence', 
                                'Disponible toute la journée',
                                'Expérience en vente'
                            ])
                        )
        
        # 5. Statistiques
        self.stdout.write('\n📊 RÉSUMÉ :')
        self.stdout.write(f'✅ Utilisateurs créés : {User.objects.filter(is_superuser=False).count()}')
        self.stdout.write(f'✅ Créneaux générés : {CreneauHoraire.objects.count()}')
        self.stdout.write(f'✅ Inscriptions actives : {Inscription.objects.filter(annulee=False).count()}')
        
        # 6. Informations de connexion
        self.stdout.write('\n🔐 COMPTES DE TEST :')
        self.stdout.write('Administrateur : admin / [votre mot de passe]')
        for username, prenom, nom, _ in utilisateurs:
            self.stdout.write(f'Utilisateur : {username} / demo123 ({prenom} {nom})')
        
        self.stdout.write('\n🎯 Données de démonstration prêtes !')
        self.stdout.write('💡 Conseil : Testez avec différents comptes pour montrer les fonctionnalités')
