from django.core.management.base import BaseCommand
from financial.models import ExpenseCategory, RevenueSource


class Command(BaseCommand):
    help = 'Inicializa las categorías de gastos y fuentes de ingresos predeterminadas'

    def handle(self, *args, **options):
        # Catégories de dépenses par défaut
        expense_categories = [
            {
                'name': 'Alquiler',
                'description': 'Gastos de alquiler de oficinas o espacios'
            },
            {
                'name': 'Servicios Públicos',
                'description': 'Agua, luz, gas, internet, teléfono'
            },
            {
                'name': 'Marketing y Publicidad',
                'description': 'Campañas publicitarias, redes sociales, promociones'
            },
            {
                'name': 'Equipamiento',
                'description': 'Compra de equipos, muebles, tecnología'
            },
            {
                'name': 'Transporte',
                'description': 'Gastos de transporte, combustible, taxis'
            },
            {
                'name': 'Alimentación',
                'description': 'Gastos de comida y bebidas'
            },
            {
                'name': 'Mantenimiento',
                'description': 'Reparaciones y mantenimiento de equipos o instalaciones'
            },
            {
                'name': 'Seguros',
                'description': 'Pólizas de seguro'
            },
            {
                'name': 'Otros',
                'description': 'Otros gastos no categorizados'
            },
        ]

        # Sources de revenus par défaut
        revenue_sources = [
            {
                'name': 'Servicios de Modelos',
                'description': 'Ingresos por servicios prestados por los modelos'
            },
            {
                'name': 'Eventos',
                'description': 'Ingresos por participación en eventos'
            },
            {
                'name': 'Contratos',
                'description': 'Ingresos por contratos a largo plazo'
            },
            {
                'name': 'Publicidad',
                'description': 'Ingresos por publicidad y patrocinios'
            },
            {
                'name': 'Otros',
                'description': 'Otros ingresos no categorizados'
            },
        ]

        # Créer les catégories de dépenses
        created_categories = 0
        for cat_data in expense_categories:
            category, created = ExpenseCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                created_categories += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Categoría de gasto creada: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Categoría ya existe: {category.name}')
                )

        # Créer les sources de revenus
        created_sources = 0
        for source_data in revenue_sources:
            source, created = RevenueSource.objects.get_or_create(
                name=source_data['name'],
                defaults={'description': source_data['description']}
            )
            if created:
                created_sources += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Fuente de ingreso creada: {source.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Fuente ya existe: {source.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Proceso completado: {created_categories} categorías y {created_sources} fuentes creadas.'
            )
        )
