from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Model, ModelGain, WorkedHours, Schedule, ScheduleAssignment, WorkSession, Pause


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'agency', 'status', 'email', 'phone', 'created_at']
    list_filter = ['status', 'agency', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Información personal'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'agency', 'status')
        }),
        (_('Información del sistema'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_regional_manager() and request.user.agency:
            return qs.filter(agency=request.user.agency)
        return qs


@admin.register(ModelGain)
class ModelGainAdmin(admin.ModelAdmin):
    list_display = ['model', 'date', 'amount', 'created_at']
    list_filter = ['date', 'created_at', 'model__agency']
    search_fields = ['model__first_name', 'model__last_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('model', 'date', 'amount', 'notes')
        }),
        (_('Información del sistema'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_regional_manager() and request.user.agency:
            return qs.filter(model__agency=request.user.agency)
        return qs


@admin.register(WorkedHours)
class WorkedHoursAdmin(admin.ModelAdmin):
    list_display = ['model', 'date', 'hours', 'created_at']
    list_filter = ['date', 'created_at', 'model__agency']
    search_fields = ['model__first_name', 'model__last_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('model', 'date', 'hours', 'notes')
        }),
        (_('Información del sistema'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_regional_manager() and request.user.agency:
            return qs.filter(model__agency=request.user.agency)
        return qs


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'agency', 'start_time', 'end_time', 'week_days', 'is_active', 'created_at']
    list_filter = ['is_active', 'agency', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('agency', 'name', 'start_time', 'end_time', 'week_days', 'meal_break_duration', 'is_active')
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


@admin.register(ScheduleAssignment)
class ScheduleAssignmentAdmin(admin.ModelAdmin):
    list_display = ['model', 'schedule', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'schedule__agency']
    search_fields = ['model__first_name', 'model__last_name', 'schedule__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('model', 'schedule', 'is_active')
        }),
        (_('Información del sistema'), {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_regional_manager() and request.user.agency:
            return qs.filter(schedule__agency=request.user.agency)
        return qs
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ['model', 'date', 'status', 'total_worked_hours', 'session_gain_amount_usd', 'session_gain_amount', 'late_penalty_amount', 'absence_penalty_amount', 'created_at']
    list_filter = ['status', 'date', 'created_at', 'model__agency']
    search_fields = ['model__first_name', 'model__last_name']
    readonly_fields = ['created_at', 'updated_at', 'total_worked_hours']
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('model', 'schedule_assignment', 'date', 'status')
        }),
        (_('Horarios reales'), {
            'fields': ('actual_arrival_time', 'late_minutes', 'end_time')
        }),
        (_('Cálculos'), {
            'fields': ('total_worked_hours',)
        }),
        (_('Multas'), {
            'fields': ('late_penalty_amount', 'absence_penalty_amount')
        }),
        (_('Ganancias'), {
            'fields': ('session_gain_amount_usd', 'session_gain_amount', 'trm_rate', 'session_bank_fees', 'session_model_ganancia')
        }),
        (_('Información del sistema'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_regional_manager() and request.user.agency:
            return qs.filter(model__agency=request.user.agency)
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtre les ForeignKey pour éviter les références invalides"""
        if db_field.name == "schedule_assignment":
            # Filtrer les assignations valides
            if request.user.is_regional_manager() and request.user.agency:
                kwargs["queryset"] = ScheduleAssignment.objects.filter(
                    schedule__agency=request.user.agency
                )
            else:
                kwargs["queryset"] = ScheduleAssignment.objects.all()
        elif db_field.name == "model":
            # Filtrer les modèles valides
            if request.user.is_regional_manager() and request.user.agency:
                kwargs["queryset"] = Model.objects.filter(agency=request.user.agency)
            else:
                kwargs["queryset"] = Model.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        
        # Valider que les ForeignKey existent avant de sauvegarder
        if obj.model_id:
            if not Model.objects.filter(id=obj.model_id).exists():
                from django.contrib import messages
                messages.error(request, _('El modelo seleccionado no existe. Por favor, seleccione otro modelo.'))
                return
        
        if obj.schedule_assignment_id:
            if not ScheduleAssignment.objects.filter(id=obj.schedule_assignment_id).exists():
                from django.contrib import messages
                messages.error(request, _('La asignación de horario seleccionada no existe. Por favor, seleccione otra asignación.'))
                return
        
        # Vérifier la contrainte unique_together (model, date)
        if obj.model_id and obj.date:
            existing = WorkSession.objects.filter(model_id=obj.model_id, date=obj.date)
            if change:
                existing = existing.exclude(id=obj.id)
            if existing.exists():
                from django.contrib import messages
                messages.error(request, _('Ya existe una sesión de trabajo para este modelo en esta fecha. La contrainte unique_together no permite duplicados.'))
                return
        
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            from django.contrib import messages
            from django.db import IntegrityError
            if isinstance(e, IntegrityError):
                messages.error(request, _('Error de integridad: Verifique que el modelo y la asignación de horario existen y que no hay duplicados.'))
            else:
                messages.error(request, _('Error al guardar: {}').format(str(e)))
            raise


@admin.register(Pause)
class PauseAdmin(admin.ModelAdmin):
    list_display = ['work_session', 'pause_type', 'start_time', 'end_time', 'duration', 'is_active']
    list_filter = ['pause_type', 'start_time', 'work_session__date']
    search_fields = ['work_session__model__first_name', 'work_session__model__last_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_time'
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('work_session', 'pause_type', 'start_time', 'end_time')
        }),
        (_('Información del sistema'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_regional_manager() and request.user.agency:
            return qs.filter(work_session__model__agency=request.user.agency)
        return qs
