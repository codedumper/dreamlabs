from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import Q

User = get_user_model()


class ActiveModelManager(models.Manager):
    """Manager personnalisé pour filtrer les modèles actifs selon les dates"""
    
    def get_queryset(self):
        """Retourne uniquement les modèles actifs selon les dates"""
        today = timezone.now().date()
        return super().get_queryset().filter(
            status='ACTIVE',  # Utiliser la valeur directement pour éviter la référence circulaire
            fecha_ingreso__lt=today,  # Date actuelle > fecha_ingreso
        ).filter(
            Q(fecha_retiro__isnull=True) | Q(fecha_retiro__gte=today)  # fecha_retiro est None OU date actuelle <= fecha_retiro
        )


class Model(models.Model):
    """Modèle pour les modèles (personnes) associés à une agence"""
    
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Activo')
        INACTIVE = 'INACTIVE', _('Inactivo')
    
    # Informations de base
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
    
    # Informations supplémentaires
    password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Contraseña'),
        help_text=_('Visible uniquement pour les managers')
    )
    edad = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_('Edad')
    )
    
    class Platform(models.TextChoices):
        FLIRTIFY = 'FLIRTIFY', _('Flirtify')
    
    platform = models.CharField(
        max_length=20,
        choices=Platform.choices,
        default=Platform.FLIRTIFY,
        verbose_name=_('Plataforma')
    )
    
    cedula = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Cédula'),
        help_text=_('Número de identificación')
    )
    
    # Contacto de seguridad
    security_contact_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Nombre del Contacto de Seguridad')
    )
    security_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Teléfono del Contacto de Seguridad')
    )
    
    class EPS(models.TextChoices):
        NUEVA_EPS = 'NUEVA_EPS', _('Nueva EPS')
        SANITAS = 'SANITAS', _('Sanitas')
        PONAL = 'PONAL', _('Ponal')
        FAMISANAR = 'FAMISANAR', _('Famisanar')
        SALUD_TOTAL = 'SALUD_TOTAL', _('Salud Total')
    
    eps = models.CharField(
        max_length=20,
        choices=EPS.choices,
        blank=True,
        null=True,
        verbose_name=_('EPS')
    )
    
    # Relation avec l'agence
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.PROTECT,
        related_name='models',
        verbose_name=_('Agencia')
    )
    
    # Modèle référent (qui a référencé ce modèle)
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_models',
        verbose_name=_('Referido por'),
        help_text=_('Modelo que refirió a este modelo')
    )
    
    # Statut
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_('Estado')
    )
    
    # Compte utilisateur optionnel
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='model_profile',
        verbose_name=_('Usuario')
    )
    
    # Dates
    fecha_ingreso = models.DateField(
        verbose_name=_('Fecha de Ingreso'),
        help_text=_('Fecha en que el modelo ingresó a la agencia')
    )
    fecha_retiro = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Retiro'),
        help_text=_('Fecha en que el modelo se retiró de la agencia')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    deactivated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de desactivación')
    )
    
    # Managers
    objects = models.Manager()  # Manager par défaut
    active_by_dates = ActiveModelManager()  # Manager pour les modèles actifs selon les dates
    
    class Meta:
        verbose_name = _('Modelo')
        verbose_name_plural = _('Modelos')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agency', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['fecha_ingreso', 'fecha_retiro']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Retourne le nom complet"""
        return f"{self.first_name} {self.last_name}"
    
    def is_active(self):
        """Vérifie si le modèle est actif (statut uniquement)"""
        return self.status == self.Status.ACTIVE
    
    def is_active_by_dates(self):
        """
        Vérifie si le modèle est actif selon les dates d'entrée et de sortie.
        Un modèle est actif si :
        - La date actuelle est > fecha_ingreso
        - ET (fecha_retiro est None OU date actuelle <= fecha_retiro)
        - ET status == ACTIVE
        """
        if self.status != self.Status.ACTIVE:
            return False
        
        today = timezone.now().date()
        
        # Vérifier que la date actuelle est > fecha_ingreso
        if today <= self.fecha_ingreso:
            return False
        
        # Vérifier que fecha_retiro est None OU date actuelle <= fecha_retiro
        if self.fecha_retiro is not None and today > self.fecha_retiro:
            return False
        
        return True
    
    def deactivate(self):
        """Désactive le modèle"""
        if self.status != self.Status.INACTIVE:
            self.status = self.Status.INACTIVE
            self.deactivated_at = timezone.now()
            # Définir automatiquement la fecha de retiro à la date du jour
            if not self.fecha_retiro:
                self.fecha_retiro = timezone.now().date()
            self.save(update_fields=['status', 'deactivated_at', 'fecha_retiro', 'updated_at'])
    
    def reactivate(self):
        """Réactive le modèle"""
        if self.status != self.Status.ACTIVE:
            self.status = self.Status.ACTIVE
            self.deactivated_at = None
            self.save(update_fields=['status', 'deactivated_at', 'updated_at'])


class ModelGain(models.Model):
    """Gains quotidiens d'un modèle"""
    
    model = models.ForeignKey(
        Model,
        on_delete=models.CASCADE,
        related_name='gains',
        verbose_name=_('Modelo')
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
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción'),
        help_text=_('Descripción opcional del trabajo realizado')
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
        related_name='gains_created',
        verbose_name=_('Creado por')
    )
    
    class Meta:
        verbose_name = _('Ganancia de Modelo')
        verbose_name_plural = _('Ganancias de Modelos')
        ordering = ['-date', '-created_at']
        unique_together = [['model', 'date']]
        indexes = [
            models.Index(fields=['model', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.model.full_name} - {self.date} - ${self.amount:,.2f} COP"


class WorkedHours(models.Model):
    """Heures travaillées quotidiennes d'un modèle"""
    
    model = models.ForeignKey(
        Model,
        on_delete=models.CASCADE,
        related_name='worked_hours',
        verbose_name=_('Modelo')
    )
    date = models.DateField(
        verbose_name=_('Fecha'),
        default=timezone.now
    )
    hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Horas'),
        help_text=_('Número de horas trabajadas (puede incluir decimales, ej: 7.5)')
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
        related_name='worked_hours_created',
        verbose_name=_('Creado por')
    )
    
    class Meta:
        verbose_name = _('Horas Trabajadas')
        verbose_name_plural = _('Horas Trabajadas')
        ordering = ['-date', '-created_at']
        unique_together = [['model', 'date']]
        indexes = [
            models.Index(fields=['model', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.model.full_name} - {self.date} - {self.hours}h"


class Schedule(models.Model):
    """Horaire de travail défini par une agence"""
    
    class WeekDay(models.TextChoices):
        MONDAY = 'MONDAY', _('Lunes')
        TUESDAY = 'TUESDAY', _('Martes')
        WEDNESDAY = 'WEDNESDAY', _('Miércoles')
        THURSDAY = 'THURSDAY', _('Jueves')
        FRIDAY = 'FRIDAY', _('Viernes')
        SATURDAY = 'SATURDAY', _('Sábado')
        SUNDAY = 'SUNDAY', _('Domingo')
    
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('Agencia')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre del Horario'),
        help_text=_('Ej: Matutino, Vespertino, Nocturno')
    )
    start_time = models.TimeField(
        verbose_name=_('Hora de Inicio')
    )
    end_time = models.TimeField(
        verbose_name=_('Hora de Fin')
    )
    week_days = models.CharField(
        max_length=100,
        verbose_name=_('Días de la Semana'),
        help_text=_('Días de la semana separados por comas (ej: Lunes,Martes,Miércoles)'),
        blank=True
    )
    meal_break_duration = models.DurationField(
        null=True,
        blank=True,
        verbose_name=_('Duración del Descanso para Comida'),
        help_text=_('Duración prevista del descanso para comida (ej: 01:00:00 para 1 hora). El inicio y fin se registran mediante botones.')
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
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedules_created',
        verbose_name=_('Creado por')
    )
    
    class Meta:
        verbose_name = _('Horario')
        verbose_name_plural = _('Horarios')
        ordering = ['agency', 'start_time']
        indexes = [
            models.Index(fields=['agency', 'is_active']),
        ]
    
    def __str__(self):
        days_str = self.get_week_days_display() if self.week_days else ""
        if days_str:
            return f"{self.agency.name} - {self.name} ({self.start_time} - {self.end_time}) - {days_str}"
        return f"{self.agency.name} - {self.name} ({self.start_time} - {self.end_time})"
    
    def get_week_days_display(self):
        """Retourne la liste des jours de la semaine formatée"""
        if not self.week_days:
            return ""
        days = self.week_days.split(',')
        day_names = {
            'MONDAY': _('Lunes'),
            'TUESDAY': _('Martes'),
            'WEDNESDAY': _('Miércoles'),
            'THURSDAY': _('Jueves'),
            'FRIDAY': _('Viernes'),
            'SATURDAY': _('Sábado'),
            'SUNDAY': _('Domingo'),
        }
        return ', '.join([str(day_names.get(day.strip(), day.strip())) for day in days if day.strip()])
    
    def get_week_days_list(self):
        """Retourne la liste des jours de la semaine comme liste"""
        if not self.week_days:
            return []
        return [day.strip() for day in self.week_days.split(',') if day.strip()]


class ScheduleAssignment(models.Model):
    """Assignation récurrente d'un modèle à un horaire (basée sur les jours de la semaine de l'horaire)"""
    
    model = models.ForeignKey(
        Model,
        on_delete=models.CASCADE,
        related_name='schedule_assignments',
        verbose_name=_('Modelo')
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_('Horario')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activo'),
        help_text=_('Si está inactivo, no se crearán sesiones de trabajo para esta asignación')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='schedule_assignments_created',
        verbose_name=_('Creado por')
    )
    
    class Meta:
        verbose_name = _('Asignación de Horario')
        verbose_name_plural = _('Asignaciones de Horarios')
        ordering = ['schedule__start_time', 'model__first_name']
        unique_together = [['model', 'schedule']]
        indexes = [
            models.Index(fields=['model', 'schedule']),
            models.Index(fields=['schedule']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.model.full_name} - {self.schedule.name}"


class Pause(models.Model):
    """Pause (normale, repas ou coaching) pour une session de travail"""
    
    class PauseType(models.TextChoices):
        BREAK = 'BREAK', _('Pausa Normal')
        MEAL = 'MEAL', _('Pausa Comida')
        COACHING = 'COACHING', _('Coaching')
    
    work_session = models.ForeignKey(
        'WorkSession',
        on_delete=models.CASCADE,
        related_name='pauses',
        verbose_name=_('Sesión de Trabajo')
    )
    pause_type = models.CharField(
        max_length=20,
        choices=PauseType.choices,
        verbose_name=_('Tipo de Pausa')
    )
    start_time = models.DateTimeField(
        verbose_name=_('Hora de Inicio')
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Hora de Fin')
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
        verbose_name = _('Pausa')
        verbose_name_plural = _('Pausas')
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['work_session', 'pause_type']),
        ]
    
    def __str__(self):
        return f"{self.work_session.model.full_name} - {self.get_pause_type_display()} - {self.start_time}"
    
    def duration(self):
        """Calcule la durée de la pause en heures"""
        from datetime import timedelta
        if self.end_time:
            return round((self.end_time - self.start_time).total_seconds() / 3600, 2)
        else:
            # Pause en cours
            return round((timezone.now() - self.start_time).total_seconds() / 3600, 2)
    
    def is_active(self):
        """Vérifie si la pause est en cours"""
        return self.end_time is None


class WorkSession(models.Model):
    """Session de travail suivie par le Regional Manager"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pendiente')
        STARTED = 'STARTED', _('Iniciada')
        ON_BREAK = 'ON_BREAK', _('En Pausa')
        ON_MEAL = 'ON_MEAL', _('En Descanso para Comida')
        ON_COACHING = 'ON_COACHING', _('En Coaching')
        COMPLETED = 'COMPLETED', _('Completada')
        ABSENT = 'ABSENT', _('Ausente')
        ABSENT_APPROVED = 'ABSENT_APPROVED', _('Ausente Aprobada')
    
    model = models.ForeignKey(
        Model,
        on_delete=models.CASCADE,
        related_name='work_sessions',
        verbose_name=_('Modelo')
    )
    schedule_assignment = models.ForeignKey(
        ScheduleAssignment,
        on_delete=models.CASCADE,
        related_name='work_sessions',
        verbose_name=_('Asignación de Horario'),
        null=True,
        blank=True,
        help_text=_('Asignación récurrente (peut être null pour compatibilité)')
    )
    date = models.DateField(
        verbose_name=_('Fecha')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Estado')
    )
    
    # Horaires réels
    actual_arrival_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Hora de Llegada Real'),
        help_text=_('Confirmación de presencia por el manager')
    )
    late_minutes = models.IntegerField(
        default=0,
        verbose_name=_('Minutos de Retraso')
    )
    
    # Pauses
    break_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Inicio de Pausa')
    )
    break_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fin de Pausa')
    )
    
    # Repas
    meal_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Inicio de Descanso para Comida')
    )
    meal_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fin de Descanso para Comida')
    )
    
    # Coaching
    coaching_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Inicio de Coaching')
    )
    coaching_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fin de Coaching')
    )
    
    # Fin de session
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Hora de Fin'),
        help_text=_('Clôture par le manager')
    )
    
    # Calculs
    total_worked_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Horas Totales Trabajadas')
    )
    
    # Amendes
    late_penalty_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Monto de Multa por Retraso')
    )
    absence_penalty_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Monto de Multa por Ausencia')
    )
    
    # Paramètres financiers sauvegardés au moment de la complétion
    session_gain_amount_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Ganancia de la Sesión (USD)'),
        help_text=_('Ganancia total de cette session en USD, sauvegardée au moment de la complétion')
    )
    session_gain_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Ganancia de la Sesión (COP)'),
        help_text=_('Ganancia total de cette session en COP (convertie depuis USD), sauvegardée au moment de la complétion')
    )
    trm_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Tasa de Cambio TRM'),
        help_text=_('Taux de change USD/COP utilisé pour la conversion au moment de la complétion')
    )
    model_gain_percentage_snapshot = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Porcentaje de Ganancia del Modelo (Snapshot)'),
        help_text=_('Porcentaje sauvegardé au moment de la complétion')
    )
    bank_fee_percentage_snapshot = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Porcentaje de Impuestos (Snapshot)'),
        help_text=_('Porcentaje sauvegardé au moment de la complétion')
    )
    session_bank_fees = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Impuestos de la Sesión (COP)'),
        help_text=_('Impuestos calculados para esta session')
    )
    session_model_ganancia = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Ganancia del Modelo de la Sesión (COP)'),
        help_text=_('Ganancia final del modelo pour cette session')
    )
    
    # Traçabilité
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
        related_name='work_sessions_created',
        verbose_name=_('Creado por')
    )
    
    class Meta:
        verbose_name = _('Sesión de Trabajo')
        verbose_name_plural = _('Sesiones de Trabajo')
        ordering = ['-date', '-created_at']
        unique_together = [['model', 'date']]
        indexes = [
            models.Index(fields=['model', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.model.full_name} - {self.date} - {self.get_status_display()}"
    
    def calculate_total_break_time(self):
        """Calcule le temps total de pause (toutes les pauses de tous types) en heures"""
        from datetime import timedelta
        total_break = timedelta(0)
        
        # Utiliser uniquement les objets Pause
        for pause in self.pauses.all():
            if pause.end_time:
                total_break += (pause.end_time - pause.start_time)
            else:
                # Pause en cours
                total_break += (timezone.now() - pause.start_time)
        
        return round(total_break.total_seconds() / 3600, 2)
    
    def calculate_worked_hours(self):
        """Calcule les heures travaillées totales"""
        if not self.actual_arrival_time:
            return None
        
        from datetime import timedelta
        end_time = self.end_time if self.end_time else timezone.now()
        total_time = end_time - self.actual_arrival_time
        
        # Soustraire toutes les pauses (utiliser les objets Pause)
        for pause in self.pauses.all():
            if pause.end_time:
                total_time -= (pause.end_time - pause.start_time)
            else:
                # Pause en cours
                total_time -= (timezone.now() - pause.start_time)
        
        # Compatibilité avec les anciens champs (pour migration progressive)
        if self.break_start and self.break_end:
            total_time -= (self.break_end - self.break_start)
        elif self.break_start:
            total_time -= (timezone.now() - self.break_start)
        
        if self.meal_start and self.meal_end:
            total_time -= (self.meal_end - self.meal_start)
        elif self.meal_start:
            total_time -= (timezone.now() - self.meal_start)
        
        if self.coaching_start and self.coaching_end:
            total_time -= (self.coaching_end - self.coaching_start)
        elif self.coaching_start:
            total_time -= (timezone.now() - self.coaching_start)
        
        # Convertir en heures
        total_hours = total_time.total_seconds() / 3600
        return round(total_hours, 2)
    
    def get_active_pause(self):
        """Retourne la pause active (en cours) si elle existe"""
        return self.pauses.filter(end_time__isnull=True).first()
    
    def has_active_pause(self):
        """Vérifie s'il y a une pause en cours"""
        return self.pauses.filter(end_time__isnull=True).exists()
    
    def calculate_total_presence_time(self):
        """Calcule le temps total de présence depuis l'arrivée (sans soustraire les pauses)"""
        if not self.actual_arrival_time:
            return None
        
        from datetime import timedelta
        end_time = self.end_time if self.end_time else timezone.now()
        total_time = end_time - self.actual_arrival_time
        
        # Convertir en heures
        total_hours = total_time.total_seconds() / 3600
        return round(total_hours, 2)
