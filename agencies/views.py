from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import Agency
from models_app.models import Model
from accounts.decorators import general_manager_required, regional_manager_required
from accounts.utils import filter_by_agency_queryset


@login_required
def agency_list(request):
    """
    Liste des agences
    - General Manager : voit toutes les agences
    - Regional Manager : voit uniquement son agence
    """
    if request.user.is_general_manager():
        agencies = Agency.objects.filter(is_active=True).order_by('name')
    elif request.user.is_regional_manager() and request.user.agency:
        agencies = Agency.objects.filter(id=request.user.agency.id, is_active=True)
    else:
        agencies = Agency.objects.none()
        messages.warning(request, _('No tiene acceso a las agencias.'))
    
    context = {
        'agencies': agencies,
    }
    return render(request, 'agencies/list.html', context)


@login_required
def agency_detail(request, agency_id):
    """
    Détails d'une agence
    - General Manager : peut voir toutes les agences
    - Regional Manager : peut voir uniquement son agence
    """
    agency = get_object_or_404(Agency, id=agency_id, is_active=True)
    
    # Vérifier les permissions
    if request.user.is_general_manager():
        # General Manager peut tout voir
        pass
    elif request.user.is_regional_manager() and request.user.agency == agency:
        # Regional Manager peut voir son agence
        pass
    else:
        messages.error(request, _('No tiene acceso a esta agencia.'))
        return redirect('agencies:list')
    
    # Récupérer les modèles de l'agence
    models = Model.objects.filter(agency=agency).order_by('-created_at')
    active_models = models.filter(status=Model.Status.ACTIVE)
    inactive_models = models.filter(status=Model.Status.INACTIVE)
    
    context = {
        'agency': agency,
        'models': models,
        'active_models': active_models,
        'inactive_models': inactive_models,
        'models_count': models.count(),
        'active_models_count': active_models.count(),
        'inactive_models_count': inactive_models.count(),
    }
    return render(request, 'agencies/detail.html', context)


@general_manager_required
def agency_create(request):
    """Création d'une agence (General Manager uniquement)"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        
        if name and code:
            try:
                # Paramètres financiers
                model_gain_percentage = request.POST.get('model_gain_percentage', '0')
                bank_fee_percentage = request.POST.get('bank_fee_percentage', '0')
                try:
                    model_gain_percentage = float(model_gain_percentage) if model_gain_percentage else 0
                    bank_fee_percentage = float(bank_fee_percentage) if bank_fee_percentage else 0
                except (ValueError, TypeError):
                    model_gain_percentage = 0
                    bank_fee_percentage = 0
                
                # Paramètres d'amendes
                late_penalty = request.POST.get('late_penalty', '0')
                absence_penalty = request.POST.get('absence_penalty', '0')
                try:
                    late_penalty = float(late_penalty) if late_penalty else 0
                    absence_penalty = float(absence_penalty) if absence_penalty else 0
                except (ValueError, TypeError):
                    late_penalty = 0
                    absence_penalty = 0
                
                agency = Agency.objects.create(
                    name=name,
                    code=code,
                    address=address,
                    phone=phone,
                    email=email,
                    model_gain_percentage=model_gain_percentage,
                    bank_fee_percentage=bank_fee_percentage,
                    late_penalty=late_penalty,
                    absence_penalty=absence_penalty,
                    is_active=True
                )
                messages.success(request, _('Agencia creada exitosamente.'))
                return redirect('agencies:detail', agency_id=agency.id)
            except Exception as e:
                messages.error(request, _('Error al crear la agencia: {}').format(str(e)))
        else:
            messages.error(request, _('El nombre y el código son obligatorios.'))
    
    return render(request, 'agencies/create.html')


@general_manager_required
def agency_update(request, agency_id):
    """Modification d'une agence (General Manager uniquement)"""
    agency = get_object_or_404(Agency, id=agency_id)
    
    if request.method == 'POST':
        agency.name = request.POST.get('name', agency.name)
        agency.code = request.POST.get('code', agency.code)
        agency.address = request.POST.get('address', agency.address)
        agency.phone = request.POST.get('phone', agency.phone)
        agency.email = request.POST.get('email', agency.email)
        agency.is_active = request.POST.get('is_active') == 'on'
        
        # Paramètres financiers
        model_gain_percentage = request.POST.get('model_gain_percentage', '0')
        bank_fee_percentage = request.POST.get('bank_fee_percentage', '0')
        try:
            agency.model_gain_percentage = float(model_gain_percentage) if model_gain_percentage else 0
            agency.bank_fee_percentage = float(bank_fee_percentage) if bank_fee_percentage else 0
        except (ValueError, TypeError):
            agency.model_gain_percentage = 0
            agency.bank_fee_percentage = 0
        
        # Paramètres d'amendes
        late_penalty = request.POST.get('late_penalty', '0')
        absence_penalty = request.POST.get('absence_penalty', '0')
        try:
            agency.late_penalty = float(late_penalty) if late_penalty else 0
            agency.absence_penalty = float(absence_penalty) if absence_penalty else 0
        except (ValueError, TypeError):
            agency.late_penalty = 0
            agency.absence_penalty = 0
        
        try:
            agency.save()
            messages.success(request, _('Agencia actualizada exitosamente.'))
            return redirect('agencies:detail', agency_id=agency.id)
        except Exception as e:
            messages.error(request, _('Error al actualizar la agencia: {}').format(str(e)))
    
    context = {
        'agency': agency,
    }
    return render(request, 'agencies/update.html', context)
