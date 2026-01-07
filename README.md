# OneLink - Universal App Store Link Generator

Sistema para generar links universales que redirigen automáticamente a la App Store correcta (iOS o Android) según el dispositivo del usuario.

## 🚀 Características

- ✅ Detección automática de plataforma (iOS/Android)
- ✅ URLs cortas personalizadas
- ✅ Analytics en tiempo real
- ✅ Dashboard de administración
- ✅ API REST completa con autenticación JWT
- ✅ Soporte para múltiples proyectos por usuario

## 🛠️ Stack Tecnológico

- **Backend:** FastAPI (Python 3.9+)
- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **ORM:** SQLAlchemy
- **Auth:** JWT tokens con python-jose
- **Detección:** user-agents library

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/efrain26/one-link.git
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
