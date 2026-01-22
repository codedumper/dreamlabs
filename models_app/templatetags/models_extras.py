from django import template
from datetime import timedelta

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Filtre pour récupérer un élément d'un dictionnaire dans les templates"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def hours_to_hhmm(hours):
    """Convertit des heures décimales en format HH:MM:SS"""
    if hours is None:
        return "-"
    
    try:
        hours = float(hours)
        total_seconds = int(hours * 3600)
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    except (ValueError, TypeError):
        return "-"


@register.filter
def filter_pause_type(pauses, pause_type):
    """Filtre les pauses par type"""
    if not pauses:
        return []
    return [pause for pause in pauses if pause.pause_type == pause_type]


@register.filter
def duration_to_hhmm(duration):
    """Convertit une durée (timedelta) en format HH:MM"""
    if duration is None:
        return ""
    
    try:
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    except (AttributeError, TypeError):
        return ""
