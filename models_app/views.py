from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum, Avg
from django.utils import timezone
from datetime import datetime, date, timedelta
from calendar import monthrange
from decimal import Decimal
from .models import Model, ModelGain, WorkedHours, WorkSession, ScheduleAssignment, Schedule
from .utils import convert_usd_to_cop, get_trm_rate
from agencies.models import Agency, BonusRule
from accounts.decorators import regional_manager_required, agency_required, role_required
from accounts.models import Role
from accounts.utils import filter_by_agency_queryset


def count_worked_days_in_period(model, period_start, period_end):
    """
    Compte le nombre de jours travaillés dans une période selon l'horaire du modèle.
    
    Args:
        model: Instance du modèle
        period_start: Date de début de la période
        period_end: Date de fin de la période
    
    Returns:
        int: Nombre de jours travaillés dans la période selon l'horaire
    """
    # Récupérer toutes les assignations d'horaires actives du modèle
    schedule_assignments = ScheduleAssignment.objects.filter(
        model=model,
        is_active=True
    ).select_related('schedule')
    
    if not schedule_assignments.exists():
        # Si pas d'horaire, retourner 0
        return 0
    
    # Récupérer tous les jours de la semaine travaillés (union de tous les horaires)
    worked_weekdays = set()
    for assignment in schedule_assignments:
        schedule = assignment.schedule
        if schedule.week_days:
            days = schedule.get_week_days_list()
            worked_weekdays.update(days)
    
    if not worked_weekdays:
        # Si aucun jour défini, retourner 0
        return 0
    
    # Mapper les jours de la semaine aux numéros (0 = lundi, 6 = dimanche)
    weekday_map = {
        'MONDAY': 0,
        'TUESDAY': 1,
        'WEDNESDAY': 2,
        'THURSDAY': 3,
        'FRIDAY': 4,
        'SATURDAY': 5,
        'SUNDAY': 6,
    }
    
    # Convertir les jours travaillés en numéros
    worked_weekday_numbers = {weekday_map[day] for day in worked_weekdays if day in weekday_map}
    
    # Compter les jours dans la période qui correspondent aux jours travaillés
    count = 0
    current_date = period_start
    while current_date <= period_end:
        # weekday() retourne 0 pour lundi, 6 pour dimanche
        if current_date.weekday() in worked_weekday_numbers:
            count += 1
        current_date += timedelta(days=1)
    
    return count


@login_required
def model_list(request):
    """
    Liste des modèles
    - General Manager : voit tous les modèles (actifs et inactifs)
    - Regional Manager : voit uniquement les modèles de son agence (actifs par défaut)
    - Modèle : voit uniquement son propre profil
    """
    if request.user.is_general_manager():
        # General Manager voit tout
        models = Model.objects.all().order_by('-created_at')
        show_inactive = request.GET.get('show_inactive', 'false') == 'true'
        if not show_inactive:
            models = models.filter(status=Model.Status.ACTIVE)
    elif request.user.is_regional_manager() and request.user.agency:
        # Regional Manager voit les modèles de son agence
        models = Model.objects.filter(agency=request.user.agency).order_by('-created_at')
        show_inactive = request.GET.get('show_inactive', 'false') == 'true'
        if not show_inactive:
            models = models.filter(status=Model.Status.ACTIVE)
    elif request.user.is_modele() and hasattr(request.user, 'model_profile'):
        # Modèle voit uniquement son profil
        models = Model.objects.filter(id=request.user.model_profile.id)
    else:
        models = Model.objects.none()
        messages.warning(request, _('No tiene acceso a los modelos.'))
    
    context = {
        'models': models,
        'show_inactive': request.GET.get('show_inactive', 'false') == 'true',
    }
    return render(request, 'models_app/list.html', context)


@login_required
def model_detail(request, model_id):
    """
    Détails d'un modèle
    - General Manager : peut voir tous les modèles
    - Regional Manager : peut voir les modèles de son agence
    - Modèle : peut voir uniquement son propre profil
    """
    model = get_object_or_404(Model, id=model_id)
    
    # Vérifier les permissions
    if request.user.is_general_manager():
        # General Manager peut tout voir
        pass
    elif request.user.is_regional_manager() and request.user.agency == model.agency:
        # Regional Manager peut voir les modèles de son agence
        pass
    elif request.user.is_modele() and hasattr(request.user, 'model_profile') and request.user.model_profile == model:
        # Modèle peut voir son propre profil
        pass
    else:
        messages.error(request, _('No tiene acceso a este modelo.'))
        return redirect('models_app:list')
    
    # Récupérer les horaires assignés récurrents actifs
    assignments = ScheduleAssignment.objects.filter(
        model=model,
        is_active=True
    ).select_related('schedule').order_by('schedule__start_time')
    
    # Filtres de date pour les sessions
    hours_date_from = request.GET.get('hours_date_from')
    hours_date_to = request.GET.get('hours_date_to')
    
    # Récupérer les sessions de travail avec filtres
    sessions_query = WorkSession.objects.filter(model=model).select_related('schedule_assignment', 'schedule_assignment__schedule')
    if hours_date_from:
        try:
            hours_date_from = datetime.strptime(hours_date_from, '%Y-%m-%d').date()
            sessions_query = sessions_query.filter(date__gte=hours_date_from)
        except ValueError:
            hours_date_from = None
    if hours_date_to:
        try:
            hours_date_to = datetime.strptime(hours_date_to, '%Y-%m-%d').date()
            sessions_query = sessions_query.filter(date__lte=hours_date_to)
        except ValueError:
            hours_date_to = None
    
    # Récupérer toutes les sessions complétées avec leurs calculs sauvegardés
    sessions_list = list(sessions_query.filter(status=WorkSession.Status.COMPLETED).order_by('-date', '-created_at')[:50])
    
    # Récupérer les règles de bonus actives de l'agence, triées par ordre croissant
    bonus_rules = []
    if model.agency:
        bonus_rules = list(BonusRule.objects.filter(agency=model.agency, is_active=True).order_by('order'))
    
    # Calculer les bonus par période (une seule fois par période, au dernier jour réel de la période)
    # Structure: {(rule_id, period_key): {'bonus': amount, 'target_date': date, 'session': session}}
    period_bonuses = {}
    
    # Identifier toutes les périodes uniques pour chaque type de règle
    all_periods = {}  # {(period_type, period_key): {'period_start': date, 'period_end': date, 'sessions': [sessions]}}
    
    for session in sessions_list:
        # Identifier les périodes pour chaque type
        session_date = session.date
        
        # Période quotidienne
        daily_key = f"DAILY_{session_date.isoformat()}"
        if daily_key not in all_periods:
            all_periods[daily_key] = {
                'period_type': BonusRule.PeriodType.DAILY,
                'period_start': session_date,
                'period_end': session_date,
                'sessions': [s for s in sessions_list if s.date == session_date]
            }
        
        # Période hebdomadaire
        week_start = session_date - timedelta(days=session_date.weekday())
        week_end = week_start + timedelta(days=6)
        weekly_key = f"WEEKLY_{week_start.isoformat()}"
        if weekly_key not in all_periods:
            all_periods[weekly_key] = {
                'period_type': BonusRule.PeriodType.WEEKLY,
                'period_start': week_start,
                'period_end': week_end,
                'sessions': [s for s in sessions_list if week_start <= s.date <= week_end]
            }
        
        # Période quinzaine
        day = session_date.day
        if day <= 15:
            biweek_start = session_date.replace(day=1)
            biweek_end = session_date.replace(day=15)
        else:
            biweek_start = session_date.replace(day=16)
            last_day = monthrange(session_date.year, session_date.month)[1]
            biweek_end = session_date.replace(day=last_day)
        biweekly_key = f"BIWEEKLY_{biweek_start.isoformat()}"
        if biweekly_key not in all_periods:
            all_periods[biweekly_key] = {
                'period_type': BonusRule.PeriodType.BIWEEKLY,
                'period_start': biweek_start,
                'period_end': biweek_end,
                'sessions': [s for s in sessions_list if biweek_start <= s.date <= biweek_end]
            }
        
        # Période mensuelle
        month_start = session_date.replace(day=1)
        last_day = monthrange(session_date.year, session_date.month)[1]
        month_end = session_date.replace(day=last_day)
        monthly_key = f"MONTHLY_{month_start.isoformat()}"
        if monthly_key not in all_periods:
            all_periods[monthly_key] = {
                'period_type': BonusRule.PeriodType.MONTHLY,
                'period_start': month_start,
                'period_end': month_end,
                'sessions': [s for s in sessions_list if month_start <= s.date <= month_end]
            }
    
    # Pour chaque période, appliquer les règles dans l'ordre croissant
    # On s'arrête à la première règle qui correspond si stop_on_match est activé
    for period_key, period_data in all_periods.items():
        period_sessions = period_data['sessions']
        period_start = period_data['period_start']
        period_end = period_data['period_end']
        period_type = period_data['period_type']
        
        if not period_sessions:
            continue
        
        # Parcourir les règles dans l'ordre croissant
        for rule in bonus_rules:
            # Vérifier que la règle correspond au type de période
            if rule.period_type != period_type:
                continue
            
            # Compter le nombre de jours travaillés dans la période selon l'horaire
            worked_days_count = count_worked_days_in_period(model, period_start, period_end)
            
            if worked_days_count == 0:
                # Si aucun jour travaillé selon l'horaire, passer à la règle suivante
                continue
            
            # Calculer la somme de ganancia pour la période
            # Utiliser USD ou COP selon la devise de l'objectif
            if rule.target_currency == BonusRule.TargetCurrency.USD:
                # Utiliser les valeurs USD
                total_period_gain = sum(s.session_gain_amount_usd or Decimal('0.00') for s in period_sessions)
            else:  # COP
                # Utiliser les valeurs COP
                total_period_gain = sum(s.session_gain_amount or Decimal('0.00') for s in period_sessions)
            
            # Calculer la moyenne journalière : somme des ganancias / nombre de jours travaillés selon l'horaire
            avg_daily_gain = total_period_gain / Decimal(str(worked_days_count))
            
            # Vérifier si la moyenne journalière atteint l'objectif
            if avg_daily_gain >= rule.target_amount:
                # Calculer le bonus selon le type
                # Pour le bonus, on utilise toujours la ganancia total en COP (pour le calcul du pourcentage)
                if rule.bonus_type == BonusRule.BonusType.PERCENTAGE:
                    # Pour le pourcentage, utiliser la ganancia total en COP
                    total_period_gain_cop = sum(s.session_gain_amount or Decimal('0.00') for s in period_sessions)
                    bonus_amount = total_period_gain_cop * rule.bonus_value / Decimal('100.00')
                else:  # FIXED_AMOUNT
                    # Le montant fixe est toujours en COP
                    bonus_amount = rule.bonus_value
                
                # Trouver la session qui correspond EXACTEMENT au dernier jour réel de la période
                # Si aucune session n'existe ce jour-là, on ne peut pas attribuer le bonus
                target_session = None
                for s in period_sessions:
                    if s.date == period_end:
                        target_session = s
                        break
                
                # Stocker le bonus UNIQUEMENT si une session existe exactement au dernier jour réel
                if target_session:
                    period_id = (rule.id, period_key)
                    period_bonuses[period_id] = {
                        'bonus': bonus_amount,
                        'target_date': period_end,  # Dernier jour réel de la période
                        'session': target_session,  # Session à laquelle attribuer le bonus (doit être au dernier jour réel)
                        'rule': rule,
                        'period_gain': total_period_gain,
                        'avg_period_gain': avg_daily_gain,
                        'worked_days_count': worked_days_count
                    }
                    
                    # Si stop_on_match est activé, s'arrêter après avoir appliqué cette règle
                    if rule.stop_on_match:
                        break
    
    # Préparer les sessions avec leurs calculs individuels
    sessions_with_calculations = []
    for session in sessions_list:
        # Utiliser les valeurs sauvegardées si disponibles
        session_gain = session.session_gain_amount if session.session_gain_amount else Decimal('0.00')
        session_bank_fees = session.session_bank_fees if session.session_bank_fees else Decimal('0.00')
        session_multas = (session.late_penalty_amount or Decimal('0.00')) + (session.absence_penalty_amount or Decimal('0.00'))
        session_model_ganancia = session.session_model_ganancia if session.session_model_ganancia else Decimal('0.00')
        model_gain_pct = session.model_gain_percentage_snapshot if session.model_gain_percentage_snapshot is not None else (model.agency.model_gain_percentage if model.agency else Decimal('0.00'))
        bank_fee_pct = session.bank_fee_percentage_snapshot if session.bank_fee_percentage_snapshot is not None else (model.agency.bank_fee_percentage if model.agency else Decimal('0.00'))
        
        # Vérifier si cette session correspond au dernier jour réel d'une période avec bonus
        session_bonus = Decimal('0.00')
        applicable_rules = []
        
        for period_id, bonus_data in period_bonuses.items():
            # Attribuer le bonus UNIQUEMENT si cette session correspond EXACTEMENT au dernier jour réel
            # Vérifier à la fois l'ID de la session ET que la date correspond au dernier jour réel
            if (bonus_data['session'].id == session.id and 
                session.date == bonus_data['target_date']):
                session_bonus += bonus_data['bonus']
                applicable_rules.append({
                    'rule': bonus_data['rule'],
                    'amount': bonus_data['bonus'],
                    'period_gain': bonus_data['period_gain'],
                    'avg_period_gain': bonus_data['avg_period_gain'],
                    'target_date': bonus_data['target_date']  # Dernier jour réel de la période
                })
        
        session_data = {
            'session': session,
            'gain': session_gain,
            'bank_fees': session_bank_fees,
            'multas': session_multas,
            'model_ganancia': session_model_ganancia,
            'bonus': session_bonus,
            'applicable_rules': applicable_rules,
            'model_gain_percentage': model_gain_pct,
            'bank_fee_percentage': bank_fee_pct,
        }
        sessions_with_calculations.append(session_data)
    
    # Calculer les totaux globaux
    total_gain = sum(item['gain'] for item in sessions_with_calculations)
    total_bank_fees = sum(item['bank_fees'] for item in sessions_with_calculations)
    total_multas = sum(item['multas'] for item in sessions_with_calculations)
    # Pour le total des bonus, utiliser les bonus calculés par période (une seule fois par période)
    total_bonus = sum(bonus_data['bonus'] for bonus_data in period_bonuses.values())
    total_model_ganancia = sum(item['model_ganancia'] for item in sessions_with_calculations)
    
    # Calculer les totaux d'heures (pour compatibilité avec l'affichage existant)
    total_worked_hours = sum(session.calculate_worked_hours() or 0 for session in sessions_list)
    total_break_hours = sum(session.calculate_total_break_time() or 0 for session in sessions_list)
    total_presence_hours = sum(session.calculate_total_presence_time() or 0 for session in sessions_list)
    total_sessions = len(sessions_with_calculations)
    avg_worked_hours = total_worked_hours / total_sessions if total_sessions > 0 else 0
    
    # Calculer les indicateurs de moyenne : Semaine courante et Quinzaine
    today = date.today()
    
    # Promedio de la semana corriente (lundi à dimanche de la semaine actuelle)
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_sessions = [s for s in sessions_list if week_start <= s.date <= week_end]
    if week_sessions:
        week_total_cop = sum(s.session_gain_amount or Decimal('0.00') for s in week_sessions)
        week_total_usd = sum(s.session_gain_amount_usd or Decimal('0.00') for s in week_sessions if s.session_gain_amount_usd)
        week_avg_cop = week_total_cop / len(week_sessions)
        week_avg_usd = week_total_usd / len(week_sessions) if week_total_usd > 0 else Decimal('0.00')
    else:
        week_avg_cop = Decimal('0.00')
        week_avg_usd = Decimal('0.00')
    
    # Promedio de la Quinzena (1-15 ou 16-fin du mois)
    day = today.day
    if day <= 15:
        quincena_start = today.replace(day=1)
        quincena_end = today.replace(day=15)
    else:
        quincena_start = today.replace(day=16)
        last_day = monthrange(today.year, today.month)[1]
        quincena_end = today.replace(day=last_day)
    
    quincena_sessions = [s for s in sessions_list if quincena_start <= s.date <= quincena_end]
    if quincena_sessions:
        quincena_total_cop = sum(s.session_gain_amount or Decimal('0.00') for s in quincena_sessions)
        quincena_total_usd = sum(s.session_gain_amount_usd or Decimal('0.00') for s in quincena_sessions if s.session_gain_amount_usd)
        quincena_avg_cop = quincena_total_cop / len(quincena_sessions)
        quincena_avg_usd = quincena_total_usd / len(quincena_sessions) if quincena_total_usd > 0 else Decimal('0.00')
    else:
        quincena_avg_cop = Decimal('0.00')
        quincena_avg_usd = Decimal('0.00')
    
    # Promedio del Mes (1er au dernier jour du mois actuel)
    month_start = today.replace(day=1)
    last_day = monthrange(today.year, today.month)[1]
    month_end = today.replace(day=last_day)
    
    month_sessions = [s for s in sessions_list if month_start <= s.date <= month_end]
    if month_sessions:
        month_total_cop = sum(s.session_gain_amount or Decimal('0.00') for s in month_sessions)
        month_total_usd = sum(s.session_gain_amount_usd or Decimal('0.00') for s in month_sessions if s.session_gain_amount_usd)
        month_avg_cop = month_total_cop / len(month_sessions)
        month_avg_usd = month_total_usd / len(month_sessions) if month_total_usd > 0 else Decimal('0.00')
    else:
        month_avg_cop = Decimal('0.00')
        month_avg_usd = Decimal('0.00')
    
    # Récupérer le mot de passe temporaire depuis la session (si réinitialisé récemment)
    user_password_temp = None
    if model.user:
        session_key = f'user_password_{model.user.id}'
        user_password_temp = request.session.get(session_key)
        # Supprimer après affichage (sécurité)
        if user_password_temp:
            del request.session[session_key]
    
    # Calculer la moyenne journalière pour la quinzaine actuelle pour le graphique gauge
    # Basé sur les jours travaillés selon l'horaire et la période du bonus (quinzaine)
    today = date.today()
    day = today.day
    
    # Déterminer la quinzaine actuelle
    if day <= 15:
        quincena_start = today.replace(day=1)
        quincena_end = today.replace(day=15)
    else:
        quincena_start = today.replace(day=16)
        last_day = monthrange(today.year, today.month)[1]
        quincena_end = today.replace(day=last_day)
    
    # Compter les jours travaillés dans la quinzaine selon l'horaire
    worked_days_quincena = count_worked_days_in_period(model, quincena_start, quincena_end)
    
    # Récupérer les sessions de la quinzaine actuelle
    quincena_sessions = [s for s in sessions_list if quincena_start <= s.date <= quincena_end]
    
    # Calculer le promedio journalier pour la quinzaine en USD
    avg_daily_gain_usd = Decimal('0.00')
    if quincena_sessions and worked_days_quincena > 0:
        # Utiliser uniquement session_gain_amount_usd pour le calcul
        total_gain_usd = sum(s.session_gain_amount_usd or Decimal('0.00') for s in quincena_sessions)
        # Diviser par le nombre de jours travaillés selon l'horaire, pas par le nombre de sessions
        avg_daily_gain_usd = total_gain_usd / Decimal(str(worked_days_quincena)) if total_gain_usd > 0 else Decimal('0.00')
    
    # Calculer aussi en COP pour l'affichage
    avg_daily_gain_cop = Decimal('0.00')
    if quincena_sessions and worked_days_quincena > 0:
        total_gain_cop = sum(s.session_gain_amount or Decimal('0.00') for s in quincena_sessions)
        avg_daily_gain_cop = total_gain_cop / Decimal(str(worked_days_quincena))
    
    # Préparer les jalons de bonus pour le graphique gauge
    # Récupérer UNIQUEMENT les règles de type BIWEEKLY (quinzaine), triées par ordre
    # Garder les jalons en USD pour le graphique
    bonus_milestones = []
    biweekly_bonus_rules = []
    if bonus_rules:
        for rule in bonus_rules:
            # Comparer avec la valeur de l'enum (qui est 'BIWEEKLY')
            if rule.period_type == BonusRule.PeriodType.BIWEEKLY or rule.period_type == 'BIWEEKLY':
                biweekly_bonus_rules.append(rule)
                # Pour le graphique, on utilise USD uniquement
                # Si le jalon est en COP, on le convertit en USD avec le TRM actuel
                if rule.target_currency == BonusRule.TargetCurrency.USD:
                    milestone_value = float(rule.target_amount)
                    milestone_currency = 'USD'
                else:
                    # Convertir COP en USD pour le graphique
                    try:
                        cop_amount = rule.target_amount
                        trm_rate = get_trm_rate(today)
                        if trm_rate and trm_rate > 0:
                            milestone_value = float(cop_amount) / float(trm_rate)
                        else:
                            # Si le TRM n'est pas disponible, utiliser une approximation
                            milestone_value = float(cop_amount) / 4000
                    except Exception:
                        # En cas d'erreur, utiliser une approximation
                        milestone_value = float(rule.target_amount) / 4000
                    milestone_currency = 'USD'
                
                bonus_milestones.append({
                    'value': milestone_value,
                    'currency': milestone_currency,
                    'name': rule.name,
                    'order': rule.order,
                    'original_currency': rule.target_currency
                })
    
    context = {
        'model': model,
        'assignments': assignments,
        'sessions_with_calculations': sessions_with_calculations,
        'total_worked_hours': total_worked_hours,
        'total_break_hours': total_break_hours,
        'total_presence_hours': total_presence_hours,
        'total_sessions': total_sessions,
        'avg_worked_hours': avg_worked_hours,
        'total_gain': total_gain,
        'total_multas': total_multas,
        'total_bank_fees': total_bank_fees,
        'total_bonus': total_bonus,
        'total_model_ganancia': total_model_ganancia,
        'hours_date_from': hours_date_from,
        'hours_date_to': hours_date_to,
        'week_avg_cop': week_avg_cop,
        'week_avg_usd': week_avg_usd,
        'quincena_avg_cop': quincena_avg_cop,
        'quincena_avg_usd': quincena_avg_usd,
        'month_avg_cop': month_avg_cop,
        'month_avg_usd': month_avg_usd,
        'user_password_temp': user_password_temp,
        'avg_daily_gain_cop': avg_daily_gain_cop,
        'avg_daily_gain_usd': avg_daily_gain_usd,
        'bonus_milestones': bonus_milestones,
        'bonus_rules': bonus_rules,
        'biweekly_bonus_rules': biweekly_bonus_rules,
        'worked_days_quincena': worked_days_quincena,
        'quincena_start': quincena_start,
        'quincena_end': quincena_end,
    }
    return render(request, 'models_app/detail.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def model_create(request):
    """Création d'un modèle"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Déterminer l'agence selon le rôle
    agency = None
    can_choose_agency = False
    
    if request.user.is_superuser or request.user.is_general_manager():
        # Admin et General Manager peuvent choisir l'agence
        can_choose_agency = True
        if request.method == 'POST':
            agency_id = request.POST.get('agency')
            if agency_id:
                agency = get_object_or_404(Agency, id=agency_id)
    elif request.user.is_regional_manager() and request.user.agency:
        # Regional Manager : agence automatique
        agency = request.user.agency
        can_choose_agency = False
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        edad = request.POST.get('edad', '').strip()
        platform = request.POST.get('platform', Model.Platform.FLIRTIFY)
        cedula = request.POST.get('cedula', '').strip()
        security_contact_name = request.POST.get('security_contact_name', '').strip()
        security_contact_phone = request.POST.get('security_contact_phone', '').strip()
        eps = request.POST.get('eps', '').strip()
        fecha_ingreso = request.POST.get('fecha_ingreso', '').strip()
        fecha_retiro = request.POST.get('fecha_retiro', '').strip()
        create_user_account = request.POST.get('create_user_account') == 'on'
        
        # Pour admin/general manager, récupérer l'agence depuis le formulaire
        if can_choose_agency and not agency:
            agency_id = request.POST.get('agency')
            if agency_id:
                try:
                    agency = get_object_or_404(Agency, id=agency_id)
                except Exception as e:
                    logger.error(f"Error getting agency {agency_id}: {str(e)}")
                    messages.error(request, _('Error al seleccionar la agencia.'))
        
        # Validation détaillée avec messages d'erreur spécifiques
        validation_errors = []
        if not first_name:
            validation_errors.append(_('El nombre es obligatorio.'))
        if not last_name:
            validation_errors.append(_('El apellido es obligatorio.'))
        if not agency:
            validation_errors.append(_('Debe seleccionar una agencia.'))
        if not fecha_ingreso:
            validation_errors.append(_('La fecha de ingreso es obligatoria.'))
        
        if validation_errors:
            for error in validation_errors:
                messages.error(request, error)
            logger.warning(f"Validation failed for model creation: {validation_errors}")
        elif first_name and last_name and agency and fecha_ingreso:
            try:
                from datetime import datetime
                fecha_ingreso_date = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date() if fecha_ingreso else None
                fecha_retiro_date = datetime.strptime(fecha_retiro, '%Y-%m-%d').date() if fecha_retiro else None
                
                logger.info(f"Creating model: {first_name} {last_name}, agency: {agency.name}, fecha_ingreso: {fecha_ingreso_date}")
                
                model = Model.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email if email else None,
                    phone=phone,
                    password=password if password else None,
                    edad=int(edad) if edad else None,
                    platform=platform,
                    cedula=cedula if cedula else None,
                    security_contact_name=security_contact_name if security_contact_name else None,
                    security_contact_phone=security_contact_phone if security_contact_phone else None,
                    eps=eps if eps else None,
                    fecha_ingreso=fecha_ingreso_date,
                    fecha_retiro=fecha_retiro_date,
                    agency=agency,
                    status=Model.Status.ACTIVE
                )
                
                logger.info(f"Model created successfully with ID: {model.id}")
                
                # Créer un compte utilisateur optionnel
                if create_user_account:
                    try:
                        from django.contrib.auth import get_user_model
                        from django.utils.crypto import get_random_string
                        from accounts.models import Role
                        User = get_user_model()
                        
                        # Générer un username unique
                        username = f"{first_name.lower()}.{last_name.lower()}"
                        base_username = username
                        counter = 1
                        while User.objects.filter(username=username).exists():
                            username = f"{base_username}{counter}"
                            counter += 1
                        
                        # Générer un mot de passe aléatoire
                        random_password = get_random_string(length=12)
                        
                        # Créer l'utilisateur
                        modele_role = Role.objects.get(name=Role.RoleType.MODELE)
                        user = User.objects.create_user(
                            username=username,
                            email=email if email else f"{username}@dreamslabs.com",
                            password=random_password,
                            role=modele_role,
                            agency=agency
                        )
                        model.user = user
                        model.save()
                        logger.info(f"User account created for model {model.id}: {username}")
                        messages.info(request, _('Cuenta de usuario creada. El modelo debe cambiar su contraseña al primer inicio de sesión.'))
                    except Exception as e:
                        logger.error(f"Error creating user account for model: {str(e)}")
                        messages.warning(request, _('Modelo creado pero hubo un error al crear la cuenta de usuario: {}').format(str(e)))
                
                messages.success(request, _('Modelo creado exitosamente.'))
                return redirect('models_app:detail', model_id=model.id)
            except ValueError as e:
                logger.error(f"ValueError creating model: {str(e)}")
                messages.error(request, _('Error en el formato de los datos: {}').format(str(e)))
            except Exception as e:
                logger.error(f"Exception creating model: {str(e)}", exc_info=True)
                messages.error(request, _('Error al crear el modelo: {}').format(str(e)))
    
    # Préparer le contexte selon le rôle
    if can_choose_agency:
        # Admin et General Manager : afficher toutes les agences
        agencies = Agency.objects.all()
        context = {
            'agencies': agencies,
            'agency': agency,
            'can_choose_agency': True,
        }
    else:
        # Regional Manager : agence fixe
        context = {
            'agencies': [],
            'agency': agency,
            'can_choose_agency': False,
        }
    
    # Si c'est une requête POST avec erreurs, passer les valeurs du formulaire au contexte
    if request.method == 'POST':
        context.update({
            'form_data': {
                'first_name': request.POST.get('first_name', ''),
                'last_name': request.POST.get('last_name', ''),
                'email': request.POST.get('email', ''),
                'phone': request.POST.get('phone', ''),
                'edad': request.POST.get('edad', ''),
                'cedula': request.POST.get('cedula', ''),
                'security_contact_name': request.POST.get('security_contact_name', ''),
                'security_contact_phone': request.POST.get('security_contact_phone', ''),
                'eps': request.POST.get('eps', ''),
                'fecha_ingreso': request.POST.get('fecha_ingreso', ''),
                'fecha_retiro': request.POST.get('fecha_retiro', ''),
                'platform': request.POST.get('platform', Model.Platform.FLIRTIFY),
                'create_user_account': request.POST.get('create_user_account') == 'on',
            }
        })
    
    return render(request, 'models_app/create.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def model_update(request, model_id):
    """Modification d'un modèle"""
    model = get_object_or_404(Model, id=model_id)
    
    # Vérifier les permissions
    can_edit_agency = False
    if request.user.is_superuser or request.user.is_general_manager():
        # Admin et General Manager peuvent modifier l'agence
        can_edit_agency = True
    elif request.user.is_regional_manager():
        # Regional Manager ne peut modifier que les modèles de son agence
        if model.agency != request.user.agency:
            messages.error(request, _('No tiene acceso a este modelo.'))
            return redirect('models_app:list')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        edad = request.POST.get('edad', '')
        platform = request.POST.get('platform', Model.Platform.FLIRTIFY)
        cedula = request.POST.get('cedula', '')
        security_contact_name = request.POST.get('security_contact_name', '')
        security_contact_phone = request.POST.get('security_contact_phone', '')
        eps = request.POST.get('eps', '')
        fecha_ingreso = request.POST.get('fecha_ingreso', '')
        fecha_retiro = request.POST.get('fecha_retiro', '')
        
        # Gestion de l'utilisateur
        manage_user = request.POST.get('manage_user', '')
        remove_user = request.POST.get('remove_user') == 'on'
        
        # Pour admin/general manager, permettre de changer l'agence
        if can_edit_agency:
            agency_id = request.POST.get('agency')
            if agency_id:
                new_agency = get_object_or_404(Agency, id=agency_id)
                model.agency = new_agency
        
        if first_name and last_name and fecha_ingreso:
            try:
                from datetime import datetime
                from django.contrib.auth import get_user_model
                from django.utils.crypto import get_random_string
                from accounts.models import Role
                User = get_user_model()
                
                fecha_ingreso_date = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date() if fecha_ingreso else model.fecha_ingreso
                fecha_retiro_date = datetime.strptime(fecha_retiro, '%Y-%m-%d').date() if fecha_retiro else None
                
                model.first_name = first_name
                model.last_name = last_name
                model.email = email if email else None
                model.phone = phone
                # Ne mettre à jour le password que s'il est fourni (et si l'utilisateur est manager)
                if password and (request.user.is_superuser or request.user.is_general_manager() or request.user.is_regional_manager()):
                    model.password = password
                model.edad = int(edad) if edad else None
                model.platform = platform
                model.cedula = cedula if cedula else None
                model.security_contact_name = security_contact_name if security_contact_name else None
                model.security_contact_phone = security_contact_phone if security_contact_phone else None
                model.eps = eps if eps else None
                model.fecha_ingreso = fecha_ingreso_date
                model.fecha_retiro = fecha_retiro_date
                model.save()
                
                # Gérer l'utilisateur associé
                agency = model.agency
                if remove_user and model.user:
                    # Supprimer l'utilisateur associé
                    user_to_delete = model.user
                    model.user = None
                    model.save()
                    user_to_delete.delete()
                    messages.info(request, _('Cuenta de usuario eliminada exitosamente.'))
                elif manage_user == 'create' and not model.user:
                    # Créer un utilisateur pour le modèle
                    # Générer un username unique
                    username = f"{first_name.lower()}.{last_name.lower()}"
                    base_username = username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1
                    
                    # Générer un mot de passe aléatoire
                    random_password = get_random_string(length=12)
                    
                    # Créer l'utilisateur
                    modele_role = Role.objects.get(name=Role.RoleType.MODELE)
                    user = User.objects.create_user(
                        username=username,
                        email=email if email else f"{username}@dreamslabs.com",
                        password=random_password,
                        role=modele_role,
                        agency=agency
                    )
                    model.user = user
                    model.save()
                    messages.info(request, _('Cuenta de usuario creada exitosamente. El modelo debe cambiar su contraseña al primer inicio de sesión.'))
                
                messages.success(request, _('Modelo actualizado exitosamente.'))
                return redirect('models_app:detail', model_id=model.id)
            except Exception as e:
                messages.error(request, _('Error al actualizar el modelo: {}').format(str(e)))
        else:
            messages.error(request, _('El nombre y apellido son obligatorios.'))
    
    # Préparer le contexte
    if can_edit_agency:
        agencies = Agency.objects.all()
    else:
        agencies = []
    
    context = {
        'model': model,
        'agencies': agencies,
        'can_edit_agency': can_edit_agency,
    }
    return render(request, 'models_app/update.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def model_deactivate(request, model_id):
    """Désactivation d'un modèle"""
    model = get_object_or_404(Model, id=model_id)
    
    # Vérifier les permissions
    if request.user.is_superuser or request.user.is_general_manager():
        # Admin et General Manager peuvent désactiver n'importe quel modèle
        pass
    elif request.user.is_regional_manager():
        # Regional Manager ne peut désactiver que les modèles de son agence
        if model.agency != request.user.agency:
            messages.error(request, _('No tiene acceso a este modelo.'))
            return redirect('models_app:list')
    
    if model.status == Model.Status.INACTIVE:
        messages.warning(request, _('Este modelo ya está desactivado.'))
        return redirect('models_app:detail', model_id=model.id)
    
    if request.method == 'POST':
        try:
            model.deactivate()
            messages.success(request, _('Modelo desactivado exitosamente. Los datos históricos se conservarán.'))
            return redirect('models_app:list')
        except Exception as e:
            messages.error(request, _('Error al desactivar el modelo: {}').format(str(e)))
    
    context = {
        'model': model,
    }
    return render(request, 'models_app/deactivate.html', context)


@login_required
@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
def model_user_reset_password(request, model_id):
    """Réinitialisation du mot de passe de l'utilisateur associé au modèle"""
    model = get_object_or_404(Model, id=model_id)
    
    # Vérifier les permissions
    if request.user.is_general_manager():
        pass
    elif request.user.is_regional_manager() and request.user.agency == model.agency:
        pass
    else:
        messages.error(request, _('No tiene acceso a este modelo.'))
        return redirect('models_app:list')
    
    if not model.user:
        messages.error(request, _('Este modelo no tiene una cuenta de usuario asociada.'))
        return redirect('models_app:detail', model_id=model.id)
    
    if request.method == 'POST':
        try:
            from django.utils.crypto import get_random_string
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Générer un nouveau mot de passe
            new_password = get_random_string(length=12)
            
            # Réinitialiser le mot de passe
            model.user.set_password(new_password)
            model.user.save()
            
            # Stocker temporairement dans la session pour l'afficher
            session_key = f'user_password_{model.user.id}'
            request.session[session_key] = new_password
            
            messages.success(request, _('Contraseña restablecida exitosamente. El nuevo contraseña se mostrará a continuación.'))
            return redirect('models_app:detail', model_id=model.id)
        except Exception as e:
            messages.error(request, _('Error al restablecer la contraseña: {}').format(str(e)))
    
    context = {
        'model': model,
    }
    return render(request, 'models_app/user_reset_password.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def model_reactivate(request, model_id):
    """Réactivation d'un modèle"""
    model = get_object_or_404(Model, id=model_id)
    
    # Vérifier les permissions
    if request.user.is_superuser or request.user.is_general_manager():
        # Admin et General Manager peuvent réactiver n'importe quel modèle
        pass
    elif request.user.is_regional_manager():
        # Regional Manager ne peut réactiver que les modèles de son agence
        if model.agency != request.user.agency:
            messages.error(request, _('No tiene acceso a este modelo.'))
            return redirect('models_app:list')
    
    if model.status == Model.Status.ACTIVE:
        messages.warning(request, _('Este modelo ya está activo.'))
        return redirect('models_app:detail', model_id=model.id)
    
    if request.method == 'POST':
        try:
            model.reactivate()
            messages.success(request, _('Modelo reactivado exitosamente.'))
            return redirect('models_app:detail', model_id=model.id)
        except Exception as e:
            messages.error(request, _('Error al reactivar el modelo: {}').format(str(e)))
    
    context = {
        'model': model,
    }
    return render(request, 'models_app/reactivate.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def gain_create(request, model_id):
    """Création d'un gain pour un modèle"""
    model = get_object_or_404(Model, id=model_id)
    
    # Vérifier les permissions
    if request.user.is_superuser or request.user.is_general_manager():
        # Admin et General Manager peuvent enregistrer des gains pour n'importe quel modèle
        pass
    elif request.user.is_regional_manager():
        # Regional Manager ne peut enregistrer que pour les modèles de son agence
        if model.agency != request.user.agency:
            messages.error(request, _('No tiene acceso a este modelo.'))
            return redirect('models_app:list')
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        amount_str = request.POST.get('amount')
        description = request.POST.get('description', '')
        
        try:
            gain_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(amount_str)
            
            if amount < 0:
                messages.error(request, _('El monto debe ser positivo.'))
            else:
                # Vérifier si un gain existe déjà pour cette date
                existing_gain = ModelGain.objects.filter(model=model, date=gain_date).first()
                if existing_gain:
                    # Mettre à jour le gain existant
                    existing_gain.amount = amount
                    existing_gain.description = description
                    existing_gain.save()
                    messages.success(request, _('Ganancia actualizada exitosamente.'))
                else:
                    # Créer un nouveau gain
                    gain = ModelGain.objects.create(
                        model=model,
                        date=gain_date,
                        amount=amount,
                        description=description,
                        created_by=request.user
                    )
                    messages.success(request, _('Ganancia registrada exitosamente.'))
                
                return redirect('models_app:detail', model_id=model.id)
        except ValueError:
            messages.error(request, _('Error en el formato de la fecha o del monto.'))
        except Exception as e:
            messages.error(request, _('Error al registrar la ganancia: {}').format(str(e)))
    
    # Date par défaut : aujourd'hui
    default_date = timezone.now().date()
    
    context = {
        'model': model,
        'default_date': default_date,
    }
    return render(request, 'models_app/gain_create.html', context)


@role_required(Role.RoleType.REGIONAL_MANAGER, Role.RoleType.GENERAL_MANAGER)
@agency_required
def worked_hours_bulk_create(request):
    """
    Saisie groupée des heures travaillées pour tous les modèles actifs
    """
    # Déterminer l'agence selon le rôle
    agency = None
    if request.user.is_superuser or request.user.is_general_manager():
        # Admin et General Manager peuvent choisir l'agence
        agency_id = request.GET.get('agency') or request.POST.get('agency')
        if agency_id:
            agency = get_object_or_404(Agency, id=agency_id)
        elif request.user.agency:
            agency = request.user.agency
        else:
            # Si pas d'agence sélectionnée, afficher toutes les agences
            agencies = Agency.objects.all()
            if agencies.count() == 1:
                agency = agencies.first()
            else:
                # Si plusieurs agences, on affichera un sélecteur dans le template
                # Pour l'instant, on prend la première agence par défaut
                agency = agencies.first() if agencies.exists() else None
                if not agency:
                    messages.error(request, _('No hay agencias disponibles.'))
                    return redirect('accounts:dashboard')
    elif request.user.is_regional_manager():
        # Regional Manager utilise son agence
        if not request.user.agency:
            messages.error(request, _('No tiene una agencia asignada.'))
            return redirect('accounts:dashboard')
        agency = request.user.agency
    
    if not agency:
        messages.error(request, _('Debe seleccionar una agencia.'))
        return redirect('accounts:dashboard')
    
    # Date par défaut : aujourd'hui
    selected_date = request.GET.get('date', timezone.now().date().isoformat())
    
    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        selected_date = timezone.now().date()
        messages.warning(request, _('Fecha inválida, usando fecha actual.'))
    
    # Récupérer tous les modèles actifs de l'agence selon les dates
    active_models = Model.active_by_dates.filter(
        agency=agency
    ).order_by('first_name', 'last_name')
    
    # Récupérer les heures déjà enregistrées pour cette date
    existing_hours_dict = {}
    for wh in WorkedHours.objects.filter(
        model__agency=agency,
        date=selected_date
    ).select_related('model'):
        existing_hours_dict[wh.model_id] = float(wh.hours)
    
    if request.method == 'POST':
        # Traiter la soumission du formulaire
        success_count = 0
        error_count = 0
        
        for model in active_models:
            hours_key = f"hours_{model.id}"
            hours_value = request.POST.get(hours_key, '').strip()
            
            if hours_value:
                try:
                    hours = float(hours_value)
                    if hours < 0:
                        continue
                    
                    # Vérifier si des heures existent déjà pour ce modèle et cette date
                    existing = WorkedHours.objects.filter(
                        model=model,
                        date=selected_date
                    ).first()
                    
                    if existing:
                        # Mettre à jour
                        existing.hours = hours
                        existing.save()
                    else:
                        # Créer
                        WorkedHours.objects.create(
                            model=model,
                            date=selected_date,
                            hours=hours,
                            created_by=request.user
                        )
                    success_count += 1
                except ValueError:
                    error_count += 1
                    continue
        
        if success_count > 0:
            messages.success(request, _('{} horas registradas exitosamente.').format(success_count))
        if error_count > 0:
            messages.warning(request, _('{} errores al registrar horas.').format(error_count))
        
        return redirect('models_app:worked_hours_bulk_create')
    
    # Pour admin/general manager, récupérer toutes les agences pour le sélecteur
    agencies = None
    can_choose_agency = False
    if request.user.is_superuser or request.user.is_general_manager():
        agencies = Agency.objects.all()
        can_choose_agency = True
    
    context = {
        'active_models': active_models,
        'selected_date': selected_date,
        'existing_hours': existing_hours_dict,
        'agency': agency,
        'agencies': agencies,
        'can_choose_agency': can_choose_agency,
    }
    return render(request, 'models_app/worked_hours_bulk.html', context)
