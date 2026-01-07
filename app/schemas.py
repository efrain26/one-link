"""
Schemas Pydantic para validación de datos.
Similar a data classes en Kotlin para validación.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# ============= USER SCHEMAS =============

class UserBase(BaseModel):
    """Schema base para usuario"""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    """Schema para respuesta de usuario (sin password)"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Antes era orm_mode en Pydantic v1


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


# ============= PROJECT SCHEMAS =============

class ProjectBase(BaseModel):
    """Schema base para proyecto"""
    app_name: str = Field(..., min_length=1, max_length=100)
    ios_url: str = Field(..., min_length=10)
    android_url: str = Field(..., min_length=10)
    fallback_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema para crear proyecto"""
    pass


class ProjectUpdate(BaseModel):
    """Schema para actualizar proyecto (todos los campos opcionales)"""
    app_name: Optional[str] = Field(None, min_length=1, max_length=100)
    ios_url: Optional[str] = Field(None, min_length=10)
    android_url: Optional[str] = Field(None, min_length=10)
    fallback_url: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema para respuesta de proyecto"""
    id: int
    user_id: int
    short_code: str
    short_url: str  # URL completa generada
    total_clicks: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= ANALYTICS SCHEMAS =============

class ClickResponse(BaseModel):
    """Schema para respuesta de click individual"""
    id: int
    project_id: int
    platform: str
    device_type: Optional[str]
    browser: Optional[str]
    country: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    """Schema para resumen de analytics"""
    project_id: int
    app_name: str
    total_clicks: int
    ios_clicks: int
    android_clicks: int
    other_clicks: int
    conversion_rate: str  # Porcentaje de iOS + Android
    top_countries: List[dict] = []
    clicks_by_day: List[dict] = []


# ============= AUTH SCHEMAS =============

class Token(BaseModel):
    """Schema para token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema para datos dentro del token"""
    email: Optional[str] = None
