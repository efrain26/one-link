"""
Utilidades para generar URLs cortas únicas.
"""
import shortuuid
import hashlib
from typing import Optional


def generate_short_code(length: int = 6) -> str:
    """
    Genera un código corto único para URLs.
    
    Args:
        length: Longitud del código (default: 6)
        
    Returns:
        String único como 'aBc123'
        
    Ejemplo:
        >>> code = generate_short_code()
        >>> print(code)  # 'xK9mP2'
    """
    return shortuuid.ShortUUID().random(length=length)


def generate_short_url(base_url: str, short_code: str) -> str:
    """
    Genera la URL completa combinando base + código.
    
    Args:
        base_url: URL base (ej: 'https://onelink.app')
        short_code: Código corto (ej: 'aBc123')
        
    Returns:
        URL completa (ej: 'https://onelink.app/aBc123')
        
    Ejemplo:
        >>> url = generate_short_url('https://onelink.app', 'xK9mP2')
        >>> print(url)  # 'https://onelink.app/xK9mP2'
    """
    # Remover trailing slash de base_url si existe
    base_url = base_url.rstrip('/')
    return f"{base_url}/{short_code}"


def hash_ip(ip_address: str) -> str:
    """
    Hashea una dirección IP para privacidad.
    No guardamos IPs reales, solo hash para analytics.
    
    Args:
        ip_address: Dirección IP (ej: '192.168.1.1')
        
    Returns:
        Hash SHA-256 de la IP
        
    Ejemplo:
        >>> hashed = hash_ip('192.168.1.1')
        >>> print(len(hashed))  # 64 (SHA-256 en hex)
    """
    return hashlib.sha256(ip_address.encode()).hexdigest()


def validate_url(url: str) -> bool:
    """
    Valida que una URL tenga formato correcto.
    
    Args:
        url: URL a validar
        
    Returns:
        True si es válida, False en caso contrario
    """
    if not url:
        return False
    
    # Validación básica
    valid_prefixes = ['http://', 'https://']
    return any(url.startswith(prefix) for prefix in valid_prefixes)
