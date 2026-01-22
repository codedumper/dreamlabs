from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from datetime import datetime, timedelta, date as date_type
from django.db.models import Q

from .models import Schedule, ScheduleAssignment, WorkSession, Model, ModelGain, Pause
from agencies.models import Agency
from accounts.decorators import role_required, agency_required
from accounts.models import Role


# ==================== SCHEDULES (HORAIRES) ====================

@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
def schedule_list(request):
    """Liste des horaires"""
    agency = None
    if request.user.is_superuser or request.user.is_general_manager():
        agency_id = request.GET.get('agency')
        if agency_id:
            agency = get_object_or_404(Agency, id=agency_id)
        elif request.user.agency:
            agency = request.user.agency
    elif request.user.is_regional_manager():
        agency = request.user.agency
    
    # Si superuser ou general_manager sans agence sélectionnée, afficher tous les horaires
    if request.user.is_superuser or request.user.is_general_manager():
        if agency:
            schedules = Schedule.objects.filter(agency=agency).order_by('start_time')
        else:
            schedules = Schedule.objects.all().order_by('agency__name', 'start_time')
        agencies = Agency.objects.all()
    elif agency:
        schedules = Schedule.objects.filter(agency=agency).order_by('start_time')
        agencies = []
    else:
        schedules = Schedule.objects.none()
        agencies = []
    
    context = {
        'schedules': schedules,
        'agencies': agencies,
        'agency': agency,
    }
    return render(request, 'models_app/schedule_list.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def schedule_create(request):
    """Création d'un horaire"""
    agency = None
    if request.user.is_superuser or request.user.is_general_manager():
        agency_id = request.GET.get('agency') or request.POST.get('agency')
        if agency_id:
            agency = get_object_or_404(Agency, id=agency_id)
        elif request.user.agency:
            agency = request.user.agency
    elif request.user.is_regional_manager():
        agency = request.user.agency
    
    if request.method == 'POST':
        name = request.POST.get('name')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        meal_break_duration_str = request.POST.get('meal_break_duration', '')
        week_days = request.POST.getlist('week_days')
        
        if name and start_time and end_time and agency:
            try:
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
                
                meal_break_duration = None
                if meal_break_duration_str:
                    try:
                        hours, minutes = map(int, meal_break_duration_str.split(':'))
                        meal_break_duration = timedelta(hours=hours, minutes=minutes)
                    except ValueError:
                        pass
                
                schedule = Schedule.objects.create(
                    agency=agency,
                    name=name,
                    start_time=start_time_obj,
                    end_time=end_time_obj,
                    meal_break_duration=meal_break_duration,
                    week_days=','.join(week_days) if week_days else '',
                    created_by=request.user
                )
                messages.success(request, _('Horario creado exitosamente.'))
                return redirect('models_app:schedule_list')
            except Exception as e:
                messages.error(request, _('Error al crear el horario: {}').format(str(e)))
    
    if request.user.is_superuser or request.user.is_general_manager():
        agencies = Agency.objects.all()
    else:
        agencies = []
    
    context = {
        'agencies': agencies,
        'agency': agency,
    }
    return render(request, 'models_app/schedule_create.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def schedule_update(request, schedule_id):
    """Modification d'un horaire"""
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    # Vérifier les permissions
    if request.user.is_superuser or request.user.is_general_manager():
        pass
    elif request.user.is_regional_manager() and request.user.agency == schedule.agency:
        pass
    else:
        messages.error(request, _('No tiene acceso a este horario.'))
        return redirect('models_app:schedule_list')
    
    if request.method == 'POST':
        schedule.name = request.POST.get('name', schedule.name)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        meal_break_duration_str = request.POST.get('meal_break_duration', '')
        week_days = request.POST.getlist('week_days')
        is_active = request.POST.get('is_active') == 'on'
        
        if start_time:
            try:
                schedule.start_time = datetime.strptime(start_time, '%H:%M').time()
            except ValueError:
                pass
        
        if end_time:
            try:
                schedule.end_time = datetime.strptime(end_time, '%H:%M').time()
            except ValueError:
                pass
        
        if meal_break_duration_str:
            try:
                hours, minutes = map(int, meal_break_duration_str.split(':'))
                schedule.meal_break_duration = timedelta(hours=hours, minutes=minutes)
            except ValueError:
                schedule.meal_break_duration = None
        else:
            schedule.meal_break_duration = None
        
        schedule.week_days = ','.join(week_days) if week_days else ''
        schedule.is_active = is_active
        
        try:
            schedule.save()
            messages.success(request, _('Horario actualizado exitosamente.'))
            return redirect('models_app:schedule_list')
        except Exception as e:
            messages.error(request, _('Error al actualizar el horario: {}').format(str(e)))
    
    if request.user.is_superuser or request.user.is_general_manager():
        agencies = Agency.objects.all()
    else:
        agencies = []
    
    context = {
        'schedule': schedule,
        'agencies': agencies,
    }
    return render(request, 'models_app/schedule_update.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
def schedule_delete(request, schedule_id):
    """Suppression d'un horaire"""
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    # Vérifier les permissions
    if request.user.is_superuser or request.user.is_general_manager():
        pass
    elif request.user.is_regional_manager() and request.user.agency == schedule.agency:
        pass
    else:
        messages.error(request, _('No tiene acceso a este horario.'))
        return redirect('models_app:schedule_list')
    
    # Vérifier s'il y a des assignations (actives ou inactives)
    assignments = ScheduleAssignment.objects.filter(schedule=schedule)
    if assignments.exists():
        models_list = [assignment.model.full_name for assignment in assignments[:5]]
        models_text = ', '.join(models_list)
        if assignments.count() > 5:
            models_text += f' y {assignments.count() - 5} más'
        messages.error(request, _('No se puede eliminar este horario porque tiene modelos asignados: {}').format(models_text))
        return redirect('models_app:schedule_list')
    
    if request.method == 'POST':
        try:
            schedule.delete()
            messages.success(request, _('Horario eliminado exitosamente.'))
            return redirect('models_app:schedule_list')
        except Exception as e:
            messages.error(request, _('Error al eliminar el horario: {}').format(str(e)))
    
    context = {
        'schedule': schedule,
    }
    return render(request, 'models_app/schedule_delete.html', context)


# ==================== SCHEDULE ASSIGNMENTS (ASSIGNATIONS) ====================

@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def schedule_assignment_list(request):
    """Liste des assignations récurrentes"""
    agency = None
    if request.user.is_superuser or request.user.is_general_manager():
        agency_id = request.GET.get('agency')
        if agency_id:
            agency = get_object_or_404(Agency, id=agency_id)
        elif request.user.agency:
            agency = request.user.agency
    elif request.user.is_regional_manager():
        agency = request.user.agency
    
    if agency:
        assignments = ScheduleAssignment.objects.filter(schedule__agency=agency).select_related('model', 'schedule').order_by('schedule__start_time', 'model__first_name')
    else:
        assignments = ScheduleAssignment.objects.all().select_related('model', 'schedule').order_by('schedule__start_time', 'model__first_name')
    
    if request.user.is_superuser or request.user.is_general_manager():
        agencies = Agency.objects.all()
    else:
        agencies = []
    
    context = {
        'assignments': assignments,
        'agencies': agencies,
        'agency': agency,
    }
    return render(request, 'models_app/schedule_assignment_list.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def schedule_assignment_create(request):
    """Assignation récurrente d'un modèle à un horaire (basée sur les jours de la semaine)"""
    agency = None
    if request.user.is_superuser or request.user.is_general_manager():
        agency_id = request.GET.get('agency') or request.POST.get('agency')
        if agency_id:
            agency = get_object_or_404(Agency, id=agency_id)
        elif request.user.agency:
            agency = request.user.agency
    elif request.user.is_regional_manager():
        agency = request.user.agency
    
    if request.method == 'POST':
        model_ids = request.POST.getlist('models')
        schedule_id = request.POST.get('schedule')
        
        if not agency:
            agency_id = request.POST.get('agency')
            if agency_id:
                agency = get_object_or_404(Agency, id=agency_id)
        
        if model_ids and schedule_id and agency:
            try:
                schedule = get_object_or_404(Schedule, id=schedule_id, agency=agency)
                
                created_count = 0
                updated_count = 0
                
                for model_id in model_ids:
                    model = get_object_or_404(Model, id=model_id, agency=agency, status=Model.Status.ACTIVE)
                    
                    existing = ScheduleAssignment.objects.filter(model=model, schedule=schedule).first()
                    if existing:
                        if not existing.is_active:
                            existing.is_active = True
                            existing.save()
                            updated_count += 1
                    else:
                        ScheduleAssignment.objects.create(
                            model=model,
                            schedule=schedule,
                            created_by=request.user
                        )
                        created_count += 1
                
                if created_count > 0 and updated_count > 0:
                    messages.success(request, _('{} asignaciones creadas y {} reactivadas exitosamente.').format(created_count, updated_count))
                elif created_count > 0:
                    messages.success(request, _('{} asignaciones creadas exitosamente.').format(created_count))
                elif updated_count > 0:
                    messages.success(request, _('{} asignaciones reactivadas exitosamente.').format(updated_count))
                
                return redirect('models_app:schedule_assignment_list')
            except Exception as e:
                messages.error(request, _('Error al crear las asignaciones: {}').format(str(e)))
        elif not model_ids:
            messages.error(request, _('Debe seleccionar al menos un modelo.'))
    
    if agency:
        # Filtrer les modèles actifs et disponibles (avec fecha_ingreso définie)
        models = Model.objects.filter(
            agency=agency,
            status=Model.Status.ACTIVE,
            fecha_ingreso__isnull=False
        ).order_by('first_name', 'last_name')
        schedules = Schedule.objects.filter(agency=agency, is_active=True).order_by('start_time')
    else:
        models = Model.objects.none()
        schedules = Schedule.objects.none()
    
    if request.user.is_superuser or request.user.is_general_manager():
        agencies = Agency.objects.all()
    else:
        agencies = []
    
    context = {
        'models': models,
        'schedules': schedules,
        'agencies': agencies,
        'agency': agency,
    }
    return render(request, 'models_app/schedule_assignment_create.html', context)


# ==================== WORK SESSIONS (SESSIONS DE TRAVAIL) ====================

def _get_redirect_url_for_session(session, request):
    """Helper pour construire l'URL de redirection avec les paramètres"""
    agency_id = request.POST.get('agency') or request.GET.get('agency')
    date_str = request.POST.get('date') or request.GET.get('date') or session.date.isoformat()
    
    url_params = f"?date={date_str}"
    if agency_id:
        url_params += f"&agency={agency_id}"
    elif session.model.agency:
        url_params += f"&agency={session.model.agency.id}"
    
    return '{}{}'.format(reverse('models_app:work_session_list'), url_params)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_list(request):
    """Liste des sessions de travail pour une date"""
    agency = None
    if request.user.is_superuser or request.user.is_general_manager():
        agency_id = request.GET.get('agency')
        if agency_id:
            agency = get_object_or_404(Agency, id=agency_id)
        elif request.user.agency:
            agency = request.user.agency
    elif request.user.is_regional_manager():
        agency = request.user.agency
    
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    if agency:
        weekday_number = selected_date.weekday()
        weekday_names = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        current_weekday = weekday_names[weekday_number]
        
        assignments = ScheduleAssignment.objects.filter(
            schedule__agency=agency,
            is_active=True
        ).select_related('model', 'schedule').order_by('schedule__start_time', 'model__first_name')
        
        valid_assignments = []
        for assignment in assignments:
            # Vérifier que le modèle est disponible à la date sélectionnée
            model = assignment.model
            if model.fecha_ingreso and model.fecha_ingreso > selected_date:
                continue  # Le modèle n'est pas encore entré
            if model.fecha_retiro and model.fecha_retiro < selected_date:
                continue  # Le modèle est déjà retiré
            
            schedule = assignment.schedule
            if not schedule.week_days:
                valid_assignments.append(assignment)
            else:
                week_days_list = schedule.get_week_days_list()
                if current_weekday in week_days_list:
                    valid_assignments.append(assignment)
        
        sessions = []
        for assignment in valid_assignments:
            session, created = WorkSession.objects.get_or_create(
                model=assignment.model,
                schedule_assignment=assignment,
                date=selected_date,
                defaults={
                    'status': WorkSession.Status.PENDING,
                    'created_by': request.user
                }
            )
            sessions.append(session)
    else:
        sessions = []
    
    if request.user.is_superuser or request.user.is_general_manager():
        agencies = Agency.objects.all()
    else:
        agencies = []
    
    # Précharger les pauses et gains pour éviter N+1 queries
    session_ids = [s.id for s in sessions]
    sessions = WorkSession.objects.filter(
        id__in=session_ids
    ).prefetch_related('pauses', 'model__gains').select_related('model', 'schedule_assignment__schedule')
    
    # Calculer les compteurs après avoir préchargé les sessions
    late_count = sum(1 for s in sessions if s.late_minutes > 0)
    absent_count = sum(1 for s in sessions if s.status == WorkSession.Status.ABSENT)
    absent_approved_count = sum(1 for s in sessions if s.status == WorkSession.Status.ABSENT_APPROVED)
    
    # Calculer les totaux pour chaque session
    for session in sessions:
        session.total_break_hours = session.calculate_total_break_time()
        session.current_worked_hours = session.calculate_worked_hours()
        session.total_presence_hours = session.calculate_total_presence_time()
        
        # Liste des pauses pour l'affichage
        session.pauses_list = list(session.pauses.all())
        
        # Gain pour cette session
        gain = ModelGain.objects.filter(model=session.model, date=session.date).first()
        session.gain_amount = gain.amount if gain else None
        
        # Indicateur de session active
        session.is_active = session.status in [
            WorkSession.Status.STARTED,
            WorkSession.Status.ON_BREAK,
            WorkSession.Status.ON_MEAL,
            WorkSession.Status.ON_COACHING
        ]
    
    context = {
        'sessions': sessions,
        'agencies': agencies,
        'agency': agency,
        'selected_date': selected_date,
        'late_count': late_count,
        'absent_count': absent_count,
        'absent_approved_count': absent_approved_count,
    }
    return render(request, 'models_app/work_session_list.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_confirm_presence(request, session_id):
    """Confirme la présence du modèle"""
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        session.actual_arrival_time = timezone.now()
        session.status = WorkSession.Status.STARTED
        
        # Calculer le retard
        if session.schedule_assignment and session.schedule_assignment.schedule:
            schedule = session.schedule_assignment.schedule
            expected_arrival = timezone.make_aware(
                datetime.combine(session.date, schedule.start_time)
            )
            if session.actual_arrival_time > expected_arrival:
                delay = session.actual_arrival_time - expected_arrival
                session.late_minutes = int(delay.total_seconds() / 60)
                
                # Appliquer l'amende de retard
                if session.model.agency and session.model.agency.late_penalty > 0:
                    session.late_penalty_amount = session.model.agency.late_penalty
            else:
                session.late_minutes = 0
                session.late_penalty_amount = 0
        
        session.save()
        messages.success(request, _('Presencia confirmada exitosamente.'))
    
    return redirect(_get_redirect_url_for_session(session, request))


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_mark_absent(request, session_id):
    """Marque le modèle comme absent"""
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        approved = request.POST.get('approved') == 'true'
        
        if approved:
            session.status = WorkSession.Status.ABSENT_APPROVED
            session.absence_penalty_amount = 0  # Pas d'amende si approuvée
            messages.info(request, _('Ausencia aprobada (sin multa).'))
        else:
            session.status = WorkSession.Status.ABSENT
            # Appliquer l'amende d'absence
            if session.model.agency and session.model.agency.absence_penalty > 0:
                session.absence_penalty_amount = session.model.agency.absence_penalty
            messages.warning(request, _('Modelo marcado como ausente.'))
        
        session.save()
    
    return redirect(_get_redirect_url_for_session(session, request))


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_reactivate_from_absent(request, session_id):
    """Réactive une session marquée comme absente"""
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        session.status = WorkSession.Status.STARTED
        session.actual_arrival_time = timezone.now()
        session.absence_penalty_amount = 0
        
        # Recalculer le retard
        if session.schedule_assignment and session.schedule_assignment.schedule:
            schedule = session.schedule_assignment.schedule
            expected_arrival = timezone.make_aware(
                datetime.combine(session.date, schedule.start_time)
            )
            if session.actual_arrival_time > expected_arrival:
                delay = session.actual_arrival_time - expected_arrival
                session.late_minutes = int(delay.total_seconds() / 60)
                
                if session.model.agency and session.model.agency.late_penalty > 0:
                    session.late_penalty_amount = session.model.agency.late_penalty
            else:
                session.late_minutes = 0
                session.late_penalty_amount = 0
        
        session.save()
        messages.success(request, _('Sesión reactivada exitosamente.'))
    
    return redirect(_get_redirect_url_for_session(session, request))


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_start_break(request, session_id):
    """Démarre une pause normale"""
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        if session.has_active_pause():
            messages.error(request, _('Ya hay una pausa en curso.'))
        else:
            Pause.objects.create(
                work_session=session,
                pause_type=Pause.PauseType.BREAK,
                start_time=timezone.now()
            )
            session.status = WorkSession.Status.ON_BREAK
            session.save()
            messages.success(request, _('Pausa iniciada.'))
    
    return redirect(_get_redirect_url_for_session(session, request))


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_end_break(request, session_id):
    """Termine une pause normale"""
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        active_pause = session.get_active_pause()
        if active_pause and active_pause.pause_type == Pause.PauseType.BREAK:
            active_pause.end_time = timezone.now()
            active_pause.save()
            session.status = WorkSession.Status.STARTED
            session.save()
            messages.success(request, _('Pausa finalizada.'))
        elif session.status == WorkSession.Status.ON_BREAK:
            # Pas de pause associée mais statut ON_BREAK, on remet simplement à STARTED
            session.status = WorkSession.Status.STARTED
            session.save()
    
    return redirect(_get_redirect_url_for_session(session, request))


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_start_meal(request, session_id):
    """Démarre une pause repas"""
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        if session.has_active_pause():
            messages.error(request, _('Ya hay una pausa en curso.'))
        else:
            Pause.objects.create(
                work_session=session,
                pause_type=Pause.PauseType.MEAL,
                start_time=timezone.now()
            )
            session.status = WorkSession.Status.ON_MEAL
            session.save()
            messages.success(request, _('Pausa de comida iniciada.'))
    
    return redirect(_get_redirect_url_for_session(session, request))


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_end_meal(request, session_id):
    """Termine une pause repas"""
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        active_pause = session.get_active_pause()
        if active_pause and active_pause.pause_type == Pause.PauseType.MEAL:
            active_pause.end_time = timezone.now()
            active_pause.save()
            session.status = WorkSession.Status.STARTED
            session.save()
            messages.success(request, _('Pausa de comida finalizada.'))
        elif session.status == WorkSession.Status.ON_MEAL:
            session.status = WorkSession.Status.STARTED
            session.save()
    
    return redirect(_get_redirect_url_for_session(session, request))


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_start_coaching(request, session_id):
    """Démarre une pause coaching"""
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        if session.has_active_pause():
            messages.error(request, _('Ya hay una pausa en curso.'))
        else:
            Pause.objects.create(
                work_session=session,
                pause_type=Pause.PauseType.COACHING,
                start_time=timezone.now()
            )
            session.status = WorkSession.Status.ON_COACHING
            session.save()
            messages.success(request, _('Coaching iniciado.'))
    
    return redirect(_get_redirect_url_for_session(session, request))


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_end_coaching(request, session_id):
    """Termine une pause coaching"""
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        active_pause = session.get_active_pause()
        if active_pause and active_pause.pause_type == Pause.PauseType.COACHING:
            active_pause.end_time = timezone.now()
            active_pause.save()
            session.status = WorkSession.Status.STARTED
            session.save()
            messages.success(request, _('Coaching finalizado.'))
        elif session.status == WorkSession.Status.ON_COACHING:
            session.status = WorkSession.Status.STARTED
            session.save()
    
    return redirect(_get_redirect_url_for_session(session, request))


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_complete(request, session_id):
    """Complète une session de travail"""
    from decimal import Decimal
    from .utils import convert_usd_to_cop
    
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        gain_amount_usd = request.POST.get('gain_amount_usd')
        gain_description = request.POST.get('gain_description', '')
        
        session.end_time = timezone.now()
        session.status = WorkSession.Status.COMPLETED
        session.total_worked_hours = float(session.calculate_worked_hours())
        
        # Sauvegarder les paramètres financiers au moment de la complétion
        if session.model.agency:
            agency = session.model.agency
            session.model_gain_percentage_snapshot = agency.model_gain_percentage or Decimal('0.00')
            session.bank_fee_percentage_snapshot = agency.bank_fee_percentage or Decimal('0.00')
        
        # Calculer et sauvegarder les valeurs financières de la session
        if gain_amount_usd:
            try:
                session_gain_usd = Decimal(str(gain_amount_usd))
                session.session_gain_amount_usd = session_gain_usd
                
                # Convertir USD en COP en utilisant le TRM
                session_date = session.date
                session_gain_cop, trm_rate = convert_usd_to_cop(session_gain_usd, session_date)
                
                if session_gain_cop is None or trm_rate is None:
                    messages.error(request, _('Error al obtener el TRM. Por favor, intente nuevamente.'))
                    return redirect(_get_redirect_url_for_session(session, request))
                
                session.session_gain_amount = session_gain_cop
                session.trm_rate = trm_rate
                
                # Calculer les impuestos (basé sur COP)
                if session.bank_fee_percentage_snapshot:
                    session.session_bank_fees = session_gain_cop * session.bank_fee_percentage_snapshot / Decimal('100.00')
                else:
                    session.session_bank_fees = Decimal('0.00')
                
                # Calculer la ganancia del modelo
                ganancia_after_bank_fees = session_gain_cop - session.session_bank_fees
                if session.model_gain_percentage_snapshot:
                    ganancia_porcentaje = ganancia_after_bank_fees * session.model_gain_percentage_snapshot / Decimal('100.00')
                else:
                    ganancia_porcentaje = Decimal('0.00')
                
                total_multas = (session.late_penalty_amount or Decimal('0.00')) + (session.absence_penalty_amount or Decimal('0.00'))
                session.session_model_ganancia = ganancia_porcentaje - total_multas
                
                # Créer ou mettre à jour le gain (en COP)
                ModelGain.objects.update_or_create(
                    model=session.model,
                    date=session.date,
                    defaults={
                        'amount': float(session_gain_cop),
                        'description': gain_description
                    }
                )
            except (ValueError, TypeError) as e:
                messages.error(request, _('Error al procesar el monto de ganancia.'))
                return redirect(_get_redirect_url_for_session(session, request))
        
        session.save()
        messages.success(request, _('Sesión completada exitosamente.'))
    
    return redirect(_get_redirect_url_for_session(session, request))


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def work_session_reopen(request, session_id):
    """Rouvre une session complétée"""
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        session.status = WorkSession.Status.STARTED
        session.end_time = None
        session.total_worked_hours = None
        session.save()
        
        # Supprimer le gain associé
        ModelGain.objects.filter(model=session.model, date=session.date).delete()
        
        messages.success(request, _('Sesión reabierta exitosamente.'))
    
    return redirect(_get_redirect_url_for_session(session, request))
