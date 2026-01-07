"""
Router para gestión de proyectos (apps).
Operaciones CRUD completas.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os

from ..database import get_db
from ..models import User, Project, Click
from ..schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from ..auth import get_current_active_user
from ..utils.short_url import generate_short_code, generate_short_url

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"]
)

# Obtener BASE_URL desde .env
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Crear un nuevo proyecto (app con links).
    
    Ejemplo:
        POST /api/projects/
        Headers: Authorization: Bearer {token}
        Body:
        {
            "app_name": "Mi App Genial",
            "ios_url": "https://apps.apple.com/app/id123456789",
            "android_url": "https://play.google.com/store/apps/details?id=com.example.app",
            "fallback_url": "https://example.com"
        }
        
        Respuesta:
        {
            "id": 1,
            "app_name": "Mi App Genial",
            "short_code": "aBc123",
            "short_url": "http://localhost:8000/aBc123",
            "total_clicks": 0,
            ...
        }
    """
    # Generar código corto único
    short_code = generate_short_code()
    
    # Verificar que sea único (muy raro que no lo sea, pero por seguridad)
    while db.query(Project).filter(Project.short_code == short_code).first():
        short_code = generate_short_code()
    
    # Crear proyecto
    db_project = Project(
        user_id=current_user.id,
        app_name=project.app_name,
        ios_url=project.ios_url,
        android_url=project.android_url,
        fallback_url=project.fallback_url,
        short_code=short_code
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Generar URL completa
    short_url = generate_short_url(BASE_URL, short_code)
    
    # Contar clicks (0 para proyecto nuevo)
    total_clicks = 0
    
    # Retornar con campos adicionales
    return {
        **db_project.__dict__,
        "short_url": short_url,
        "total_clicks": total_clicks
    }


@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Listar todos los proyectos del usuario actual.
    
    Soporta paginación con skip y limit.
    """
    projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    # Agregar short_url y total_clicks a cada proyecto
    result = []
    for project in projects:
        clicks_count = db.query(Click).filter(
            Click.project_id == project.id
        ).count()
        
        result.append({
            **project.__dict__,
            "short_url": generate_short_url(BASE_URL, project.short_code),
            "total_clicks": clicks_count
        })
    
    return result


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener un proyecto específico por ID.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    clicks_count = db.query(Click).filter(Click.project_id == project.id).count()
    
    return {
        **project.__dict__,
        "short_url": generate_short_url(BASE_URL, project.short_code),
        "total_clicks": clicks_count
    }


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualizar un proyecto existente.
    Solo se actualizan los campos enviados.
    """
    db_project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Actualizar solo campos que no son None
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    
    clicks_count = db.query(Click).filter(Click.project_id == db_project.id).count()
    
    return {
        **db_project.__dict__,
        "short_url": generate_short_url(BASE_URL, db_project.short_code),
        "total_clicks": clicks_count
    }


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Eliminar un proyecto.
    También elimina todos los clicks asociados (cascade).
    """
    db_project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(db_project)
    db.commit()
    
    return None
