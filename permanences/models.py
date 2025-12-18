from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta
from django.utils import timezone



class CreneauHoraire(models.Model):
    """Représente un créneau horaire d'une heure pour les permanences"""
    date = models.DateField(help_text="Date du créneau")
    heure_debut = models.TimeField(help_text="Heure de début du créneau")
    heure_fin = models.TimeField(help_text="Heure de fin du créneau")
    max_personnes = models.PositiveIntegerField(
        default=3, 
        help_text="Nombre maximum de personnes autorisées pour ce créneau"
    )
    actif = models.BooleanField(default=True, help_text="Créneau disponible pour inscription")
    
    class Meta:
        verbose_name = "Créneau horaire"
        verbose_name_plural = "Créneaux horaires"
        unique_together = ['date', 'heure_debut']
        ordering = ['date', 'heure_debut']
    
    def __str__(self):
        return f"{self.date} {self.heure_debut} - {self.heure_fin}"
    
    @property
    def places_disponibles(self):
        """Retourne le nombre de places disponibles"""
        try:
            inscriptions_count = self.inscriptions.filter(annulee=False).count()
            return max(0, self.max_personnes - inscriptions_count)
        except Exception:
            return self.max_personnes
    
    @property
    def complet(self):
        """Vérifie si le créneau est complet"""
        try:
            return self.places_disponibles <= 0
        except Exception:
            return False
    
    @property
    def est_passe(self):
        """
        True si le créneau est terminé.
        Évite la comparaison aware/naïve en travaillant sur date + time séparés.
        """
        now = timezone.localtime()  # toujours aware si USE_TZ
        if self.date < now.date():
            return True
        if self.date == now.date() and self.heure_fin <= now.time():
            return True
        return False
        
        
    @property
    def inscriptions_actives(self):
        return self.inscriptions.filter(annulee=False)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.heure_debut is not None and self.heure_fin is not None:
            if self.heure_debut >= self.heure_fin:
                raise ValidationError("L'heure de début doit être strictement inférieure à l'heure de fin.")
            # Autorise les plages > 1h pour l'admin, la découpe se fait dans save_model
            delta = (
                datetime.combine(self.date, self.heure_fin) -
                datetime.combine(self.date, self.heure_debut)
            )
            if delta < timedelta(hours=1):
                raise ValidationError("Un créneau doit durer au moins 1 heure.")

    def get_user_inscription(self, user):
        """Retourne l'inscription active (non annulée) de l'utilisateur pour ce créneau."""
        if user.is_authenticated:
            return self.inscriptions.filter(utilisateur=user, annulee=False).first()
        return None

class Inscription(models.Model):
    """Inscription d'un utilisateur à un créneau horaire"""
    utilisateur = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='inscriptions',
        help_text="Utilisateur inscrit"
    )
    creneau = models.ForeignKey(
        CreneauHoraire,
        on_delete=models.CASCADE,
        related_name='inscriptions',
        help_text="Créneau horaire"
    )
    date_inscription = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure d'inscription"
    )
    annulee = models.BooleanField(default=False, help_text="Inscription annulée")
    date_annulation = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date et heure d'annulation"
    )
    commentaire = models.TextField(
        blank=True,
        help_text="Commentaire optionnel"
    )
    
    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ['utilisateur', 'creneau']
        ordering = ['-date_inscription']
    
    def __str__(self):
        status = " (Annulée)" if self.annulee else ""
        return f"{self.utilisateur.username} - {self.creneau}{status}"
    
    def clean(self):
        """Validation de l'inscription"""
        if not self.creneau:
            return
            
        try:
            # Vérifier que le créneau n'est pas complet
            if not self.annulee:
                inscriptions_actives = self.creneau.inscriptions.filter(annulee=False)
                if self.pk:
                    # Exclure cette inscription si elle existe déjà
                    inscriptions_actives = inscriptions_actives.exclude(pk=self.pk)
                
                if inscriptions_actives.count() >= self.creneau.max_personnes:
                    raise ValidationError("Ce créneau est complet")
            
            # Vérifier que le créneau n'est pas passé
            if not self.annulee and self.creneau.est_passe:
                raise ValidationError("Impossible de s'inscrire à un créneau passé")
        except ValidationError:
            raise
        except Exception as e:
            # En cas d'erreur inattendue, on laisse passer mais on pourrait logger
            pass
    
    def annuler(self):
        """Annule l'inscription (timestamps aware)"""
        if not self.annulee:
            self.annulee = True
            self.date_annulation = timezone.now()
            self.save()
