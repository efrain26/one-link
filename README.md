# OneLink - Universal App Store Link Generator

Sistema para generar links universales que redirigen automáticamente a la App Store correcta (iOS o Android) según el dispositivo del usuario.

## 🚀 Características

- ✅ Detección automática de plataforma (iOS/Android)
- ✅ URLs cortas personalizadas
- ✅ Analytics en tiempo real
- ✅ Dashboard de administración
- ✅ API REST completa
- ✅ Soporte para múltiples proyectos

## 🛠️ Stack Tecnológico

- **Backend:** FastAPI (Python)
- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **ORM:** SQLAlchemy
- **Auth:** JWT tokens
- **Detección:** user-agents

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/one-link.git
cd one-link
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Inicializar la base de datos

```bash
# La base de datos se crea automáticamente al iniciar la app
```

### 6. Correr el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

## 📚 Documentación API

Una vez iniciado el servidor, accede a:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🏗️ Estructura del Proyecto

```
one-link/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI principal
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── database.py          # Configuración DB
│   ├── auth.py              # Autenticación JWT
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── projects.py      # CRUD proyectos
│   │   ├── redirect.py      # Endpoint redirección
│   │   └── analytics.py     # Estadísticas
│   └── utils/
│       ├── __init__.py

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Inicializar la base de datos

```bash
# La base de datos se crea automáticamente al iniciar la app
```

### 6. Correr el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

## 📚 Documentación API

Una vez iniciado el servidor, accede a:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🏗️ Estructura del Proyecto

```
one-link/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI principal
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── database.py          # Configuración DB
│   ├── auth.py              # Autenticación JWT
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── projects.py      # CRUD proyectos
│   │   ├── redirect.py      # Endpoint redirección
│   │   └── analytics.py     # Estadísticas
│   └── utils/
│       ├── __init__.py

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Inicializar la base de datos

```bash
# La base de datos se crea automáticamente al iniciar la app
```

### 6. Correr el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

## 📚 Documentación API

Una vez iniciado el servidor, accede a:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🏗️ Estructura del Proyecto

```
one-link/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI principal
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── database.py          # Configuración DB
│   ├── auth.py              # Autenticación JWT
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── projects.py      # CRUD proyectos
│   │   ├── redirect.py      # Endpoint redirección
│   │   └── analytics.py     # Estadísticas
│   └── utils/
│       ├── __init__.py
│       ├── device_detect.py  # Detección de dispositivo
│       └── short_url.py     # Generador URLs cortas
├── static/                  # Archivos estáticos
├── templates/               # Templates HTML
├── .env                     # Variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔐 Autenticación

La API usa JWT tokens. Para autenticarte:

1. Crear un usuario: `POST /api/auth/register`
2. Hacer login: `POST /api/auth/login`
3. Usar el token en headers: `Authorization: Bearer {token}`

## 📊 Uso Básico

### Crear un proyecto

```bash
curl -X POST "http://localhost:8000/api/projects/" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "Mi App",
    "ios_url": "https://apps.apple.com/app/id123456789",
    "android_url": "https://play.google.com/store/apps/details?id=com.example.app"
  }'
```

### Usar el link generado

El link generado será algo como: `http://localhost:8000/aBc123`

Cuando alguien haga click:
- iOS users → App Store
- Android users → Play Store
- Others → Fallback URL

## 🚀 Deployment

### Railway

```bash
# Conectar repo con Railway
# Railway detecta FastAPI automáticamente
```

### Render

```bash
# Conectar repo con Render
# Agregar comando de inicio: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 📝 Licencia

MIT

## 👨‍💻 Autor

Creado con ❤️ para simplificar la distribución de apps móviles
