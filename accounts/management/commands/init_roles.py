from django.core.management.base import BaseCommand
from accounts.models import Role


class Command(BaseCommand):
    help = 'Initialise les rôles de base dans la base de données'

    def handle(self, *args, **options):
        roles_data = [
            {
                'name': Role.RoleType.GENERAL_MANAGER,
                'description': 'Manager général avec accès à toutes les agences en lecture seule'
            },
            {
                'name': Role.RoleType.REGIONAL_MANAGER,
                'description': 'Manager régional avec accès complet à son agence'
            },
            {
                'name': Role.RoleType.MODELE,
                'description': 'Modèle avec accès en lecture seule à ses propres données'
            },
        ]
        
        created_count = 0
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Rôle créé: {role.get_name_display()}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Rôle existant: {role.get_name_display()}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{created_count} nouveau(x) rôle(s) créé(s) sur {len(roles_data)}'
            )
        )
