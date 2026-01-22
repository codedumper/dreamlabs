from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone

User = get_user_model()


class ExpenseCategory(models.Model):
    """Catégories de dépenses"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nombre')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    
    class Meta:
        verbose_name = _('Categoría de Gasto')
        verbose_name_plural = _('Categorías de Gastos')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Expense(models.Model):
    """Dépenses de l'entreprise"""
    
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.PROTECT,
        related_name='expenses',
        verbose_name=_('Agencia')
    )
    date = models.DateField(
        verbose_name=_('Fecha'),
        default=timezone.now
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Monto'),
        help_text=_('Monto en COP (Peso colombiano)')
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='expenses',
        verbose_name=_('Categoría')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción'),
        help_text=_('Descripción detallada del gasto')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='expenses_created',
        verbose_name=_('Creado por')
    )
    
    class Meta:
        verbose_name = _('Gasto')
        verbose_name_plural = _('Gastos')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['agency', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.agency.name} - {self.date} - ${self.amount:,.2f} COP - {self.category.name}"


class Employee(models.Model):
    """Employés de l'entreprise (pour les salaires)"""
    
    first_name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre')
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_('Apellido')
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Correo electrónico')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Teléfono')
    )
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.PROTECT,
        related_name='employees',
        verbose_name=_('Agencia')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activo')
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
        verbose_name = _('Empleado')
        verbose_name_plural = _('Empleados')
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['agency', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Retourne le nom complet"""
        return f"{self.first_name} {self.last_name}"


class Salary(models.Model):
    """Salaires des employés"""
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='salaries',
        verbose_name=_('Empleado')
    )
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.PROTECT,
        related_name='salaries',
        verbose_name=_('Agencia')
    )
    payment_date = models.DateField(
        verbose_name=_('Fecha de pago')
    )
    period_start = models.DateField(
        verbose_name=_('Inicio del período')
    )
    period_end = models.DateField(
        verbose_name=_('Fin del período')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Monto'),
        help_text=_('Monto en COP (Peso colombiano)')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción'),
        help_text=_('Notas adicionales sobre el pago')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='salaries_created',
        verbose_name=_('Creado por')
    )
    
    class Meta:
        verbose_name = _('Salario')
        verbose_name_plural = _('Salarios')
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['agency', 'payment_date']),
            models.Index(fields=['payment_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.payment_date} - ${self.amount:,.2f} COP"


class RevenueSource(models.Model):
    """Sources de revenus"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nombre')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    
    class Meta:
        verbose_name = _('Fuente de Ingreso')
        verbose_name_plural = _('Fuentes de Ingresos')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Revenue(models.Model):
    """Revenus de l'entreprise"""
    
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.PROTECT,
        related_name='revenues',
        verbose_name=_('Agencia')
    )
    date = models.DateField(
        verbose_name=_('Fecha'),
        default=timezone.now
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Monto'),
        help_text=_('Monto en COP (Peso colombiano)')
    )
    source = models.ForeignKey(
        RevenueSource,
        on_delete=models.PROTECT,
        related_name='revenues',
        verbose_name=_('Fuente')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción'),
        help_text=_('Descripción detallada del ingreso')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='revenues_created',
        verbose_name=_('Creado por')
    )
    
    class Meta:
        verbose_name = _('Ingreso')
        verbose_name_plural = _('Ingresos')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['agency', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.agency.name} - {self.date} - ${self.amount:,.2f} COP - {self.source.name}"
