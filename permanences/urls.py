from django.urls import path
from . import views

app_name = 'permanences'

urlpatterns = [
    path('', views.calendrier_permanences, name='calendrier'),
    path('gestion/', views.gestion_inscriptions, name='gestion'),
    path('inscrire/<int:creneau_id>/', views.inscrire_creneau, name='inscrire'),
    path('annuler/<int:inscription_id>/', views.annuler_inscription, name='annuler'),
    path('auto-inscription/<int:creneau_id>/', views.auto_inscription, name='auto_inscription'),
    path('auto-desinscription/<int:inscription_id>/', views.auto_desinscription, name='auto_desinscription'),
    path('mes-inscriptions/', views.mes_inscriptions, name='mes_inscriptions'),
    path('ajax/places/<int:creneau_id>/', views.ajax_places_disponibles, name='ajax_places'),
]
