from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Liste tous les utilisateurs pour déboguer les problèmes de connexion'
    
    def handle(self, *args, **options):
        self.stdout.write('=== LISTE DES UTILISATEURS ===')
        
        users = User.objects.all()
        if not users:
            self.stdout.write(self.style.WARNING('Aucun utilisateur trouvé !'))
            return
        
        for user in users:
            status = []
            if user.is_superuser:
                status.append('SUPERUSER')
            if user.is_staff:
                status.append('STAFF')
            if user.is_active:
                status.append('ACTIF')
            else:
                status.append('INACTIF')
            
            self.stdout.write(
                f'ID: {user.id} | Username: {user.username} | '
                f'Email: {user.email} | Nom: {user.first_name} {user.last_name} | '
                f'Statut: {", ".join(status)} | '
                f'Dernière connexion: {user.last_login}'
            )
        
        self.stdout.write(f'\nTotal: {users.count()} utilisateurs')
        
        # Vérifier la configuration Django
        self.stdout.write('\n=== CONFIGURATION AUTH ===')
        from django.conf import settings
        self.stdout.write(f'LOGIN_URL: {settings.LOGIN_URL}')
        self.stdout.write(f'LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}')
        self.stdout.write(f'LOGOUT_REDIRECT_URL: {settings.LOGOUT_REDIRECT_URL}')
        
        # Tester un utilisateur
        if users.exists():
            test_user = users.first()
            self.stdout.write(f'\n=== TEST UTILISATEUR: {test_user.username} ===')
            self.stdout.write(f'Mot de passe chiffré: {test_user.password[:50]}...')
            self.stdout.write(f'Peut se connecter: {test_user.is_active}')
