"""
Router de redirección - El corazón del sistema.
Este endpoint maneja las redirecciones a las stores.
"""
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime

from ..database import get_db
from ..models import Project, Click
from ..utils.device_detect import detect_platform, get_device_info
from ..utils.short_url import hash_ip

router = APIRouter(tags=["redirect"])


@router.get("/{short_code}")
async def redirect_to_store(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint principal de redirección.
    
    Este es el endpoint que se comparte con los usuarios.
    Ejemplo: https://tudominio.com/aBc123
    
    Flujo:
    1. Buscar proyecto por short_code
    2. Detectar plataforma del usuario (iOS/Android/Other)
    3. Registrar click en analytics
    4. Redirigir a la store correcta
    
    Similar a un DeepLink handler en Android.
    """
    
    # 1. Buscar el proyecto por short_code
    project = db.query(Project).filter(
        Project.short_code == short_code
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found. Please check the URL."
        )
    
    # 2. Detectar plataforma del usuario
    user_agent = request.headers.get("user-agent", "")
    platform = detect_platform(user_agent)
    device_info = get_device_info(user_agent)
    
    # 3. Obtener IP del cliente (para analytics)
    client_ip = request.client.host if request.client else "unknown"
    ip_hashed = hash_ip(client_ip)
    
    # 4. Registrar el click en analytics
    click = Click(
        project_id=project.id,
        platform=platform,
        device_type=device_info.get('device', 'Unknown'),
        browser=device_info.get('browser', 'Unknown'),
        os_version=device_info.get('os_version', 'Unknown'),
        country="Unknown",  # Puedes agregar GeoIP aquí más tarde
        ip_hash=ip_hashed,
        timestamp=datetime.utcnow()
    )
    
    db.add(click)
    db.commit()
    
    # 5. Determinar URL de redirección según plataforma
    if platform == 'ios':
        redirect_url = project.ios_url
    elif platform == 'android':
        redirect_url = project.android_url
    else:
        # Desktop u otros dispositivos
        redirect_url = project.fallback_url or project.android_url
    
    # 6. Redirigir al usuario
    # 307: Temporary Redirect (mantiene el método HTTP)
    return RedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )


@router.get("/{short_code}/preview")
async def preview_link(
    short_code: str,
    db: Session = Depends(get_db)
):
    """
    Preview de un link sin redirigir.
    Útil para ver a dónde apunta un link antes de hacer click.
    
    Ejemplo: GET /aBc123/preview
    """
    project = db.query(Project).filter(
        Project.short_code == short_code
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    return {
        "short_code": short_code,
        "app_name": project.app_name,
        "destinations": {
            "ios": project.ios_url,
            "android": project.android_url,
            "fallback": project.fallback_url
        }
    }
