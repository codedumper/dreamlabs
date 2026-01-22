# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agencies", "0006_bonusrule_target_currency_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="bonusrule",
            name="order",
            field=models.IntegerField(
                default=0,
                help_text="Orden de aplicación de la regla (menor número = se aplica primero). Las reglas se aplican en orden creciente y se aplica la primera regla que corresponde.",
                verbose_name="Orden",
            ),
        ),
        migrations.AddField(
            model_name="bonusrule",
            name="stop_on_match",
            field=models.BooleanField(
                default=False,
                help_text="Si está activado, se detiene la evaluación de reglas después de aplicar esta regla",
                verbose_name="Detenerse en esta regla si se aplica",
            ),
        ),
    ]
