from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import datetime, date, timedelta
from .models import Expense, ExpenseCategory, Employee, Salary, Revenue, RevenueSource
from accounts.decorators import regional_manager_required, agency_required, general_manager_required
from accounts.utils import filter_by_agency_queryset


# ==================== EXPENSES (DÉPENSES) ====================

@login_required
def expense_list(request):
    """Liste des dépenses"""
    if request.user.is_general_manager():
        expenses = Expense.objects.all().order_by('-date', '-created_at')
    elif request.user.is_regional_manager() and request.user.agency:
        expenses = Expense.objects.filter(agency=request.user.agency).order_by('-date', '-created_at')
    else:
        expenses = Expense.objects.none()
        messages.warning(request, _('No tiene acceso a los gastos.'))
    
    # Filtres
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    category_id = request.GET.get('category')
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            expenses = expenses.filter(date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            expenses = expenses.filter(date__lte=date_to)
        except ValueError:
            pass
    
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    
    # Statistiques
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'expenses': expenses,
        'categories': ExpenseCategory.objects.all().order_by('name'),
        'total': total,
        'date_from': date_from,
        'date_to': date_to,
        'selected_category': int(category_id) if category_id else None,
    }
    return render(request, 'financial/expense_list.html', context)


@regional_manager_required
@agency_required
def expense_create(request):
    """Création d'une dépense (Regional Manager ou superuser)"""
    # Pour superuser, permettre de choisir l'agence
    agency = None
    if request.user.is_superuser:
        agency_id = request.POST.get('agency') if request.method == 'POST' else request.GET.get('agency')
        if agency_id:
            from agencies.models import Agency
            agency = get_object_or_404(Agency, id=agency_id)
        elif not request.user.agency:
            # Si superuser sans agence, afficher toutes les agences pour choisir
            from agencies.models import Agency
            agencies = Agency.objects.all()
            context = {
                'agencies': agencies,
                'categories': ExpenseCategory.objects.all().order_by('name'),
                'default_date': timezone.now().date(),
            }
            return render(request, 'financial/expense_create.html', context)
    else:
        agency = request.user.agency
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        amount_str = request.POST.get('amount')
        category_id = request.POST.get('category')
        description = request.POST.get('description', '')
        
        # Pour superuser, toujours récupérer l'agence depuis le formulaire
        if request.user.is_superuser:
            agency_id = request.POST.get('agency')
            if agency_id:
                from agencies.models import Agency
                agency = get_object_or_404(Agency, id=agency_id)
        
        try:
            expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(amount_str)
            category = get_object_or_404(ExpenseCategory, id=category_id)
            
            if amount < 0:
                messages.error(request, _('El monto debe ser positivo.'))
            elif not agency:
                messages.error(request, _('Debe seleccionar una agencia.'))
            else:
                expense = Expense.objects.create(
                    agency=agency,
                    date=expense_date,
                    amount=amount,
                    category=category,
                    description=description,
                    created_by=request.user
                )
                messages.success(request, _('Gasto registrado exitosamente.'))
                return redirect('financial:expense_list')
        except ValueError:
            messages.error(request, _('Error en el formato de la fecha o del monto.'))
        except Exception as e:
            messages.error(request, _('Error al registrar el gasto: {}').format(str(e)))
    
    from agencies.models import Agency
    agencies = Agency.objects.all() if request.user.is_superuser else [request.user.agency] if request.user.agency else []
    
    context = {
        'categories': ExpenseCategory.objects.all().order_by('name'),
        'default_date': timezone.now().date(),
        'agencies': agencies,
        'selected_agency': agency,
    }
    return render(request, 'financial/expense_create.html', context)


@regional_manager_required
@agency_required
def expense_update(request, expense_id):
    """Modification d'une dépense (Regional Manager uniquement)"""
    expense = get_object_or_404(Expense, id=expense_id)
    
    # Vérifier que la dépense appartient à l'agence du Regional Manager (sauf pour superuser)
    if not request.user.is_superuser and expense.agency != request.user.agency:
        messages.error(request, _('No tiene acceso a este gasto.'))
        return redirect('financial:expense_list')
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        amount_str = request.POST.get('amount')
        category_id = request.POST.get('category')
        description = request.POST.get('description', '')
        
        try:
            expense.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            expense.amount = float(amount_str)
            expense.category = get_object_or_404(ExpenseCategory, id=category_id)
            expense.description = description
            
            # Pour superuser, permettre de modifier l'agence
            if request.user.is_superuser:
                agency_id = request.POST.get('agency')
                if agency_id:
                    from agencies.models import Agency
                    expense.agency = get_object_or_404(Agency, id=agency_id)
            
            expense.save()
            messages.success(request, _('Gasto actualizado exitosamente.'))
            return redirect('financial:expense_list')
        except ValueError:
            messages.error(request, _('Error en el formato de la fecha o del monto.'))
        except Exception as e:
            messages.error(request, _('Error al actualizar el gasto: {}').format(str(e)))
    
    from agencies.models import Agency
    agencies = Agency.objects.all() if request.user.is_superuser else [request.user.agency] if request.user.agency else []
    
    context = {
        'expense': expense,
        'categories': ExpenseCategory.objects.all().order_by('name'),
        'agencies': agencies,
    }
    return render(request, 'financial/expense_update.html', context)


@regional_manager_required
@agency_required
def expense_delete(request, expense_id):
    """Suppression d'une dépense (Regional Manager uniquement)"""
    expense = get_object_or_404(Expense, id=expense_id)
    
    # Vérifier que la dépense appartient à l'agence du Regional Manager
    if expense.agency != request.user.agency:
        messages.error(request, _('No tiene acceso a este gasto.'))
        return redirect('financial:expense_list')
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, _('Gasto eliminado exitosamente.'))
        return redirect('financial:expense_list')
    
    context = {
        'expense': expense,
    }
    return render(request, 'financial/expense_delete.html', context)


# ==================== SALARIES (SALAIRES) ====================

@login_required
def salary_list(request):
    """Liste des salaires"""
    if request.user.is_general_manager():
        salaries = Salary.objects.all().order_by('-payment_date', '-created_at')
    elif request.user.is_regional_manager() and request.user.agency:
        salaries = Salary.objects.filter(agency=request.user.agency).order_by('-payment_date', '-created_at')
    else:
        salaries = Salary.objects.none()
        messages.warning(request, _('No tiene acceso a los salarios.'))
    
    # Filtres
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    employee_id = request.GET.get('employee')
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            salaries = salaries.filter(payment_date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            salaries = salaries.filter(payment_date__lte=date_to)
        except ValueError:
            pass
    
    if employee_id:
        salaries = salaries.filter(employee_id=employee_id)
    
    # Statistiques
    total = salaries.aggregate(total=Sum('amount'))['total'] or 0
    
    # Récupérer les employés pour le filtre
    if request.user.is_general_manager():
        employees = Employee.objects.filter(is_active=True).order_by('first_name', 'last_name')
    elif request.user.is_regional_manager() and request.user.agency:
        employees = Employee.objects.filter(agency=request.user.agency, is_active=True).order_by('first_name', 'last_name')
    else:
        employees = Employee.objects.none()
    
    context = {
        'salaries': salaries,
        'employees': employees,
        'total': total,
        'date_from': date_from,
        'date_to': date_to,
        'selected_employee': int(employee_id) if employee_id else None,
    }
    return render(request, 'financial/salary_list.html', context)


@regional_manager_required
@agency_required
def salary_create(request):
    """Création d'un salaire (Regional Manager uniquement)"""
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        payment_date_str = request.POST.get('payment_date')
        period_start_str = request.POST.get('period_start')
        period_end_str = request.POST.get('period_end')
        amount_str = request.POST.get('amount')
        description = request.POST.get('description', '')
        
        try:
            employee = get_object_or_404(Employee, id=employee_id, agency=request.user.agency)
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
            period_start = datetime.strptime(period_start_str, '%Y-%m-%d').date()
            period_end = datetime.strptime(period_end_str, '%Y-%m-%d').date()
            amount = float(amount_str)
            
            if amount < 0:
                messages.error(request, _('El monto debe ser positivo.'))
            else:
                salary = Salary.objects.create(
                    employee=employee,
                    agency=request.user.agency,
                    payment_date=payment_date,
                    period_start=period_start,
                    period_end=period_end,
                    amount=amount,
                    description=description,
                    created_by=request.user
                )
                messages.success(request, _('Salario registrado exitosamente.'))
                return redirect('financial:salary_list')
        except ValueError:
            messages.error(request, _('Error en el formato de la fecha o del monto.'))
        except Exception as e:
            messages.error(request, _('Error al registrar el salario: {}').format(str(e)))
    
    # Récupérer les employés actifs de l'agence
    employees = Employee.objects.filter(
        agency=request.user.agency,
        is_active=True
    ).order_by('first_name', 'last_name')
    
    context = {
        'employees': employees,
        'default_date': timezone.now().date(),
    }
    return render(request, 'financial/salary_create.html', context)


# ==================== REVENUES (REVENUS) ====================

@login_required
def revenue_list(request):
    """Liste des revenus"""
    if request.user.is_general_manager():
        revenues = Revenue.objects.all().order_by('-date', '-created_at')
    elif request.user.is_regional_manager() and request.user.agency:
        revenues = Revenue.objects.filter(agency=request.user.agency).order_by('-date', '-created_at')
    else:
        revenues = Revenue.objects.none()
        messages.warning(request, _('No tiene acceso a los ingresos.'))
    
    # Filtres
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    source_id = request.GET.get('source')
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            revenues = revenues.filter(date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            revenues = revenues.filter(date__lte=date_to)
        except ValueError:
            pass
    
    if source_id:
        revenues = revenues.filter(source_id=source_id)
    
    # Statistiques
    total = revenues.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'revenues': revenues,
        'sources': RevenueSource.objects.all().order_by('name'),
        'total': total,
        'date_from': date_from,
        'date_to': date_to,
        'selected_source': int(source_id) if source_id else None,
    }
    return render(request, 'financial/revenue_list.html', context)


@regional_manager_required
@agency_required
def revenue_create(request):
    """Création d'un revenu (Regional Manager uniquement)"""
    if request.method == 'POST':
        date_str = request.POST.get('date')
        amount_str = request.POST.get('amount')
        source_id = request.POST.get('source')
        description = request.POST.get('description', '')
        
        try:
            revenue_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(amount_str)
            source = get_object_or_404(RevenueSource, id=source_id)
            
            if amount < 0:
                messages.error(request, _('El monto debe ser positivo.'))
            else:
                revenue = Revenue.objects.create(
                    agency=request.user.agency,
                    date=revenue_date,
                    amount=amount,
                    source=source,
                    description=description,
                    created_by=request.user
                )
                messages.success(request, _('Ingreso registrado exitosamente.'))
                return redirect('financial:revenue_list')
        except ValueError:
            messages.error(request, _('Error en el formato de la fecha o del monto.'))
        except Exception as e:
            messages.error(request, _('Error al registrar el ingreso: {}').format(str(e)))
    
    context = {
        'sources': RevenueSource.objects.all().order_by('name'),
        'default_date': timezone.now().date(),
    }
    return render(request, 'financial/revenue_create.html', context)
