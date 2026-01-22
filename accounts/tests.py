from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from agencies.models import Agency
from .models import Role

User = get_user_model()


class RoleModelTest(TestCase):
    """Tests pour le modèle Role"""
    
    def setUp(self):
        """Créer les rôles de base"""
        self.general_manager_role = Role.objects.create(
            name=Role.RoleType.GENERAL_MANAGER,
            description="General Manager"
        )
        self.regional_manager_role = Role.objects.create(
            name=Role.RoleType.REGIONAL_MANAGER,
            description="Regional Manager"
        )
        self.modele_role = Role.objects.create(
            name=Role.RoleType.MODELE,
            description="Modèle"
        )
    
    def test_role_creation(self):
        """Test de création des rôles"""
        self.assertEqual(self.general_manager_role.name, Role.RoleType.GENERAL_MANAGER)
        self.assertEqual(self.regional_manager_role.name, Role.RoleType.REGIONAL_MANAGER)
        self.assertEqual(self.modele_role.name, Role.RoleType.MODELE)
    
    def test_role_str(self):
        """Test de la représentation string des rôles"""
        self.assertEqual(str(self.general_manager_role), "General Manager")
        self.assertEqual(str(self.regional_manager_role), "Regional Manager")
        self.assertEqual(str(self.modele_role), "Modèle")


class UserModelTest(TestCase):
    """Tests pour le modèle User"""
    
    def setUp(self):
        """Créer les rôles et une agence"""
        self.general_manager_role = Role.objects.create(
            name=Role.RoleType.GENERAL_MANAGER
        )
        self.regional_manager_role = Role.objects.create(
            name=Role.RoleType.REGIONAL_MANAGER
        )
        self.agency = Agency.objects.create(
            name="Agencia Test",
            code="AGT001"
        )
    
    def test_user_creation(self):
        """Test de création d'un utilisateur"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("testpass123"))
    
    def test_user_with_role(self):
        """Test d'un utilisateur avec un rôle"""
        user = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="testpass123",
            role=self.general_manager_role
        )
        self.assertEqual(user.role, self.general_manager_role)
        self.assertTrue(user.is_general_manager())
        self.assertFalse(user.is_regional_manager())
    
    def test_user_with_agency(self):
        """Test d'un utilisateur avec une agence"""
        user = User.objects.create_user(
            username="regional",
            email="regional@example.com",
            password="testpass123",
            role=self.regional_manager_role,
            agency=self.agency
        )
        self.assertEqual(user.agency, self.agency)
        self.assertTrue(user.is_regional_manager())


class AuthenticationTest(TestCase):
    """Tests d'authentification"""
    
    def setUp(self):
        """Créer un utilisateur de test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    def test_login(self):
        """Test de connexion"""
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'testuser', 'password': 'testpass123'}
        )
        self.assertEqual(response.status_code, 302)  # Redirection après login
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_login_invalid_credentials(self):
        """Test de connexion avec des identifiants invalides"""
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'testuser', 'password': 'wrongpassword'}
        )
        self.assertEqual(response.status_code, 200)  # Reste sur la page de login
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout(self):
        """Test de déconnexion"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)  # Redirection après logout
        self.assertFalse(self.client.session.get('_auth_user_id'))


class PermissionTest(TestCase):
    """Tests des permissions et décorateurs"""
    
    def setUp(self):
        """Créer des utilisateurs avec différents rôles"""
        self.client = Client()
        
        # Créer les rôles
        self.gm_role = Role.objects.create(name=Role.RoleType.GENERAL_MANAGER)
        self.rm_role = Role.objects.create(name=Role.RoleType.REGIONAL_MANAGER)
        self.modele_role = Role.objects.create(name=Role.RoleType.MODELE)
        
        # Créer une agence
        self.agency = Agency.objects.create(name="Agencia Test", code="AGT001")
        
        # Créer les utilisateurs
        self.gm_user = User.objects.create_user(
            username="general_manager",
            password="test123",
            role=self.gm_role
        )
        self.rm_user = User.objects.create_user(
            username="regional_manager",
            password="test123",
            role=self.rm_role,
            agency=self.agency
        )
        self.modele_user = User.objects.create_user(
            username="modele",
            password="test123",
            role=self.modele_role
        )
    
    def test_general_manager_permissions(self):
        """Test des permissions du General Manager"""
        self.assertTrue(self.gm_user.is_general_manager())
        self.assertFalse(self.gm_user.is_regional_manager())
        self.assertFalse(self.gm_user.is_modele())
    
    def test_regional_manager_permissions(self):
        """Test des permissions du Regional Manager"""
        self.assertFalse(self.rm_user.is_general_manager())
        self.assertTrue(self.rm_user.is_regional_manager())
        self.assertFalse(self.rm_user.is_modele())
        self.assertEqual(self.rm_user.agency, self.agency)
