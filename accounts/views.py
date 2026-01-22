from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .decorators import role_required, general_manager_required
from .models import Role, User
from financial.models import Expense, Salary, Revenue
from models_app.models import Model, ModelGain, WorkedHours, WorkSession, ScheduleAssignment
from agencies.models import Agency


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, _('Bienvenido, {}').format(user.username))
            return redirect('accounts:dashboard')
        else:
            messages.error(request, _('Usuario o contraseña incorrectos'))
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, _('Sesión cerrada correctamente'))
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """Vue du tableau de bord avec statistiques selon le rôle"""
    context = {
        'user': request.user,
        'user_role': request.user.get_role_display() if request.user.role else 'Sin rol',
        'user_agency': request.user.agency.name if request.user.agency else None,
    }
    
    # Récupérer la période (par défaut : mois en cours)
    period_start = request.GET.get('period_start')
    period_end = request.GET.get('period_end')
    
    if not period_start:
        period_start = timezone.now().replace(day=1).date()
    else:
        try:
            period_start = datetime.strptime(period_start, '%Y-%m-%d').date()
        except ValueError:
            period_start = timezone.now().replace(day=1).date()
    
    if not period_end:
        period_end = timezone.now().date()
    else:
        try:
            period_end = datetime.strptime(period_end, '%Y-%m-%d').date()
        except ValueError:
            period_end = timezone.now().date()
    
    context['period_start'] = period_start
    context['period_end'] = period_end
    
    # Dashboard selon le rôle
    if request.user.role:
        if request.user.is_general_manager():
            # Dashboard General Manager - Vue consolidée des 2 agences
            agencies = Agency.objects.all()
            agencies_data = []
            
            # Calculer les nouveaux indicateurs basés sur WorkSession
            completed_sessions = WorkSession.objects.filter(
                status=WorkSession.Status.COMPLETED,
                date__gte=period_start,
                date__lte=period_end
            )
            
            # Ganancia total (somme de toutes les session_gain_amount)
            total_gain = completed_sessions.aggregate(
                total=Sum('session_gain_amount')
            )['total'] or 0
            
            # Ganancia de los modelos (somme de toutes les session_model_ganancia)
            total_model_gain = completed_sessions.aggregate(
                total=Sum('session_model_ganancia')
            )['total'] or 0
            
            # Impuestos (somme de toutes les session_bank_fees)
            total_bank_fees = completed_sessions.aggregate(
                total=Sum('session_bank_fees')
            )['total'] or 0
            
            # Otros gastos (somme de toutes les Expense)
            total_other_expenses = Expense.objects.filter(
                date__gte=period_start,
                date__lte=period_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Salarios (somme de toutes les Salary)
            total_salaries = Salary.objects.filter(
                payment_date__gte=period_start,
                payment_date__lte=period_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Ganancia de la empresa
            # = Ganancia total - Impuestos - Ganancia de los modelos - Otros gastos - Salarios
            company_gain = total_gain - total_bank_fees - total_model_gain - total_other_expenses - total_salaries
            
            # Données par agence pour le tableau
            for agency in agencies:
                # Sessions complétées de l'agence
                agency_sessions = completed_sessions.filter(model__agency=agency)
                
                agency_gain = agency_sessions.aggregate(
                    total=Sum('session_gain_amount')
                )['total'] or 0
                
                agency_model_gain = agency_sessions.aggregate(
                    total=Sum('session_model_ganancia')
                )['total'] or 0
                
                agency_bank_fees = agency_sessions.aggregate(
                    total=Sum('session_bank_fees')
                )['total'] or 0
                
                agency_other_expenses = Expense.objects.filter(
                    agency=agency,
                    date__gte=period_start,
                    date__lte=period_end
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                agency_salaries = Salary.objects.filter(
                    agency=agency,
                    payment_date__gte=period_start,
                    payment_date__lte=period_end
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                agency_company_gain = agency_gain - agency_bank_fees - agency_model_gain - agency_other_expenses - agency_salaries
                
                agencies_data.append({
                    'agency': agency,
                    'gain': agency_gain,
                    'model_gain': agency_model_gain,
                    'bank_fees': agency_bank_fees,
                    'other_expenses': agency_other_expenses,
                    'salaries': agency_salaries,
                    'company_gain': agency_company_gain,
                    'active_models': Model.active_by_dates.filter(agency=agency).count(),
                })
            
            context.update({
                'agencies_data': agencies_data,
                'total_gain': total_gain,
                'total_model_gain': total_model_gain,
                'total_bank_fees': total_bank_fees,
                'total_other_expenses': total_other_expenses,
                'total_salaries': total_salaries,
                'company_gain': company_gain,
                'total_agencies': agencies.count(),
                'total_active_models': Model.active_by_dates.count(),
            })
            
            return render(request, 'accounts/dashboard_general_manager.html', context)
            
        elif request.user.is_regional_manager() and request.user.agency:
            # Dashboard Regional Manager - Vue de son agence
            agency = request.user.agency
            
            # Dépenses
            expenses = Expense.objects.filter(
                agency=agency,
                date__gte=period_start,
                date__lte=period_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Revenus
            revenues = Revenue.objects.filter(
                agency=agency,
                date__gte=period_start,
                date__lte=period_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Salaires
            salaries = Salary.objects.filter(
                agency=agency,
                payment_date__gte=period_start,
                payment_date__lte=period_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Gains des modèles
            model_gains = ModelGain.objects.filter(
                model__agency=agency,
                date__gte=period_start,
                date__lte=period_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Bilan
            balance = revenues - expenses - salaries
            
            # Statistiques des modèles
            active_models = Model.active_by_dates.filter(agency=agency).count()
            total_worked_hours = WorkedHours.objects.filter(
                model__agency=agency,
                date__gte=period_start,
                date__lte=period_end
            ).aggregate(total=Sum('hours'))['total'] or 0
            
            # Dernières dépenses
            recent_expenses = Expense.objects.filter(agency=agency).order_by('-date')[:5]
            
            # Derniers revenus
            recent_revenues = Revenue.objects.filter(agency=agency).order_by('-date')[:5]
            
            # Liste des modèles qui travaillent aujourd'hui (ou date sélectionnée)
            working_date_str = request.GET.get('working_date')
            if working_date_str:
                try:
                    working_date = datetime.strptime(working_date_str, '%Y-%m-%d').date()
                except ValueError:
                    working_date = timezone.now().date()
            else:
                working_date = timezone.now().date()
            
            # Récupérer les sessions de travail pour cette date
            work_sessions = WorkSession.objects.filter(
                model__agency=agency,
                date=working_date
            ).select_related('model', 'schedule_assignment', 'schedule_assignment__schedule').order_by('model__first_name', 'model__last_name')
            
            # Récupérer les modèles uniques qui travaillent ce jour
            working_models = Model.objects.filter(
                id__in=work_sessions.values_list('model_id', flat=True).distinct()
            ).order_by('first_name', 'last_name')
            
            # Préparer les données des modèles avec leurs sessions
            working_models_data = []
            for model in working_models:
                model_sessions = work_sessions.filter(model=model)
                working_models_data.append({
                    'model': model,
                    'sessions': model_sessions,
                    'sessions_count': model_sessions.count(),
                })
            
            context.update({
                'agency': agency,
                'expenses': expenses,
                'revenues': revenues,
                'salaries': salaries,
                'model_gains': model_gains,
                'balance': balance,
                'active_models': active_models,
                'total_worked_hours': total_worked_hours,
                'recent_expenses': recent_expenses,
                'recent_revenues': recent_revenues,
                'working_date': working_date,
                'working_models_data': working_models_data,
            })
            
            return render(request, 'accounts/dashboard_regional_manager.html', context)
            
        elif request.user.is_modele():
            # Dashboard Modèle - Vue personnelle
            # Trouver le modèle associé à l'utilisateur
            try:
                model = Model.objects.get(user=request.user)
            except Model.DoesNotExist:
                messages.warning(request, _('No tiene un perfil de modelo asociado.'))
                return render(request, 'accounts/dashboard.html', context)
            
            # Gains du modèle
            total_gains = ModelGain.objects.filter(
                model=model,
                date__gte=period_start,
                date__lte=period_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Heures travaillées
            total_hours = WorkedHours.objects.filter(
                model=model,
                date__gte=period_start,
                date__lte=period_end
            ).aggregate(total=Sum('hours'))['total'] or 0
            
            avg_hours = WorkedHours.objects.filter(
                model=model,
                date__gte=period_start,
                date__lte=period_end
            ).aggregate(avg=Avg('hours'))['avg'] or 0
            
            # Derniers gains
            recent_gains = ModelGain.objects.filter(model=model).order_by('-date')[:10]
            
            # Dernières heures travaillées
            recent_hours = WorkedHours.objects.filter(model=model).order_by('-date')[:10]
            
            # Horarios asignados
            schedule_assignments = ScheduleAssignment.objects.filter(
                model=model
            ).select_related('schedule').order_by('schedule__start_time')
            
            context.update({
                'model': model,
                'total_gains': total_gains,
                'total_hours': total_hours,
                'avg_hours': avg_hours,
                'recent_gains': recent_gains,
                'recent_hours': recent_hours,
                'schedule_assignments': schedule_assignments,
            })
            
            return render(request, 'accounts/dashboard_modele.html', context)
    
    return render(request, 'accounts/dashboard.html', context)


# ==================== USER MANAGEMENT ====================

@login_required
@general_manager_required
def user_list(request):
    """Liste des utilisateurs (seulement pour superuser et general_manager)"""
    users = User.objects.all().select_related('role', 'agency').order_by('-date_joined')
    
    # Filtres
    role_filter = request.GET.get('role')
    agency_filter = request.GET.get('agency')
    is_active_filter = request.GET.get('is_active')
    
    if role_filter:
        users = users.filter(role__name=role_filter)
    
    if agency_filter:
        users = users.filter(agency_id=agency_filter)
    
    if is_active_filter == 'true':
        users = users.filter(is_active=True)
    elif is_active_filter == 'false':
        users = users.filter(is_active=False)
    
    # Statistiques
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    
    # Rôles et agences pour les filtres
    roles = Role.objects.all()
    agencies = Agency.objects.all()
    
    context = {
        'users': users,
        'roles': roles,
        'agencies': agencies,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'role_filter': role_filter,
        'agency_filter': agency_filter,
        'is_active_filter': is_active_filter,
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
@general_manager_required
def user_create(request):
    """Création d'un utilisateur"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        role_id = request.POST.get('role')
        agency_id = request.POST.get('agency', '')
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not username or not password:
            messages.error(request, _('El nombre de usuario y la contraseña son obligatorios.'))
        elif password != password_confirm:
            messages.error(request, _('Las contraseñas no coinciden.'))
        elif User.objects.filter(username=username).exists():
            messages.error(request, _('El nombre de usuario ya existe.'))
        elif email and User.objects.filter(email=email).exists():
            messages.error(request, _('El correo electrónico ya está en uso.'))
        else:
            try:
                role = None
                if role_id:
                    role = get_object_or_404(Role, id=role_id)
                
                agency = None
                if agency_id:
                    agency = get_object_or_404(Agency, id=agency_id)
                
                user = User.objects.create_user(
                    username=username,
                    email=email if email else None,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    role=role,
                    agency=agency,
                    is_staff=is_staff,
                    is_active=is_active
                )
                messages.success(request, _('Usuario creado exitosamente.'))
                return redirect('accounts:user_list')
            except Exception as e:
                messages.error(request, _('Error al crear el usuario: {}').format(str(e)))
    
    roles = Role.objects.all()
    agencies = Agency.objects.all()
    
    context = {
        'roles': roles,
        'agencies': agencies,
    }
    return render(request, 'accounts/user_create.html', context)


@login_required
@general_manager_required
def user_update(request, user_id):
    """Modification d'un utilisateur"""
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        role_id = request.POST.get('role')
        agency_id = request.POST.get('agency', '')
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not username:
            messages.error(request, _('El nombre de usuario es obligatorio.'))
        elif password and password != password_confirm:
            messages.error(request, _('Las contraseñas no coinciden.'))
        elif User.objects.filter(username=username).exclude(id=target_user.id).exists():
            messages.error(request, _('El nombre de usuario ya existe.'))
        elif email and User.objects.filter(email=email).exclude(id=target_user.id).exists():
            messages.error(request, _('El correo electrónico ya está en uso.'))
        else:
            try:
                # Mettre à jour les champs de base
                target_user.username = username
                target_user.email = email if email else None
                target_user.first_name = first_name
                target_user.last_name = last_name
                target_user.phone = phone
                target_user.is_staff = is_staff
                target_user.is_active = is_active
                
                # Mettre à jour le mot de passe si fourni
                if password:
                    target_user.set_password(password)
                
                # Mettre à jour le rôle
                if role_id:
                    role = get_object_or_404(Role, id=role_id)
                    target_user.role = role
                else:
                    target_user.role = None
                
                # Mettre à jour l'agence
                if agency_id:
                    agency = get_object_or_404(Agency, id=agency_id)
                    target_user.agency = agency
                else:
                    target_user.agency = None
                
                target_user.save()
                messages.success(request, _('Usuario actualizado exitosamente.'))
                return redirect('accounts:user_list')
            except Exception as e:
                messages.error(request, _('Error al actualizar el usuario: {}').format(str(e)))
    
    roles = Role.objects.all()
    agencies = Agency.objects.all()
    
    context = {
        'target_user': target_user,
        'roles': roles,
        'agencies': agencies,
    }
    return render(request, 'accounts/user_update.html', context)


@login_required
@general_manager_required
def user_deactivate(request, user_id):
    """Désactivation d'un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    
    # Ne pas permettre de désactiver soi-même
    if user == request.user:
        messages.error(request, _('No puede desactivar su propia cuenta.'))
        return redirect('accounts:user_list')
    
    if request.method == 'POST':
        user.is_active = False
        user.save()
        messages.success(request, _('Usuario desactivado exitosamente.'))
        return redirect('accounts:user_list')
    
    context = {
        'target_user': user,
    }
    return render(request, 'accounts/user_deactivate.html', context)


@login_required
@general_manager_required
def user_activate(request, user_id):
    """Activation d'un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_active = True
        user.save()
        messages.success(request, _('Usuario activado exitosamente.'))
        return redirect('accounts:user_list')
    
    context = {
        'target_user': user,
    }
    return render(request, 'accounts/user_activate.html', context)


@login_required
@general_manager_required
def user_delete(request, user_id):
    """Suppression d'un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    
    # Ne pas permettre de supprimer soi-même
    if user == request.user:
        messages.error(request, _('No puede eliminar su propia cuenta.'))
        return redirect('accounts:user_list')
    
    # Vérifier si l'utilisateur est lié à un modèle
    if hasattr(user, 'model_profile'):
        messages.error(request, _('No se puede eliminar este usuario porque está asociado a un modelo. Desactive el modelo primero.'))
        return redirect('accounts:user_list')
    
    if request.method == 'POST':
        try:
            user.delete()
            messages.success(request, _('Usuario eliminado exitosamente.'))
            return redirect('accounts:user_list')
        except Exception as e:
            messages.error(request, _('Error al eliminar el usuario: {}').format(str(e)))
    
    context = {
        'target_user': user,
    }
    return render(request, 'accounts/user_delete.html', context)
