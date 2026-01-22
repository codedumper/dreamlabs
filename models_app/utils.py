"""
Utilitaire pour la conversion USD vers COP en utilisant le TRM (Tasa Representativa del Mercado)
"""
from suds.client import Client
from decimal import Decimal
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

WSDL_URL = 'https://www.superfinanciera.gov.co/SuperfinancieraWebServiceTRM/TCRMServicesWebService/TCRMServicesWebService?WSDL'


def get_trm_rate(date_obj):
    """
    Récupère la valeur TRM (Tasa Representativa del Mercado) pour une date donnée.
    
    Args:
        date_obj (date): Date pour laquelle récupérer le TRM
    
    Returns:
        Decimal: Taux de change USD/COP ou None en cas d'erreur
    """
    try:
        # Convertir la date en format string YYYY-MM-DD
        date_str = date_obj.strftime('%Y-%m-%d')
        
        client = Client(WSDL_URL, location=WSDL_URL, faults=True)
        result = client.service.queryTCRM(date_str)
        
        # Extraire la valeur du TRM
        if hasattr(result, 'value'):
            value = result.value
        elif hasattr(result, 'Value'):
            value = result.Value
        else:
            logger.error(f"Format de réponse TRM inattendu pour la date {date_str}")
            return None
        
        return Decimal(str(value))
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la TRM pour {date_obj}: {str(e)}")
        return None


def convert_usd_to_cop(usd_amount, date_obj=None):
    """
    Convertit un montant USD en COP en utilisant le TRM.
    
    Args:
        usd_amount (Decimal ou float): Montant en USD
        date_obj (date, optional): Date pour le TRM. Si None, utilise la date actuelle.
    
    Returns:
        tuple: (montant_cop, taux_trm) ou (None, None) en cas d'erreur
    """
    if date_obj is None:
        date_obj = date.today()
    
    trm_rate = get_trm_rate(date_obj)
    
    if trm_rate is None:
        return None, None
    
    usd_decimal = Decimal(str(usd_amount))
    cop_amount = usd_decimal * trm_rate
    
    return cop_amount, trm_rate
