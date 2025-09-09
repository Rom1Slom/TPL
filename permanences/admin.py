from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CreneauHoraire, Inscription
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from datetime import date, datetime, timedelta


class PlageCreneauxForm(forms.Form):
    date_debut = forms.DateField(label="Date de début")
    heure_debut = forms.TimeField(label="Heure de début")
    heure_fin = forms.TimeField(label="Heure de fin")
    repeter = forms.BooleanField(label="Répéter chaque semaine", required=False)
    date_fin = forms.DateField(label="Jusqu'au (si répétition)", required=False)
   

class CreneauHoraireForm(forms.ModelForm):
    repeter = forms.BooleanField(label="Répéter chaque semaine", required=False)
    date_fin = forms.DateField(label="Jusqu'au (si répétition)", required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = CreneauHoraire
        fields = "__all__"


@admin.register(CreneauHoraire)
class CreneauHoraireAdmin(admin.ModelAdmin):

    form = CreneauHoraireForm 

    list_display = ['date', 'heure_debut', 'heure_fin', 'max_personnes', 'actif', 'nb_inscriptions_actives', 'places_libres']
    list_filter = ['actif', 'date', 'max_personnes']
    list_editable = ['actif']
    search_fields = ['date']
    date_hierarchy = 'date'
    ordering = ['-date', 'heure_debut']
    # inlines = [InscriptionInline]
    
    

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('ajouter-plage/', self.admin_site.admin_view(self.ajouter_plage))
        ]
        return custom_urls + urls

    def ajouter_plage(self, request):
        if request.method == "POST":
            form = PlageCreneauxForm(request.POST)
            if form.is_valid():
                date_debut = form.cleaned_data['date_debut']
                heure_debut = form.cleaned_data['heure_debut']
                heure_fin = form.cleaned_data['heure_fin']
                repeter = form.cleaned_data['repeter']
                date_fin = form.cleaned_data['date_fin'] if form.cleaned_data['date_fin'] else date_debut

                current_date = date_debut
                while current_date <= date_fin:
                    h = heure_debut
                    while (datetime.combine(current_date, h) + timedelta(hours=1)).time() <= heure_fin:
                        fin = (datetime.combine(current_date, h) + timedelta(hours=1)).time()
                        CreneauHoraire.objects.create(
                            date=current_date,
                            heure_debut=h,
                            heure_fin=fin,
                            actif=True
                        )
                        h = fin
                    if repeter:
                        current_date += timedelta(days=7)
                    else:
                        break
                self.message_user(request, "Créneaux créés avec succès !")
                return redirect("..")
        else:
            form = PlageCreneauxForm()
        return render(request, "admin/permanences/ajouter_plage.html", {"form": form})
    
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
        
        repeter = form.cleaned_data.get('repeter')
        date_fin = form.cleaned_data.get('date_fin')
        debut = obj.heure_debut
        fin = obj.heure_fin
        date = obj.date

         # On va créer les créneaux sur toutes les semaines si demandé
        if repeter and date_fin and date:
            current_date = date
            while current_date <= date_fin:
                self._creer_creneaux_heure_par_heure(current_date, debut, fin, obj)
                current_date += timedelta(days=7)
            return  # On ne sauvegarde pas l'objet original
        else:
            # Cas normal : découpage automatique si besoin
            self._creer_creneaux_heure_par_heure(date, debut, fin, obj, save_original=True)
            return
        
    def _creer_creneaux_heure_par_heure(self, date, debut, fin, obj, save_original=False):
        delta = (datetime.combine(date, fin) - datetime.combine(date, debut))
        heures = int(delta.total_seconds() // 3600)
        if heures > 1:
            for i in range(heures):
                h_debut = (datetime.combine(date, debut) + timedelta(hours=i)).time()
                h_fin = (datetime.combine(date, debut) + timedelta(hours=i+1)).time()
                # Vérifie si le créneau existe déjà
                if not CreneauHoraire.objects.filter(date=date, heure_debut=h_debut).exists():
                    CreneauHoraire.objects.create(
                        date=date,
                        heure_debut=h_debut,
                        heure_fin=h_fin,
                        max_personnes=obj.max_personnes,
                        actif=obj.actif
                    )
        else:
            if save_original:
                # Vérifie si le créneau existe déjà
                if not CreneauHoraire.objects.filter(date=date, heure_debut=debut).exists():
                    super(CreneauHoraireAdmin, self).save_model(None, obj, None, False)





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
