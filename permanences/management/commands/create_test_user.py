from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crée un utilisateur de test pour déboguer la connexion'
    
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='testuser', help='Nom d\'utilisateur')
        parser.add_argument('--password', type=str, default='testpass123', help='Mot de passe')
        parser.add_argument('--email', type=str, default='test@example.com', help='Email')
        parser.add_argument('--reset', action='store_true', help='Supprimer l\'utilisateur s\'il existe')
    
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        # Supprimer l'utilisateur s'il existe et si --reset est spécifié
        if options['reset']:
            try:
                user = User.objects.get(username=username)
                user.delete()
                self.stdout.write(f'Utilisateur {username} supprimé.')
            except User.DoesNotExist:
                pass
        
        # Créer l'utilisateur
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name='Test',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Utilisateur créé avec succès !')
            )
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write(f'Email: {email}')
            
            # Tester l'authentification
            from django.contrib.auth import authenticate
            auth_user = authenticate(username=username, password=password)
            if auth_user:
                self.stdout.write(self.style.SUCCESS('✓ Test d\'authentification réussi'))
            else:
                self.stdout.write(self.style.ERROR('✗ Test d\'authentification échoué'))
                
        except Exception as e:
            if 'already exists' in str(e):
                self.stdout.write(
                    self.style.WARNING(f'L\'utilisateur {username} existe déjà.')
                )
                # Tester l'authentification de l'utilisateur existant
                from django.contrib.auth import authenticate
                auth_user = authenticate(username=username, password=password)
                if auth_user:
                    self.stdout.write(self.style.SUCCESS('✓ Test d\'authentification réussi'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Test d\'authentification échoué - mot de passe incorrect ?'))
            else:
                self.stdout.write(self.style.ERROR(f'Erreur: {e}'))
