"""
OneLink - Universal App Store Link Generator
FastAPI Main Application - MVP VERSION

Simple, rápido, sin autenticación ni analytics.
Solo redirección inteligente a app stores.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .database import engine, Base
from .routers import projects, redirect

# Cargar variables de entorno
load_dotenv()

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI(
    title="OneLink API",
    description="Universal App Store Link Generator - Redirige usuarios a la store correcta automáticamente",
    version="1.0.0 MVP",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS (permitir requests desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= ROUTES =============

# Root endpoint
@app.get("/", tags=["root"])
def root():
    """
    Endpoint raíz - Info básica de la API
    """
    return {
        "name": "OneLink API",
        "version": "1.0.0 MVP",
        "description": "Universal App Store Link Generator",
        "docs": "/docs",
        "endpoints": {
            "create_project": "POST /api/projects/",
            "list_projects": "GET /api/projects/",
            "redirect": "GET /{short_code}",
            "redirect_info": "GET /info/{short_code}"
        }
    }


# Health check
@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint para monitoring
    """
    return {
        "status": "healthy",
        "service": "onelink-api",
        "version": "1.0.0"
    }



# ============= INCLUDE ROUTERS =============

# Router de proyectos (crear, listar)
app.include_router(projects.router)

# Router de redirección (¡EL MÁS IMPORTANTE!)
# IMPORTANTE: Este debe ir SIN prefijo para que /{short_code} funcione
app.include_router(redirect.router)


# ============= ERROR HANDLERS =============

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Handler personalizado para 404
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "El recurso solicitado no existe",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    Handler personalizado para errores 500
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Ocurrió un error interno. Por favor intenta de nuevo."
        }
    )


# ============= STARTUP EVENT =============

@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación
    """
    print("🚀 OneLink API iniciada")
    print(f"📝 Documentación: http://localhost:8000/docs")
    print(f"🔗 Base URL: {os.getenv('BASE_URL', 'http://localhost:8000')}")
    print("✅ Sistema listo para generar links universales")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento que se ejecuta al cerrar la aplicación
    """
    print("👋 OneLink API detenida")
