# Generated manually

from django.db import migrations


def populate_fecha_ingreso(apps, schema_editor):
    """Remplir fecha_ingreso avec created_at pour les modèles existants"""
    Model = apps.get_model('models_app', 'Model')
    for model in Model.objects.filter(fecha_ingreso__isnull=True):
        if model.created_at:
            model.fecha_ingreso = model.created_at.date()
            model.save()


def reverse_populate_fecha_ingreso(apps, schema_editor):
    """Ne rien faire en reverse"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('models_app', '0014_model_fecha_ingreso_model_fecha_retiro'),
    ]

    operations = [
        migrations.RunPython(populate_fecha_ingreso, reverse_populate_fecha_ingreso),
    ]
