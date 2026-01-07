"""
Router de analytics.
Proporciona estadísticas y métricas de los proyectos.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database import get_db
from ..models import User, Project, Click
from ..schemas import AnalyticsSummary, ClickResponse
from ..auth import get_current_active_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/{project_id}/summary", response_model=AnalyticsSummary)
def get_project_analytics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int = 30
):
    """
    Obtiene resumen de analytics para un proyecto.
    
    - **project_id**: ID del proyecto
    - **days**: Número de días a analizar (default: 30)
    
    Returns:
        - Total de clicks
        - Clicks por plataforma (iOS, Android, Other)
        - Tasa de conversión
        - Top países
        - Clicks por día
    
    Ejemplo:
        GET /api/analytics/1/summary?days=30
        Authorization: Bearer {token}
    """
    # Verificar que el proyecto pertenece al usuario
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Calcular fecha límite
    date_limit = datetime.utcnow() - timedelta(days=days)
    
    # Obtener todos los clicks del proyecto en el período
    clicks = db.query(Click).filter(
        Click.project_id == project_id,
        Click.timestamp >= date_limit
    ).all()
    
    # Contar por plataforma
    total_clicks = len(clicks)
    ios_clicks = sum(1 for c in clicks if c.platform == 'ios')
    android_clicks = sum(1 for c in clicks if c.platform == 'android')
    other_clicks = sum(1 for c in clicks if c.platform == 'other')
    
    # Calcular tasa de conversión (móviles / total)
    mobile_clicks = ios_clicks + android_clicks
    conversion_rate = f"{(mobile_clicks / total_clicks * 100):.1f}%" if total_clicks > 0 else "0%"
    
    # Top países (agrupar por país)
    country_counts = {}
    for click in clicks:
        country = click.country or "Unknown"
        country_counts[country] = country_counts.get(country, 0) + 1
    
    top_countries = [
        {"country": country, "clicks": count}
        for country, count in sorted(
            country_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5 países
    ]
    
    # Clicks por día
    clicks_by_day_dict = {}
    for click in clicks:
        day = click.timestamp.date().isoformat()
        clicks_by_day_dict[day] = clicks_by_day_dict.get(day, 0) + 1
    
    clicks_by_day = [
        {"date": day, "clicks": count}
        for day, count in sorted(clicks_by_day_dict.items())
    ]
    
    return {
        "project_id": project_id,
        "app_name": project.app_name,
        "total_clicks": total_clicks,
        "ios_clicks": ios_clicks,
        "android_clicks": android_clicks,
        "other_clicks": other_clicks,
        "conversion_rate": conversion_rate,
        "top_countries": top_countries,
        "clicks_by_day": clicks_by_day
    }


@router.get("/{project_id}/clicks", response_model=List[ClickResponse])
def get_project_clicks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Obtiene lista detallada de clicks de un proyecto.
    
    - **skip**: Registros a saltar (paginación)
    - **limit**: Máximo de registros a retornar
    
    Ejemplo:
        GET /api/analytics/1/clicks?skip=0&limit=50
        Authorization: Bearer {token}
    """
    # Verificar que el proyecto pertenece al usuario
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Obtener clicks ordenados por timestamp descendente (más recientes primero)
    clicks = db.query(Click).filter(
        Click.project_id == project_id
    ).order_by(
        Click.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    return clicks


@router.get("/overview", response_model=dict)
def get_user_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene resumen general de analytics para todos los proyectos del usuario.
    
    Returns:
        - Total de proyectos
        - Total de clicks
        - Clicks por plataforma
        - Proyecto más popular
    
    Ejemplo:
        GET /api/analytics/overview
        Authorization: Bearer {token}
    """
    # Obtener todos los proyectos del usuario
    projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).all()
    
    total_projects = len(projects)
    
    # Obtener IDs de proyectos
    project_ids = [p.id for p in projects]
    
    if not project_ids:
        return {
            "total_projects": 0,
            "total_clicks": 0,
            "ios_clicks": 0,
            "android_clicks": 0,
            "other_clicks": 0,
            "most_popular_project": None
        }
    
    # Contar todos los clicks
    all_clicks = db.query(Click).filter(
        Click.project_id.in_(project_ids)
    ).all()
    
    total_clicks = len(all_clicks)
    ios_clicks = sum(1 for c in all_clicks if c.platform == 'ios')
    android_clicks = sum(1 for c in all_clicks if c.platform == 'android')
    other_clicks = sum(1 for c in all_clicks if c.platform == 'other')
    
    # Encontrar proyecto más popular
    project_click_counts = {}
    for click in all_clicks:
        project_click_counts[click.project_id] = project_click_counts.get(click.project_id, 0) + 1
    
    most_popular_project = None
    if project_click_counts:
        most_popular_id = max(project_click_counts, key=project_click_counts.get)
        most_popular = next((p for p in projects if p.id == most_popular_id), None)
        if most_popular:
            most_popular_project = {
                "id": most_popular.id,
                "app_name": most_popular.app_name,
                "clicks": project_click_counts[most_popular_id]
            }
    
    return {
        "total_projects": total_projects,
        "total_clicks": total_clicks,
        "ios_clicks": ios_clicks,
        "android_clicks": android_clicks,
        "other_clicks": other_clicks,
        "most_popular_project": most_popular_project
    }
