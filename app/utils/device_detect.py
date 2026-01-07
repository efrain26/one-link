"""
Utilidades para detectar el dispositivo del usuario.
Similar a Build.VERSION y UserAgent en Android.
"""
from user_agents import parse
from typing import Dict


def detect_platform(user_agent_string: str) -> str:
    """
    Detecta la plataforma del dispositivo basándose en el User-Agent.
    
    Args:
        user_agent_string: String del User-Agent del request
        
    Returns:
        'ios', 'android', o 'other'
        
    Ejemplo:
        >>> detect_platform("Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)")
        'ios'
    """
    if not user_agent_string:
        return 'other'
    
    user_agent = parse(user_agent_string)
    
    # Detectar iOS (iPhone, iPad, iPod)
    if user_agent.is_mobile and user_agent.os.family == 'iOS':
        return 'ios'
    
    # Detectar Android
    if user_agent.os.family == 'Android':
        return 'android'
    
    # Todo lo demás (desktop, otros móviles, etc.)
    return 'other'


def get_device_info(user_agent_string: str) -> Dict[str, any]:
    """
    Obtiene información detallada del dispositivo.
    
    Args:
        user_agent_string: String del User-Agent del request
        
    Returns:
        Dictionary con información del dispositivo
        
    Ejemplo:
        >>> info = get_device_info("Mozilla/5.0...")
        >>> print(info['platform'])  # 'ios'
        >>> print(info['device'])    # 'iPhone'
    """
    if not user_agent_string:
        return {
            'platform': 'other',
            'device': 'Unknown',
            'os': 'Unknown',
            'os_version': 'Unknown',
            'browser': 'Unknown',
            'is_mobile': False,
            'is_tablet': False,
            'is_bot': False
        }
    
    user_agent = parse(user_agent_string)
    
    return {
        'platform': detect_platform(user_agent_string),
        'device': user_agent.device.family or 'Unknown',
        'os': user_agent.os.family or 'Unknown',
        'os_version': user_agent.os.version_string or 'Unknown',
        'browser': user_agent.browser.family or 'Unknown',
        'browser_version': user_agent.browser.version_string or 'Unknown',
        'is_mobile': user_agent.is_mobile,
        'is_tablet': user_agent.is_tablet,
        'is_bot': user_agent.is_bot
    }


def is_mobile_device(user_agent_string: str) -> bool:
    """
    Verifica si el dispositivo es móvil.
    
    Returns:
        True si es móvil (iOS o Android), False en caso contrario
    """
    platform = detect_platform(user_agent_string)
    return platform in ['ios', 'android']
