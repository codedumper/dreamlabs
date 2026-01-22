from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Agency, BonusRule


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone', 'email', 'model_gain_percentage', 'bank_fee_percentage', 'late_penalty', 'absence_penalty', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('name', 'code', 'is_active')
        }),
        (_('Información de contacto'), {
            'fields': ('address', 'phone', 'email')
        }),
        (_('Parámetros financieros'), {
            'fields': ('model_gain_percentage', 'bank_fee_percentage'),
            'description': _('Porcentajes aplicados a las ganancias y transacciones')
        }),
        (_('Parámetros de multas'), {
            'fields': ('late_penalty', 'absence_penalty'),
            'description': _('Montos en COP (Peso colombiano)')
        }),
        (_('Fechas'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BonusRule)
class BonusRuleAdmin(admin.ModelAdmin):
    list_display = ['agency', 'name', 'period_type', 'target_amount', 'bonus_type', 'bonus_value', 'is_active', 'created_at']
    list_filter = ['is_active', 'period_type', 'bonus_type', 'agency', 'created_at']
    search_fields = ['name', 'agency__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('agency', 'name', 'is_active')
        }),
        (_('Configuración de la Regla'), {
            'fields': ('period_type', 'target_amount', 'bonus_type', 'bonus_value'),
            'description': _('Define el período, el objetivo y el tipo de bonus')
        }),
        (_('Fechas'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
