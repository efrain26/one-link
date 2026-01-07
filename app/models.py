"""
Modelos de base de datos usando SQLAlchemy ORM.
Similar a @Entity y @Dao en Room (Android).
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    """
    Modelo de Usuario.
    Similar a:
    @Entity(tableName = "users")
    data class User(...)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación uno-a-muchos con Projects
    # Similar a @Relation en Room
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    """
    Modelo de Proyecto (App con sus links a stores).
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información de la app
    app_name = Column(String, nullable=False)
    ios_url = Column(String, nullable=False)
    android_url = Column(String, nullable=False)
    fallback_url = Column(String, nullable=True)
    
    # Link corto único
    short_code = Column(String, unique=True, index=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    owner = relationship("User", back_populates="projects")
    clicks = relationship("Click", back_populates="project", cascade="all, delete-orphan")


class Click(Base):
    """
    Modelo de Click (Analytics).
    Registra cada vez que alguien usa un link.
    """
    __tablename__ = "clicks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Información del click
    platform = Column(String, nullable=False)  # 'ios', 'android', 'other'
    device_type = Column(String, nullable=True)  # 'iPhone', 'Samsung Galaxy', etc.
    browser = Column(String, nullable=True)
    os_version = Column(String, nullable=True)
    
    # Geolocalización (opcional)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    
    # IP hash (por privacidad, no guardamos IP real)
    ip_hash = Column(String, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relación
    project = relationship("Project", back_populates="clicks")
