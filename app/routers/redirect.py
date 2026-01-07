"""
Router de redirección - EL MÁS IMPORTANTE.
Este es el endpoint que hace la magia: /{short_code}
Detecta el dispositivo y redirige a la store correcta.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models import Project, Click
from ..utils.device_detect import detect_platform, get_device_info
from ..utils.short_url import hash_ip

router = APIRouter(tags=["Redirect"])


@router.get("/{short_code}")
async def redirect_to_store(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint principal de redirección.
    
    Este es el que se usa en los SMS/links compartidos.
    Ejemplo: https://tudominio.com/aBc123
    
    Flujo:
    1. Busca el proyecto por short_code
    2. Detecta la plataforma del usuario (iOS/Android/Other)
    3. Registra el click en analytics
    4. Redirige a la store correspondiente
    
    Args:
        short_code: Código corto del proyecto (ej: 'aBc123')
        request: FastAPI Request object (para obtener headers)
        db: Database session
    
    Returns:
        RedirectResponse a la store correspondiente (307 Temporary Redirect)
    
    Raises:
        404: Si el short_code no existe
    """
    
    # 1. Buscar el proyecto
    project = db.query(Project).filter(
        Project.short_code == short_code
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link not found: {short_code}"
        )
    
    # 2. Detectar plataforma del usuario
    user_agent = request.headers.get("user-agent", "")
    platform = detect_platform(user_agent)
    device_info = get_device_info(user_agent)
    
    # 3. Obtener IP (para analytics y geolocalización)
    # En producción con proxy/load balancer, usar X-Forwarded-For
    client_ip = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    # 4. Registrar click en analytics
    click = Click(
        project_id=project.id,
        platform=platform,
        device_type=device_info.get('device', 'Unknown'),
        browser=device_info.get('browser', 'Unknown'),
        os_version=device_info.get('os_version', 'Unknown'),
        country="Unknown",  # TODO: Agregar GeoIP lookup
        city=None,
        ip_hash=hash_ip(client_ip),
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
    
    # 6. Redirigir (307 = Temporary Redirect, mantiene método HTTP)
    return RedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
