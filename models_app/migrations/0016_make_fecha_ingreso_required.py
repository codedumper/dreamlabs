# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models_app', '0015_populate_fecha_ingreso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='fecha_ingreso',
            field=models.DateField(
                help_text='Fecha en que el modelo ingresó a la agencia',
                verbose_name='Fecha de Ingreso'
            ),
        ),
    ]
