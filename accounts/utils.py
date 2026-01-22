from django.core.exceptions import PermissionDenied
from .models import Role


def check_role_permission(user, required_role):
    """
    Vérifie si un utilisateur a le rôle requis.
    
    Args:
        user: Instance de User
        required_role: Role.RoleType (ex: Role.RoleType.GENERAL_MANAGER)
    
    Returns:
        bool: True si l'utilisateur a le rôle requis, False sinon
    
    Raises:
        PermissionDenied: Si l'utilisateur n'est pas authentifié ou n'a pas de rôle
    """
    if not user.is_authenticated:
        raise PermissionDenied("Usuario no autenticado")
    
    if not user.role:
        raise PermissionDenied("Usuario sin rol asignado")
    
    return user.role.name == required_role.value if hasattr(required_role, 'value') else user.role.name == required_role


def check_agency_access(user, agency):
    """
    Vérifie si un utilisateur peut accéder aux données d'une agence.
    
    - General Manager : accès à toutes les agences
    - Regional Manager : accès uniquement à son agence
    - Modèle : accès uniquement à son agence
    
    Args:
        user: Instance de User
        agency: Instance de Agency
    
    Returns:
        bool: True si l'utilisateur peut accéder à l'agence
    
    Raises:
        PermissionDenied: Si l'utilisateur n'a pas accès
    """
    if not user.is_authenticated:
        raise PermissionDenied("Usuario no autenticado")
    
    # General Manager a accès à tout
    if user.is_general_manager():
        return True
    
    # Regional Manager et Modèle : uniquement leur agence
    if user.agency and user.agency == agency:
        return True
    
    raise PermissionDenied("No tiene acceso a esta agencia")


def filter_by_agency_queryset(user, queryset, agency_field='agency'):
    """
    Filtre un queryset selon l'agence de l'utilisateur.
    
    - General Manager : pas de filtre (voit tout)
    - Regional Manager : filtre par son agence
    - Modèle : filtre par son agence
    
    Args:
        user: Instance de User
        queryset: QuerySet à filtrer
        agency_field: Nom du champ de relation avec Agency
    
    Returns:
        QuerySet filtré
    """
    if not user.is_authenticated:
        return queryset.none()
    
    # General Manager voit tout
    if user.is_general_manager():
        return queryset
    
    # Regional Manager et Modèle : uniquement leur agence
    if user.agency:
        filter_kwargs = {agency_field: user.agency}
        return queryset.filter(**filter_kwargs)
    
    # Pas d'agence assignée = pas d'accès
    return queryset.none()
