"""
Router de analytics - Estadísticas y métricas.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..models import User, Project, Click
from ..schemas import AnalyticsSummary, ClickResponse
from ..auth import get_current_active_user

router = APIRouter(
    prefix="/api/analytics",
    tags=["analytics"]
)


@router.get("/projects/{project_id}/summary", response_model=AnalyticsSummary)
def get_project_analytics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener resumen de analytics para un proyecto.
    
    Retorna:
    - Total de clicks
    - Clicks por plataforma (iOS, Android, Other)
    - Tasa de conversión
    - Top países
    - Clicks por día
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
    
    # Obtener todos los clicks del proyecto
    clicks = db.query(Click).filter(Click.project_id == project_id).all()
    
    total_clicks = len(clicks)
    
    # Contar por plataforma
    ios_clicks = sum(1 for c in clicks if c.platform == 'ios')
    android_clicks = sum(1 for c in clicks if c.platform == 'android')
    other_clicks = sum(1 for c in clicks if c.platform == 'other')
    
    # Calcular tasa de conversión (móviles vs total)
    mobile_clicks = ios_clicks + android_clicks
    conversion_rate = f"{(mobile_clicks / total_clicks * 100):.1f}%" if total_clicks > 0 else "0%"
    
    # Top países (simplificado - puedes mejorar con GeoIP)
    country_counts = db.query(
        Click.country,
        func.count(Click.id).label('count')
    ).filter(
        Click.project_id == project_id
    ).group_by(Click.country).order_by(func.count(Click.id).desc()).limit(5).all()
    
    top_countries = [
        {"country": country, "clicks": count}
        for country, count in country_counts
    ]
    
    # Clicks por día (últimos 7 días)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_clicks = db.query(
        func.date(Click.timestamp).label('date'),
        func.count(Click.id).label('clicks')
    ).filter(
        Click.project_id == project_id,
        Click.timestamp >= seven_days_ago
    ).group_by(func.date(Click.timestamp)).all()
    
    clicks_by_day = [
        {"date": str(date), "clicks": clicks}
        for date, clicks in daily_clicks
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


@router.get("/projects/{project_id}/clicks", response_model=List[ClickResponse])
def get_project_clicks(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener lista detallada de clicks individuales.
    Útil para ver cada click con sus detalles.
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
    
    # Obtener clicks con paginación
    clicks = db.query(Click).filter(
        Click.project_id == project_id
    ).order_by(Click.timestamp.desc()).offset(skip).limit(limit).all()
    
    return clicks


@router.get("/dashboard")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Resumen general de todos los proyectos del usuario.
    Útil para mostrar un dashboard general.
    """
    # Total de proyectos
    total_projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).count()
    
    # Total de clicks en todos los proyectos
    project_ids = [p.id for p in db.query(Project.id).filter(
        Project.user_id == current_user.id
    ).all()]
    
    total_clicks = db.query(Click).filter(
        Click.project_id.in_(project_ids)
    ).count() if project_ids else 0
    
    # Clicks por plataforma (global)
    platform_stats = db.query(
        Click.platform,
        func.count(Click.id).label('count')
    ).filter(
        Click.project_id.in_(project_ids)
    ).group_by(Click.platform).all() if project_ids else []
    
    platform_breakdown = {
        platform: count for platform, count in platform_stats
    }
    
    # Proyecto más popular (por clicks)
    if project_ids:
        top_project_id = db.query(
            Click.project_id,
            func.count(Click.id).label('click_count')
        ).filter(
            Click.project_id.in_(project_ids)
        ).group_by(Click.project_id).order_by(
            func.count(Click.id).desc()
        ).first()
        
        if top_project_id:
            top_project = db.query(Project).filter(
                Project.id == top_project_id[0]
            ).first()
            most_popular = {
                "project_id": top_project.id,
                "app_name": top_project.app_name,
                "clicks": top_project_id[1]
            }
        else:
            most_popular = None
    else:
        most_popular = None
    
    return {
        "total_projects": total_projects,
        "total_clicks": total_clicks,
        "platform_breakdown": platform_breakdown,
        "most_popular_project": most_popular
    }
