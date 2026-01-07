"""
Schemas Pydantic para validación de datos - MVP VERSION
Solo Projects, sin Users ni Analytics.
"""
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional


# ============= PROJECT SCHEMAS =============

class ProjectCreate(BaseModel):
    """
    Schema para crear un proyecto.
    El usuario solo necesita proveer estos 3 campos.
    """
    app_name: str = Field(..., min_length=1, max_length=100, description="Nombre de la app")
    ios_url: HttpUrl = Field(..., description="URL del App Store")
    android_url: HttpUrl = Field(..., description="URL del Play Store")
    fallback_url: Optional[HttpUrl] = Field(None, description="URL para desktop/otros (opcional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "app_name": "Bait App",
                "ios_url": "https://apps.apple.com/app/id123456789",
                "android_url": "https://play.google.com/store/apps/details?id=com.ordenaris.bait",
                "fallback_url": "https://www.ordenaris.com"
            }
        }


class ProjectResponse(BaseModel):
    """
    Schema para respuesta de proyecto creado.
    Incluye el link corto generado.
    """
    id: int
    app_name: str
    ios_url: str
    android_url: str
    fallback_url: Optional[str]
    short_code: str
    short_url: str  # URL completa: https://onelink.app/xK9mP2
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema para listar proyectos (simplificado)"""
    id: int
    app_name: str
    short_code: str
    short_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= REDIRECT INFO =============

class RedirectInfo(BaseModel):
    """Info sobre una redirección (para debugging)"""
    short_code: str
    app_name: str
    detected_platform: str  # 'ios', 'android', 'other'
    redirect_url: str
    timestamp: datetime
