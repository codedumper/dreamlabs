from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class Agency(models.Model):
    """Modèle pour les agences"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nombre')
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_('Código')
    )
    address = models.TextField(
        blank=True,
        verbose_name=_('Dirección')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Teléfono')
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_('Correo electrónico')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activa')
    )
    # Paramètres d'amendes
    late_penalty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Multa por Retraso (COP)'),
        help_text=_('Monto de la multa aplicada cuando un modelo llega tarde')
    )
    absence_penalty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Multa por Ausencia (COP)'),
        help_text=_('Monto de la multa aplicada cuando un modelo no se presenta')
    )
    # Paramètres financiers
    model_gain_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_('Porcentaje de Ganancia de Modelos (%)'),
        help_text=_('Porcentaje que reciben los modelos de sus ganancias')
    )
    bank_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_('Porcentaje de Impuestos (%)'),
        help_text=_('Porcentaje de impuestos aplicados a las transacciones')
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
        verbose_name = _('Agencia')
        verbose_name_plural = _('Agencias')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BonusRule(models.Model):
    """Règles de bonus pour les agences"""
    
    class PeriodType(models.TextChoices):
        DAILY = 'DAILY', _('Diario')
        WEEKLY = 'WEEKLY', _('Semanal')
        BIWEEKLY = 'BIWEEKLY', _('Quincenal (2 veces al mes)')
        MONTHLY = 'MONTHLY', _('Mensual')
    
    class BonusType(models.TextChoices):
        PERCENTAGE = 'PERCENTAGE', _('Porcentaje de Ganancia Total')
        FIXED_AMOUNT = 'FIXED_AMOUNT', _('Monto Fijo')
    
    class TargetCurrency(models.TextChoices):
        COP = 'COP', _('COP (Pesos Colombianos)')
        USD = 'USD', _('USD (Dólares)')
    
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='bonus_rules',
        verbose_name=_('Agencia')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Nombre de la Regla'),
        help_text=_('Descripción de la regla de bonus')
    )
    period_type = models.CharField(
        max_length=20,
        choices=PeriodType.choices,
        verbose_name=_('Tipo de Período')
    )
    target_currency = models.CharField(
        max_length=3,
        choices=TargetCurrency.choices,
        default=TargetCurrency.COP,
        verbose_name=_('Moneda del Objetivo'),
        help_text=_('Moneda en la que se define el objetivo (COP o USD)')
    )
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Objetivo'),
        help_text=_('Objetivo de ganancia journalier moyen para activar el bonus. Se calcula sumando todas las ganancias de los días trabajados en la período y dividiendo por el número de días trabajados según el horario.')
    )
    bonus_type = models.CharField(
        max_length=20,
        choices=BonusType.choices,
        verbose_name=_('Tipo de Bonus')
    )
    bonus_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Valor del Bonus'),
        help_text=_('Porcentaje (%) o monto fijo (COP) según el tipo seleccionado')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activa')
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_('Orden'),
        help_text=_('Orden de aplicación de la regla (menor número = se aplica primero)')
    )
    stop_on_match = models.BooleanField(
        default=False,
        verbose_name=_('Detener en esta regla'),
        help_text=_('Si esta regla se aplica, no se evaluarán las reglas siguientes')
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
        verbose_name = _('Regla de Bonus')
        verbose_name_plural = _('Reglas de Bonus')
        ordering = ['agency', 'order', 'period_type', '-created_at']
    
    def __str__(self):
        return f"{self.agency.name} - {self.name} ({self.get_period_type_display()})"
    
    def get_bonus_display(self, total_gain):
        """Calcule et retourne le bonus pour une ganancia total donnée"""
        if total_gain < self.target_amount:
            return 0
        
        if self.bonus_type == self.BonusType.PERCENTAGE:
            return total_gain * self.bonus_value / 100
        else:  # FIXED_AMOUNT
            return self.bonus_value
