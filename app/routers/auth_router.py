"""
Router de autenticación.
Endpoints: /api/auth/register, /api/auth/login, /api/auth/me
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, Token, UserLogin
from ..auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_user_by_email
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario.
    
    - **email**: Email único del usuario
    - **password**: Contraseña (mínimo 6 caracteres)
    - **name**: Nombre del usuario (opcional)
    
    Ejemplo:
        POST /api/auth/register
        {
            "email": "user@example.com",
            "password": "securepass123",
            "name": "John Doe"
        }
    """
    # Verificar si el email ya existe
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login de usuario y generación de JWT token.
    
    - **username**: Email del usuario (OAuth2 usa 'username')
    - **password**: Contraseña
    
    Returns:
        access_token: JWT token para usar en requests autenticados
        token_type: "bearer"
    
    Ejemplo:
        POST /api/auth/login
        Content-Type: application/x-www-form-urlencoded
        
        username=user@example.com&password=securepass123
    """
    # Autenticar usuario
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la información del usuario actualmente autenticado.
    
    Requiere: Authorization header con Bearer token
    
    Ejemplo:
        GET /api/auth/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    return current_user
