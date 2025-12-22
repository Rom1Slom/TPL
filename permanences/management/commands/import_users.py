import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Importe des utilisateurs depuis users_extraits.xlsx"

    def handle(self, *args, **options):
        User = get_user_model()
        # Charge le fichier Excel
        df = pd.read_excel('users_extraits.xlsx')
        for _, row in df.iterrows():
            username = str(row['ID']).strip()
            password = str(row['Password']).strip()
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password=password)
                self.stdout.write(self.style.SUCCESS(f"Utilisateur {username} créé"))
            else:
                self.stdout.write(self.style.WARNING(f"{username} existe déjà"))
