"""
Router para gestión de proyectos - MVP VERSION
Solo crear y listar proyectos, sin autenticación.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv

from ..database import get_db
from ..models import Project
from ..schemas import ProjectCreate, ProjectResponse, ProjectListResponse
from ..utils.short_url import generate_short_code, generate_short_url

load_dotenv()

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"]
)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo proyecto y genera un link corto único.
    
    No requiere autenticación (MVP).
    
    Returns:
        ProjectResponse con el link corto generado
    """
    
    # Generar código corto único
    short_code = generate_short_code(length=6)
    
    # Verificar que sea único (probabilidad muy baja de colisión, pero mejor verificar)
    max_attempts = 10
    attempt = 0
    while db.query(Project).filter(Project.short_code == short_code).first():
        short_code = generate_short_code(length=6)
        attempt += 1
        if attempt >= max_attempts:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo generar un código único. Intenta de nuevo."
            )
    
    # Crear proyecto en base de datos
    db_project = Project(
        app_name=project.app_name,
        ios_url=str(project.ios_url),
        android_url=str(project.android_url),
        fallback_url=str(project.fallback_url) if project.fallback_url else None,
        short_code=short_code
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Generar URL completa
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    short_url = generate_short_url(base_url, short_code)
    
    # Retornar respuesta con link generado
    return ProjectResponse(
        id=db_project.id,
        app_name=db_project.app_name,
        ios_url=db_project.ios_url,
        android_url=db_project.android_url,
        fallback_url=db_project.fallback_url,
        short_code=db_project.short_code,
        short_url=short_url,
        created_at=db_project.created_at
    )


@router.get("/", response_model=List[ProjectListResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista todos los proyectos creados.
    
    MVP: No hay filtros por usuario, lista todos.
    
    Args:
        skip: Número de proyectos a saltar (paginación)
        limit: Máximo de proyectos a retornar
    """
    projects = db.query(Project).offset(skip).limit(limit).all()
    
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    
    result = []
    for project in projects:
        result.append(ProjectListResponse(
            id=project.id,
            app_name=project.app_name,
            short_code=project.short_code,
            short_url=generate_short_url(base_url, project.short_code),
            created_at=project.created_at
        ))
    
    return result


@router.get("/{short_code}", response_model=ProjectResponse)
def get_project_by_code(
    short_code: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene información de un proyecto por su código corto.
    Útil para verificar que un link existe.
    """
    project = db.query(Project).filter(Project.short_code == short_code).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún proyecto con el código: {short_code}"
        )
    
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    short_url = generate_short_url(base_url, project.short_code)
    
    return ProjectResponse(
        id=project.id,
        app_name=project.app_name,
        ios_url=project.ios_url,
        android_url=project.android_url,
        fallback_url=project.fallback_url,
        short_code=project.short_code,
        short_url=short_url,
        created_at=project.created_at
    )
