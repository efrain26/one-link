"""
OneLink - Universal App Store Link Generator
Aplicación FastAPI principal.

Esta aplicación permite crear links universales que redirigen automáticamente
a la App Store correcta (iOS o Android) según el dispositivo del usuario.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .database import engine, Base
from .routers import auth_router, projects, redirect, analytics

# Cargar variables de entorno
load_dotenv()

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title="OneLink API",
    description="Universal App Store Link Generator - Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
# IMPORTANTE: redirect.router va PRIMERO y SIN PREFIX
# porque necesita capturar /{short_code} directamente
app.include_router(redirect.router)

# Los demás routers con sus prefijos
app.include_router(auth_router.router)
app.include_router(projects.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    """
    Endpoint raíz - información de la API.
    """
    return {
        "name": "OneLink API",
        "version": "1.0.0",
        "description": "Universal App Store Link Generator",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "me": "GET /api/auth/me"
            },
            "projects": {
                "list": "GET /api/projects/",
                "create": "POST /api/projects/",
                "get": "GET /api/projects/{id}",
                "update": "PUT /api/projects/{id}",
                "delete": "DELETE /api/projects/{id}"
            },
            "analytics": {
                "summary": "GET /api/analytics/{project_id}/summary",
                "clicks": "GET /api/analytics/{project_id}/clicks",
                "overview": "GET /api/analytics/overview"
            },
            "redirect": {
                "short_link": "GET /{short_code}"
            }
        }
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint para monitoreo.
    """
    return {
        "status": "healthy",
        "service": "onelink-api",
        "version": "1.0.0"
    }


@app.exception_handler(404)
def not_found_handler(request, exc):
    """
    Handler personalizado para 404.
    """
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Not found",
            "message": "The requested resource was not found"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Para desarrollo local
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
