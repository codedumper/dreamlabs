from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ExpenseCategory, Expense, Employee, Salary, RevenueSource, Revenue


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['agency', 'date', 'amount', 'category', 'created_by', 'created_at']
    list_filter = ['date', 'category', 'agency', 'created_at']
    search_fields = ['description', 'agency__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('agency', 'date', 'amount', 'category', 'description')
        }),
        (_('Información del sistema'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_regional_manager() and request.user.agency:
            return qs.filter(agency=request.user.agency)
        return qs
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'agency', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'agency', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_regional_manager() and request.user.agency:
            return qs.filter(agency=request.user.agency)
        return qs


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'agency', 'payment_date', 'amount', 'created_by', 'created_at']
    list_filter = ['payment_date', 'agency', 'created_at']
    search_fields = ['employee__first_name', 'employee__last_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('employee', 'agency', 'payment_date', 'period_start', 'period_end', 'amount', 'description')
        }),
        (_('Información del sistema'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_regional_manager() and request.user.agency:
            return qs.filter(agency=request.user.agency)
        return qs
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(RevenueSource)
class RevenueSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['agency', 'date', 'amount', 'source', 'created_by', 'created_at']
    list_filter = ['date', 'source', 'agency', 'created_at']
    search_fields = ['description', 'agency__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('agency', 'date', 'amount', 'source', 'description')
        }),
        (_('Información del sistema'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_regional_manager() and request.user.agency:
            return qs.filter(agency=request.user.agency)
        return qs
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
