from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # path('signup/', views.inscription_utilisateur, name='signup'),  # Désactivé - seuls les admins créent des comptes
    path('profil/', views.profil_utilisateur, name='profil'),
    path('login/', views.CustomLoginView.as_view(), name='custom_login'),
    path('debug/', views.debug_session, name='debug'),
]
