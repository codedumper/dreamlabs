from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from .models import Role


def role_required(*required_roles):
    """
    Décorateur pour protéger une vue et exiger un ou plusieurs rôles spécifiques.
    Les superusers (admin) ont accès à tout.
    
    Usage:
        @role_required(Role.RoleType.GENERAL_MANAGER)
        def my_view(request):
            ...
        
        @role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, _('Debe iniciar sesión para acceder a esta página.'))
                return redirect('accounts:login')
            
            # Les superusers ont accès à tout
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not request.user.role:
                messages.error(request, _('No tiene un rol asignado. Contacte al administrador.'))
                return redirect('accounts:dashboard')
            
            # Vérifier si l'utilisateur a l'un des rôles requis
            user_role_name = request.user.role.name
            if user_role_name not in [role.value if hasattr(role, 'value') else role for role in required_roles]:
                messages.error(request, _('No tiene permisos para acceder a esta página.'))
                raise PermissionDenied(_('No tiene permisos para acceder a esta página.'))
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def general_manager_required(view_func):
    """Décorateur pour exiger le rôle General Manager"""
    return role_required(Role.RoleType.GENERAL_MANAGER)(view_func)


def regional_manager_required(view_func):
    """Décorateur pour exiger le rôle Regional Manager"""
    return role_required(Role.RoleType.REGIONAL_MANAGER)(view_func)


def modele_required(view_func):
    """Décorateur pour exiger le rôle Modèle"""
    return role_required(Role.RoleType.MODELE)(view_func)


def agency_required(view_func):
    """
    Décorateur pour s'assurer qu'un Regional Manager a une agence assignée.
    Les superusers (admin) ont accès à tout.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, _('Debe iniciar sesión para acceder a esta página.'))
            return redirect('accounts:login')
        
        # Les superusers ont accès à tout
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if request.user.is_regional_manager() and not request.user.agency:
            messages.error(request, _('No tiene una agencia asignada. Contacte al administrador.'))
            return redirect('accounts:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper
