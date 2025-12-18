from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import JsonResponse


def inscription_utilisateur(request):
    """Vue d'inscription pour les nouveaux utilisateurs"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username}! Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profil_utilisateur(request):
    """Vue du profil utilisateur"""
    user = request.user
    inscriptions_actives = user.inscriptions.filter(annulee=False).count()
    inscriptions_totales = user.inscriptions.count()
    
    context = {
        'user': user,
        'inscriptions_actives': inscriptions_actives,
        'inscriptions_totales': inscriptions_totales,
    }
    
    return render(request, 'accounts/profil.html', context)


class CustomLoginView(LoginView):
    """Vue de connexion personnalisée pour un meilleur débogage"""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True # évite de revoir le formulaire quand déjà connecté

    def get_success_url(self):
        return reverse_lazy('permanences:calendrier')
    
    def form_valid(self, form):
        """Appelé quand le formulaire est valide"""
        messages.success(self.request, f'Connexion réussie ! Bienvenue {form.get_user().username}.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Appelé quand le formulaire est invalide"""
        messages.error(self.request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        return super().form_invalid(form)


def connexion_utilisateur(request):
    """Vue de connexion personnalisée (alternative)"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Connexion réussie ! Bienvenue {username}.')
                next_url = request.GET.get('next') or '/permanences/'
                return redirect(next_url)
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Erreur dans le formulaire.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


def debug_session(request):
    """Vue de débogage pour vérifier les sessions"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        debug_info = {
            'username_provided': username,
            'password_provided': bool(password),
            'user_found': user is not None,
            'user_active': user.is_active if user else False,
            'session_key': request.session.session_key,
            'session_data': dict(request.session.items()),
            'is_authenticated_before': request.user.is_authenticated,
        }
        
        if user:
            login(request, user)
            debug_info['login_successful'] = True
            debug_info['is_authenticated_after'] = request.user.is_authenticated
            debug_info['logged_in_user'] = request.user.username
        else:
            debug_info['login_successful'] = False
            debug_info['error'] = 'Utilisateur non trouvé ou mot de passe incorrect'
        
        return JsonResponse(debug_info)
    
    return render(request, 'debug_login.html')
