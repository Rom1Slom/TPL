from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
from .models import CreneauHoraire, Inscription
from django.urls import reverse
from urllib.parse import urlencode


def is_superuser(user):
    """Vérifie si l'utilisateur est un super utilisateur"""
    return user.is_superuser


def calendrier_permanences(request):
    """Vue principale affichant le calendrier des permanences"""
    # Récupérer la semaine courante ou celle spécifiée
    today = timezone.now().date()
    week_start = request.GET.get('week')
    
    if week_start:
        try:
            week_start = datetime.strptime(week_start, '%Y-%m-%d').date()
        except ValueError:
            week_start = today - timedelta(days=today.weekday())
    else:
        week_start = today - timedelta(days=today.weekday())
    
    week_end = week_start + timedelta(days=6)
    
    # Récupérer les créneaux de la semaine
    creneaux = CreneauHoraire.objects.filter(
        date__range=[week_start, week_end],
        actif=True
    ).prefetch_related('inscriptions__utilisateur').order_by('date', 'heure_debut')

    for creneau in creneaux:
        creneau.user_inscription = creneau.get_user_inscription(request.user)
    
    # Organiser les créneaux par jour
    creneaux_par_jour = {}
    for creneau in creneaux:
        creneau.user_inscription = creneau.get_user_inscription(request.user)
        if creneau.date not in creneaux_par_jour:
            creneaux_par_jour[creneau.date] = []
        
        # Ajouter les informations d'inscription de l'utilisateur
        creneau.user_inscription = creneau.get_user_inscription(request.user)
        
        creneaux_par_jour[creneau.date].append(creneau)
    
    # Naviguation semaine précédente/suivante
    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)
    
    context = {
        'creneaux_par_jour': creneaux_par_jour,
        'week_start': week_start,
        'week_end': week_end,
        'prev_week': prev_week,
        'next_week': next_week,
        'today': today,
    }
    
    return render(request, 'permanences/calendrier.html', context)


@user_passes_test(is_superuser)
@require_POST
def inscrire_creneau(request, creneau_id):
    """Inscrit un utilisateur à un créneau (réservé aux super utilisateurs)"""
    creneau = get_object_or_404(CreneauHoraire, id=creneau_id, actif=True)
    
    # Récupérer l'utilisateur à inscrire depuis le formulaire
    from django.contrib.auth.models import User
    user_id = request.POST.get('utilisateur_id')
    if not user_id:
        messages.error(request, "Aucun utilisateur sélectionné.")
        return redirect('permanences:calendrier')
    
    try:
        utilisateur = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        return redirect('permanences:calendrier')
    
    # Vérifications
    if creneau.est_passe:
        messages.error(request, "Impossible d'inscrire à un créneau passé.")
        return redirect('permanences:calendrier')
    
    if creneau.complet:
        messages.error(request, "Ce créneau est complet.")
        return redirect('permanences:calendrier')
    
    # Vérifier si l'utilisateur n'est pas déjà inscrit
    inscription_existante = Inscription.objects.filter(
        utilisateur=utilisateur,
        creneau=creneau,
        annulee=False
    ).first()
    
    if inscription_existante:
        messages.warning(request, f"{utilisateur.username} est déjà inscrit à ce créneau.")
        return redirect('permanences:calendrier')
    
    # Créer l'inscription
    try:
        inscription = Inscription.objects.create(
            utilisateur=utilisateur,
            creneau=creneau,
            commentaire=request.POST.get('commentaire', '')
        )
        messages.success(request, f"Inscription de {utilisateur.username} confirmée pour le {creneau.date} de {creneau.heure_debut} à {creneau.heure_fin}.")
    except Exception as e:
        messages.error(request, f"Erreur lors de l'inscription : {str(e)}")
    
    return redirect('permanences:calendrier')


@user_passes_test(is_superuser)
@require_POST
def annuler_inscription(request, inscription_id):
    """Annule une inscription (réservé aux super utilisateurs)"""
    inscription = get_object_or_404(
        Inscription,
        id=inscription_id,
        annulee=False
    )
    
    if inscription.creneau.est_passe:
        messages.error(request, "Impossible d'annuler une inscription pour un créneau passé.")
        return redirect('permanences:calendrier')
    
    username = inscription.utilisateur.username
    inscription.annuler()
    messages.success(request, f"Inscription de {username} annulée pour le {inscription.creneau.date} de {inscription.creneau.heure_debut} à {inscription.creneau.heure_fin}.")
    
    return redirect('permanences:calendrier')


@login_required
def mes_inscriptions(request):
    inscriptions = Inscription.objects.filter(
        utilisateur=request.user,
        annulee=False
    ).select_related('creneau').order_by('creneau__date', 'creneau__heure_debut')

    inscriptions_a_venir = [i for i in inscriptions if not i.creneau.est_passe]

    return render(request, 'permanences/mes_inscriptions.html', {
        'inscriptions': inscriptions,
        'inscriptions_a_venir': inscriptions_a_venir,
    })


def ajax_places_disponibles(request, creneau_id):
    """Retourne le nombre de places disponibles pour un créneau (AJAX)"""
    creneau = get_object_or_404(CreneauHoraire, id=creneau_id)
    
    return JsonResponse({
        'places_disponibles': creneau.places_disponibles,
        'complet': creneau.complet,
        'est_passe': creneau.est_passe,
    })


@user_passes_test(is_superuser)
def gestion_inscriptions(request):
    """Vue de gestion des inscriptions pour les super utilisateurs"""
    # Récupérer la semaine courante ou celle spécifiée
    today = timezone.now().date()
    week_start = request.GET.get('week')
    
    if week_start:
        try:
            week_start = datetime.strptime(week_start, '%Y-%m-%d').date()
        except ValueError:
            week_start = today - timedelta(days=today.weekday())
    else:
        week_start = today - timedelta(days=today.weekday())
    
    week_end = week_start + timedelta(days=6)
    
    # Récupérer tous les utilisateurs actifs
    from django.contrib.auth.models import User
    utilisateurs = User.objects.filter(is_active=True).order_by('username')
    
    # Récupérer les créneaux de la semaine avec leurs inscriptions
    creneaux = CreneauHoraire.objects.filter(
        date__range=[week_start, week_end],
        actif=True
    ).prefetch_related('inscriptions__utilisateur').order_by('date', 'heure_debut')
    
    # Organiser les créneaux par jour et ajouter les utilisateurs disponibles
    creneaux_par_jour = {}
    for creneau in creneaux:
        if creneau.date not in creneaux_par_jour:
            creneaux_par_jour[creneau.date] = []
        
        # Récupérer les IDs des utilisateurs déjà inscrits (non annulés)
        utilisateurs_inscrits_ids = set(
            inscription.utilisateur.id 
            for inscription in creneau.inscriptions.filter(annulee=False)
        )
        
        # Filtrer les utilisateurs disponibles pour ce créneau
        creneau.utilisateurs_disponibles = [
            utilisateur for utilisateur in utilisateurs 
            if utilisateur.id not in utilisateurs_inscrits_ids
        ]
        
        creneaux_par_jour[creneau.date].append(creneau)
    
    # Naviguation semaine précédente/suivante
    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)
    
    context = {
        'creneaux_par_jour': creneaux_par_jour,
        'utilisateurs': utilisateurs,
        'week_start': week_start,
        'week_end': week_end,
        'prev_week': prev_week,
        'next_week': next_week,
        'today': today,
    }
    
    return render(request, 'permanences/gestion_inscriptions.html', context)


@login_required
@require_POST
def auto_inscription(request, creneau_id):
    creneau = get_object_or_404(CreneauHoraire, pk=creneau_id)
    inscription = Inscription.objects.filter(
        utilisateur=request.user,
        creneau=creneau
    ).first()
    if inscription:
        if inscription.annulee:
            inscription.annulee = False
            inscription.date_annulation = None
            inscription.save()
            messages.success(request, "Votre inscription a été réactivée.")
        else:
            messages.info(request, "Vous êtes déjà inscrit à ce créneau.")
    else:
        Inscription.objects.create(utilisateur=request.user, creneau=creneau)
        messages.success(request, "Vous êtes inscrit à ce créneau.")
    # Redirection avec la semaine courante
    week = request.GET.get('week')
    url = reverse('permanences:calendrier')
    if week:
        url += f'?week={week}'
    return redirect(url)



@login_required
@require_POST
def auto_desinscription(request, inscription_id):
    inscription = get_object_or_404(
        Inscription,
        id=inscription_id,
        utilisateur=request.user,
        annulee=False
    )
    if inscription.creneau.est_passe:
        messages.error(request, "Impossible d'annuler une inscription pour un créneau passé.")
        return redirect('permanences:calendrier')
    inscription.annulee = True
    inscription.date_annulation = timezone.now()
    inscription.save()
    messages.success(request, "Votre inscription a bien été annulée.")
    next_page = request.GET.get('next')
    if next_page == "mes_inscriptions":
        return redirect('permanences:mes_inscriptions')
    week = request.GET.get('week')
    url = reverse('permanences:calendrier')
    if week:
        url += f'?week={week}'
    return redirect(url)

