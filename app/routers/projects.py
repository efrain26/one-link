"""
Router de proyectos.
CRUD completo: Create, Read, Update, Delete
Endpoints: /api/projects/
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os

from ..database import get_db
from ..models import User, Project, Click
from ..schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from ..auth import get_current_active_user
from ..utils.short_url import generate_short_code, generate_short_url

router = APIRouter(prefix="/api/projects", tags=["Projects"])

# Base URL desde environment variable
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Crea un nuevo proyecto (app con links a stores).
    
    - **app_name**: Nombre de la aplicación
    - **ios_url**: URL de Apple App Store
    - **android_url**: URL de Google Play Store
    - **fallback_url**: URL de respaldo (opcional)
    
    Returns:
        Proyecto creado con short_code y short_url generados
    
    Ejemplo:
        POST /api/projects/
        Authorization: Bearer {token}
        {
            "app_name": "Mi Super App",
            "ios_url": "https://apps.apple.com/app/id123456789",
            "android_url": "https://play.google.com/store/apps/details?id=com.example.app",
            "fallback_url": "https://example.com"
        }
    """
    # Generar código corto único
    short_code = generate_short_code()
    
    # Verificar que sea único (por si acaso hay colisión)
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
    
    # Contar clicks (será 0 para nuevo proyecto)
    total_clicks = 0
    
    # Retornar con información adicional
    return {
        **db_project.__dict__,
        "short_url": short_url,
        "total_clicks": total_clicks
    }


@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Lista todos los proyectos del usuario actual.
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Máximo de registros a retornar
    
    Ejemplo:
        GET /api/projects/?skip=0&limit=10
        Authorization: Bearer {token}
    """
    projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    # Enriquecer con información adicional
    result = []
    for project in projects:
        # Contar clicks
        total_clicks = db.query(Click).filter(
            Click.project_id == project.id
        ).count()
        
        result.append({
            **project.__dict__,
            "short_url": generate_short_url(BASE_URL, project.short_code),
            "total_clicks": total_clicks
        })
    
    return result


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene un proyecto específico por ID.
    
    Ejemplo:
        GET /api/projects/1
        Authorization: Bearer {token}
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
    
    # Contar clicks
    total_clicks = db.query(Click).filter(
        Click.project_id == project.id
    ).count()
    
    return {
        **project.__dict__,
        "short_url": generate_short_url(BASE_URL, project.short_code),
        "total_clicks": total_clicks
    }


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualiza un proyecto existente.
    
    Todos los campos son opcionales. Solo se actualizan los campos enviados.
    
    Ejemplo:
        PUT /api/projects/1
        Authorization: Bearer {token}
        {
            "app_name": "Nuevo Nombre"
        }
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
    
    # Actualizar solo los campos enviados
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    # Contar clicks
    total_clicks = db.query(Click).filter(
        Click.project_id == project.id
    ).count()
    
    return {
        **project.__dict__,
        "short_url": generate_short_url(BASE_URL, project.short_code),
        "total_clicks": total_clicks
    }


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Elimina un proyecto.
    
    También elimina todos los clicks asociados (cascade).
    
    Ejemplo:
        DELETE /api/projects/1
        Authorization: Bearer {token}
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
    
    db.delete(project)
    db.commit()
    
    return None
