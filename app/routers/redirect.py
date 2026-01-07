"""
Router para redirección - MVP VERSION
¡Este es el corazón del sistema!

Endpoint principal: /{short_code}
Detecta el dispositivo y redirige a la store correcta.
"""
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Depends

from ..database import get_db
from ..models import Project
from ..utils.device_detect import detect_platform, get_device_info

router = APIRouter()


@router.get("/{short_code}")
async def redirect_to_store(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint principal de redirección.
    
    Este es EL endpoint más importante del sistema.
    
    Flujo:
    1. Busca el proyecto por short_code
    2. Detecta la plataforma del usuario (iOS/Android/Other)
    3. Redirige a la URL correcta
    
    Args:
        short_code: Código corto único (ej: "xK9mP2")
        request: Request de FastAPI para obtener headers
    
    Returns:
        RedirectResponse: Redirección 307 (Temporary) a la store correcta
    
    Example:
        GET /xK9mP2 desde iPhone → Redirige a App Store
        GET /xK9mP2 desde Android → Redirige a Play Store
    """
    
    # 1. Buscar el proyecto por short_code
    project = db.query(Project).filter(
        Project.short_code == short_code
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link no encontrado: /{short_code}"
        )
    
    # 2. Detectar plataforma del usuario desde User-Agent
    user_agent = request.headers.get("user-agent", "")
    platform = detect_platform(user_agent)
    
    # 3. Obtener info adicional del dispositivo (opcional, para logs)
    device_info = get_device_info(user_agent)
    
    # Para debugging (puedes comentar esto en producción)
    print(f"""
    🔄 REDIRECT:
      Short Code: {short_code}
      App: {project.app_name}
      Platform: {platform}
      Device: {device_info['device']}
      OS: {device_info['os']} {device_info['os_version']}
      Browser: {device_info['browser']}
    """)
    
    # 4. Determinar URL de redirección según plataforma
    if platform == 'ios':
        redirect_url = project.ios_url
    elif platform == 'android':
        redirect_url = project.android_url
    else:
        # Desktop u otros dispositivos
        redirect_url = project.fallback_url or project.android_url
    
    # 5. Redirigir
    # status_code=307 mantiene el método HTTP (importante para algunos casos)
    # También puedes usar 302 (Found) o 303 (See Other)
    return RedirectResponse(
        url=redirect_url,
        status_code=307  # Temporary Redirect
    )


@router.get("/info/{short_code}")
async def get_redirect_info(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint para ver info de redirección SIN redirigir.
    Útil para debugging y testing.
    
    Returns:
        JSON con info sobre dónde redirigiría
    """
    project = db.query(Project).filter(
        Project.short_code == short_code
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link no encontrado: /{short_code}"
        )
    
    user_agent = request.headers.get("user-agent", "")
    platform = detect_platform(user_agent)
    device_info = get_device_info(user_agent)
    
    # Determinar URL
    if platform == 'ios':
        redirect_url = project.ios_url
    elif platform == 'android':
        redirect_url = project.android_url
    else:
        redirect_url = project.fallback_url or project.android_url
    
    return {
        "short_code": short_code,
        "app_name": project.app_name,
        "detected_platform": platform,
        "device_info": device_info,
        "would_redirect_to": redirect_url,
        "available_urls": {
            "ios": project.ios_url,
            "android": project.android_url,
            "fallback": project.fallback_url
        }
    }
