from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Max
import json
from decimal import Decimal
from .models import Agency, BonusRule
from accounts.decorators import general_manager_required
from accounts.utils import filter_by_agency_queryset


@general_manager_required
def bonus_rule_list(request, agency_id):
    """Liste des règles de bonus pour une agence"""
    agency = get_object_or_404(Agency, id=agency_id)
    
    bonus_rules = BonusRule.objects.filter(agency=agency).order_by('order', 'period_type', '-created_at')
    
    context = {
        'agency': agency,
        'bonus_rules': bonus_rules,
    }
    return render(request, 'agencies/bonus_rule_list.html', context)


@general_manager_required
def bonus_rule_create(request, agency_id):
    """Création d'une règle de bonus"""
    agency = get_object_or_404(Agency, id=agency_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        period_type = request.POST.get('period_type')
        target_currency = request.POST.get('target_currency', BonusRule.TargetCurrency.COP)
        target_amount = request.POST.get('target_amount', '0')
        bonus_type = request.POST.get('bonus_type')
        bonus_value = request.POST.get('bonus_value', '0')
        is_active = request.POST.get('is_active') == 'on'
        stop_on_match = request.POST.get('stop_on_match') == 'on'
        
        if name and period_type and bonus_type:
            try:
                target_amount = Decimal(target_amount) if target_amount else Decimal('0')
                bonus_value = Decimal(bonus_value) if bonus_value else Decimal('0')
                
                # Assigner automatiquement le prochain ordre disponible
                current_max_order = BonusRule.objects.filter(agency=agency).aggregate(
                    max_order=Max('order')
                )['max_order']
                order = (current_max_order + 1) if current_max_order is not None else 0
                
                bonus_rule = BonusRule.objects.create(
                    agency=agency,
                    name=name,
                    period_type=period_type,
                    target_currency=target_currency,
                    target_amount=target_amount,
                    bonus_type=bonus_type,
                    bonus_value=bonus_value,
                    is_active=is_active,
                    order=order,
                    stop_on_match=stop_on_match
                )
                messages.success(request, _('Regla de bonus creada exitosamente.'))
                return redirect('agencies:bonus_rule_list', agency_id=agency.id)
            except Exception as e:
                messages.error(request, _('Error al crear la regla de bonus: {}').format(str(e)))
        else:
            messages.error(request, _('Todos los campos son obligatorios.'))
    
    context = {
        'agency': agency,
    }
    return render(request, 'agencies/bonus_rule_create.html', context)


@general_manager_required
def bonus_rule_update(request, agency_id, rule_id):
    """Modification d'une règle de bonus"""
    agency = get_object_or_404(Agency, id=agency_id)
    bonus_rule = get_object_or_404(BonusRule, id=rule_id, agency=agency)
    
    if request.method == 'POST':
        bonus_rule.name = request.POST.get('name', bonus_rule.name)
        bonus_rule.period_type = request.POST.get('period_type', bonus_rule.period_type)
        bonus_rule.target_currency = request.POST.get('target_currency', bonus_rule.target_currency)
        bonus_rule.bonus_type = request.POST.get('bonus_type', bonus_rule.bonus_type)
        bonus_rule.is_active = request.POST.get('is_active') == 'on'
        bonus_rule.stop_on_match = request.POST.get('stop_on_match') == 'on'
        
        target_amount = request.POST.get('target_amount', '0')
        bonus_value = request.POST.get('bonus_value', '0')
        try:
            bonus_rule.target_amount = Decimal(target_amount) if target_amount else Decimal('0')
            bonus_rule.bonus_value = Decimal(bonus_value) if bonus_value else Decimal('0')
            # L'ordre n'est pas modifiable via le formulaire, seulement via drag and drop
        except (ValueError, TypeError):
            messages.error(request, _('Error en el formato de los valores numéricos.'))
            context = {
                'agency': agency,
                'bonus_rule': bonus_rule,
            }
            return render(request, 'agencies/bonus_rule_update.html', context)
        
        try:
            bonus_rule.save()
            messages.success(request, _('Regla de bonus actualizada exitosamente.'))
            return redirect('agencies:bonus_rule_list', agency_id=agency.id)
        except Exception as e:
            messages.error(request, _('Error al actualizar la regla de bonus: {}').format(str(e)))
    
    context = {
        'agency': agency,
        'bonus_rule': bonus_rule,
    }
    return render(request, 'agencies/bonus_rule_update.html', context)


@general_manager_required
def bonus_rule_delete(request, agency_id, rule_id):
    """Suppression d'une règle de bonus"""
    agency = get_object_or_404(Agency, id=agency_id)
    bonus_rule = get_object_or_404(BonusRule, id=rule_id, agency=agency)
    
    if request.method == 'POST':
        # Sauvegarder l'ordre de la règle avant suppression
        deleted_order = bonus_rule.order
        
        # Supprimer la règle
        bonus_rule.delete()
        
        # Réordonner toutes les règles restantes qui avaient un ordre supérieur
        remaining_rules = BonusRule.objects.filter(
            agency=agency,
            order__gt=deleted_order
        ).order_by('order')
        
        # Réassigner les ordres de manière séquentielle
        for index, rule in enumerate(remaining_rules, start=deleted_order):
            rule.order = index
            rule.save(update_fields=['order'])
        
        messages.success(request, _('Regla de bonus eliminada exitosamente.'))
        return redirect('agencies:bonus_rule_list', agency_id=agency.id)
    
    context = {
        'agency': agency,
        'bonus_rule': bonus_rule,
    }
    return render(request, 'agencies/bonus_rule_delete.html', context)


@general_manager_required
@require_http_methods(["POST"])
def bonus_rule_reorder(request, agency_id):
    """Mise à jour de l'ordre des règles de bonus via AJAX"""
    agency = get_object_or_404(Agency, id=agency_id)
    
    try:
        data = json.loads(request.body)
        rule_orders = data.get('orders', [])  # Liste de [rule_id, new_order]
        
        # Mettre à jour l'ordre de chaque règle
        for rule_id, new_order in rule_orders:
            try:
                rule = BonusRule.objects.get(id=rule_id, agency=agency)
                rule.order = int(new_order)
                rule.save(update_fields=['order'])
            except BonusRule.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'Regla {rule_id} no encontrada'}, status=404)
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': f'Orden inválido para regla {rule_id}'}, status=400)
        
        return JsonResponse({'success': True, 'message': 'Orden actualizado exitosamente'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
