"""
Modelos de base de datos usando SQLAlchemy ORM - MVP VERSION
Solo necesitamos Projects, sin Users ni Analytics.
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base


class Project(Base):
    """
    Modelo de Proyecto (App con sus links a stores).
    MVP: Sin usuarios, sin analytics, solo la info esencial.
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información de la app
    app_name = Column(String, nullable=False)
    ios_url = Column(String, nullable=False)
    android_url = Column(String, nullable=False)
    fallback_url = Column(String, nullable=True)  # Para desktop/otros
    
    # Link corto único
    short_code = Column(String, unique=True, index=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
