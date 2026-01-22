from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class RoleRequiredMiddleware:
    """
    Middleware pour vérifier que l'utilisateur a le rôle requis pour accéder à certaines vues.
    Utilisé en complément des décorateurs de vues.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code exécuté avant la vue
        response = self.get_response(request)
        # Code exécuté après la vue
        return response


class AgencyIsolationMiddleware:
    """
    Middleware pour isoler les données par agence pour les Regional Managers.
    Ajoute l'agence de l'utilisateur au contexte de la requête.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ajouter l'agence de l'utilisateur au contexte si c'est un Regional Manager
        if request.user.is_authenticated and request.user.is_regional_manager():
            request.user_agency = request.user.agency
        else:
            request.user_agency = None
        
        response = self.get_response(request)
        return response
