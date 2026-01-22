#!/usr/bin/env python
"""Script pour créer un superutilisateur"""
import os
import sys
import django

# Utiliser les settings de production si spécifié, sinon les settings par défaut
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'dreamslabs_manager.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
django.setup()

from accounts.models import User, Role

username = 'admin'
email = 'admin@dreamslabs.com'
password = 'admin'

# Vérifier si l'utilisateur existe déjà
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    
    # Assigner le rôle GENERAL_MANAGER (rôle admin)
    try:
        admin_role = Role.objects.get(name=Role.RoleType.GENERAL_MANAGER)
        user.role = admin_role
    except Role.DoesNotExist:
        print("⚠️  Le rôle GENERAL_MANAGER n'existe pas. Exécutez 'python manage.py init_roles' d'abord.")
    
    user.save()
    print(f"✓ Mot de passe mis à jour pour l'utilisateur '{username}'")
    if user.role:
        print(f"✓ Rôle assigné: {user.role.get_name_display()}")
else:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    # Assigner le rôle GENERAL_MANAGER (rôle admin)
    try:
        admin_role = Role.objects.get(name=Role.RoleType.GENERAL_MANAGER)
        user.role = admin_role
        user.save()
        print(f"✓ Rôle assigné: {admin_role.get_name_display()}")
    except Role.DoesNotExist:
        print("⚠️  Le rôle GENERAL_MANAGER n'existe pas. Exécutez 'python manage.py init_roles' d'abord.")
    
    print(f"✓ Superutilisateur '{username}' créé avec succès")
    print(f"  Email: {email}")
    print(f"  Mot de passe: {password}")
