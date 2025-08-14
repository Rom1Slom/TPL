from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import HoraireOuverture, CreneauHoraire, Inscription


@admin.register(HoraireOuverture)
class HoraireOuvertureAdmin(admin.ModelAdmin):
    list_display = ['jour_semaine_display', 'heure_ouverture', 'heure_fermeture', 'actif']
    list_filter = ['actif', 'jour_semaine']
    list_editable = ['actif']
    ordering = ['jour_semaine']
    
    def jour_semaine_display(self, obj):
        """Affiche le nom du jour en français"""
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        try:
            return jours[obj.jour_semaine]
        except (IndexError, TypeError):
            return f"Jour {obj.jour_semaine}"
    jour_semaine_display.short_description = 'Jour'


class InscriptionInline(admin.TabularInline):
    model = Inscription
    extra = 0
    readonly_fields = ['date_inscription']
    fields = ['utilisateur', 'annulee', 'date_inscription', 'commentaire']
    
    def has_add_permission(self, request, obj=None):
        """Empêche l'ajout d'inscriptions via l'inline si le créneau est complet"""
        if obj and hasattr(obj, 'places_disponibles'):
            try:
                return obj.places_disponibles > 0
            except:
                pass
        return True


@admin.register(CreneauHoraire)
class CreneauHoraireAdmin(admin.ModelAdmin):
    list_display = ['date', 'heure_debut', 'heure_fin', 'max_personnes', 'actif', 'nb_inscriptions_actives', 'places_libres']
    list_filter = ['actif', 'date', 'max_personnes']
    list_editable = ['actif']
    search_fields = ['date']
    date_hierarchy = 'date'
    ordering = ['-date', 'heure_debut']
    inlines = [InscriptionInline]
    
    def get_queryset(self, request):
        """Optimise les requêtes en préchargeant les inscriptions"""
        return super().get_queryset(request).prefetch_related('inscriptions')
    
    def nb_inscriptions_actives(self, obj):
        """Compte le nombre d'inscriptions actives (non annulées)"""
        try:
            return obj.inscriptions.filter(annulee=False).count()
        except Exception as e:
            return f"Erreur: {e}"
    nb_inscriptions_actives.short_description = 'Inscriptions actives'
    
    def places_libres(self, obj):
        """Calcule le nombre de places libres"""
        try:
            inscriptions_actives = obj.inscriptions.filter(annulee=False).count()
            places_libres = obj.max_personnes - inscriptions_actives
            if places_libres <= 0:
                return format_html('<span style="color: red; font-weight: bold;">Complet</span>')
            elif places_libres == 1:
                return format_html('<span style="color: orange; font-weight: bold;">1 place</span>')
            else:
                return format_html('<span style="color: green;">{} places</span>', places_libres)
        except Exception as e:
            return f"Erreur: {e}"
    places_libres.short_description = 'Places disponibles'
    
    def save_model(self, request, obj, form, change):
        """Validation supplémentaire avant sauvegarde"""
        try:
            obj.full_clean()
        except Exception as e:
            self.message_user(request, f"Erreur de validation: {e}", level='ERROR')
            return
        super().save_model(request, obj, form, change)


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ['utilisateur_nom', 'creneau_info', 'date_inscription', 'statut_inscription']
    list_filter = ['annulee', 'creneau__date', 'date_inscription']
    search_fields = ['utilisateur__username', 'utilisateur__first_name', 'utilisateur__last_name']
    readonly_fields = ['date_inscription', 'date_annulation']
    date_hierarchy = 'date_inscription'
    ordering = ['-date_inscription']
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related('utilisateur', 'creneau')
    
    def utilisateur_nom(self, obj):
        """Affiche le nom complet de l'utilisateur"""
        try:
            if obj.utilisateur.first_name and obj.utilisateur.last_name:
                return f"{obj.utilisateur.first_name} {obj.utilisateur.last_name}"
            return obj.utilisateur.username
        except:
            return "Utilisateur inconnu"
    utilisateur_nom.short_description = 'Utilisateur'
    
    def creneau_info(self, obj):
        """Affiche les informations du créneau"""
        try:
            return f"{obj.creneau.date} de {obj.creneau.heure_debut} à {obj.creneau.heure_fin}"
        except:
            return "Créneau inconnu"
    creneau_info.short_description = 'Créneau'
    
    def statut_inscription(self, obj):
        """Affiche le statut de l'inscription avec couleur"""
        try:
            if obj.annulee:
                annulation_info = f" le {obj.date_annulation.strftime('%d/%m/%Y à %H:%M')}" if obj.date_annulation else ""
                return format_html('<span style="color: red;">Annulée{}</span>', annulation_info)
            else:
                return format_html('<span style="color: green;">Active</span>')
        except:
            return "Statut inconnu"
    statut_inscription.short_description = 'Statut'
    
    fieldsets = (
        ('Inscription', {
            'fields': ('utilisateur', 'creneau', 'commentaire')
        }),
        ('Statut', {
            'fields': ('annulee', 'date_inscription', 'date_annulation')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Protège les champs selon le contexte"""
        readonly = list(self.readonly_fields)
        if obj:
            try:
                from datetime import datetime
                maintenant = datetime.now()
                creneau_datetime = datetime.combine(obj.creneau.date, obj.creneau.heure_debut)
                if creneau_datetime < maintenant:
                    readonly.extend(['utilisateur', 'creneau'])
            except:
                pass
        return readonly
    
    def save_model(self, request, obj, form, change):
        """Validation et gestion de l'annulation"""
        try:
            if obj.annulee and not obj.date_annulation:
                from datetime import datetime
                obj.date_annulation = datetime.now()
            elif not obj.annulee:
                obj.date_annulation = None
            
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except Exception as e:
            self.message_user(request, f"Erreur lors de la sauvegarde: {e}", level='ERROR')
