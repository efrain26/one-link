"""
Aplicación principal FastAPI.
Punto de entrada de la API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .database import engine, Base
from .routers import auth, projects, redirect, analytics

# Cargar variables de entorno
load_dotenv()

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title="OneLink API",
    description="Universal App Store Link Generator - Redirect users to the right app store based on their device",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
# En producción, especifica los dominios permitidos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: ["https://tudominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir routers
# IMPORTANTE: redirect.router debe ir PRIMERO y SIN prefix
# para que /{short_code} funcione en la raíz
app.include_router(redirect.router)  # Primero, sin prefix
app.include_router(auth.router)      # /api/auth/*
app.include_router(projects.router)  # /api/projects/*
app.include_router(analytics.router) # /api/analytics/*


# Root endpoint
@app.get("/")
def root():
    """
    Endpoint raíz - Información de la API.
    """
    return {
        "message": "OneLink API - Universal App Store Link Generator",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "auth": "/api/auth",
            "projects": "/api/projects",
            "analytics": "/api/analytics",
            "redirect": "/{short_code}"
        },
        "status": "operational"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check para monitoreo.
    """
    return {
        "status": "healthy",
        "database": "connected"
    }



# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Handler personalizado para 404.
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    Handler personalizado para errores 500.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Ejecutado al iniciar la aplicación.
    """
    print("🚀 OneLink API starting up...")
    print(f"📚 Documentation available at: http://localhost:8000/docs")
    print(f"🔗 Redirect endpoint: http://localhost:8000/{{short_code}}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Ejecutado al cerrar la aplicación.
    """
    print("👋 OneLink API shutting down...")
