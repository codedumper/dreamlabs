from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """Modèle pour les rôles utilisateurs"""
    
    class RoleType(models.TextChoices):
        GENERAL_MANAGER = 'GENERAL_MANAGER', _('General Manager')
        REGIONAL_MANAGER = 'REGIONAL_MANAGER', _('Regional Manager')
        MODELE = 'MODELE', _('Modèle')
    
    name = models.CharField(
        max_length=50,
        choices=RoleType.choices,
        unique=True,
        verbose_name=_('Nombre del rol')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    
    class Meta:
        verbose_name = _('Rol')
        verbose_name_plural = _('Roles')
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """Modèle utilisateur étendu avec rôle et agence"""
    
    # Override des related_name pour éviter les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    role = models.ForeignKey(
        'Role',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('Rol')
    )
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('Agencia')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Teléfono')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    
    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display() if self.role else 'Sin rol'})"
    
    def get_role_display(self):
        """Retourne le nom d'affichage du rôle"""
        if self.role:
            return self.role.get_name_display()
        return None
    
    def is_general_manager(self):
        """Vérifie si l'utilisateur est General Manager"""
        if not self.role:
            return False
        return self.role.name == Role.RoleType.GENERAL_MANAGER
    
    def is_regional_manager(self):
        """Vérifie si l'utilisateur est Regional Manager"""
        if not self.role:
            return False
        return self.role.name == Role.RoleType.REGIONAL_MANAGER
    
    def is_modele(self):
        """Vérifie si l'utilisateur est Modèle"""
        if not self.role:
            return False
        return self.role.name == Role.RoleType.MODELE
    
    # Propriétés pour les templates Django (les méthodes sans () ne fonctionnent pas toujours)
    @property
    def is_general_manager_prop(self):
        """Propriété pour les templates"""
        return self.is_general_manager()
    
    @property
    def is_regional_manager_prop(self):
        """Propriété pour les templates"""
        return self.is_regional_manager()
    
    @property
    def is_modele_prop(self):
        """Propriété pour les templates"""
        return self.is_modele()
