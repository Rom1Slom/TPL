from django.core.management.base import BaseCommand
from permanences.models import CreneauHoraire, Inscription
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test les modèles pour identifier les erreurs'
    
    def handle(self, *args, **options):
        self.stdout.write('Test des modèles...')
        
        try:
            # Test 1: Récupérer tous les créneaux
            creneaux = CreneauHoraire.objects.all()
            self.stdout.write(f'Nombre de créneaux: {creneaux.count()}')
            
            # Test 2: Tester les propriétés sur chaque créneau
            for creneau in creneaux[:5]:  # Tester les 5 premiers
                self.stdout.write(f'Créneau: {creneau}')
                try:
                    self.stdout.write(f'  - Places disponibles: {creneau.places_disponibles}')
                except Exception as e:
                    self.stdout.write(f'  - ERREUR places_disponibles: {e}')
                    
                try:
                    self.stdout.write(f'  - Complet: {creneau.complet}')
                except Exception as e:
                    self.stdout.write(f'  - ERREUR complet: {e}')
                    
                try:
                    self.stdout.write(f'  - Est passé: {creneau.est_passe}')
                except Exception as e:
                    self.stdout.write(f'  - ERREUR est_passe: {e}')
                    
                try:
                    inscriptions = creneau.inscriptions.all()
                    self.stdout.write(f'  - Inscriptions: {inscriptions.count()}')
                except Exception as e:
                    self.stdout.write(f'  - ERREUR inscriptions: {e}')
                    
        except Exception as e:
            self.stdout.write(f'ERREUR GENERALE: {e}')
            
        self.stdout.write('Test terminé')
