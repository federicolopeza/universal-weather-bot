# 📁 Estructura del Proyecto

## 🗂️ Organización de archivos

```
universal-weather-bot/
├── 📄 README.md                    # Documentación principal
├── 📄 LICENSE                      # Licencia MIT
├── 📄 CHANGELOG.md                 # Historial de cambios
├── 📄 CONTRIBUTING.md              # Guía para contribuidores
├── 📄 SECURITY.md                  # Política de seguridad
├── 📄 PROJECT_STRUCTURE.md         # Este archivo
├── 📄 .gitignore                   # Archivos a ignorar en Git
├── 📄 .env.example                 # Plantilla de configuración
│
├── 🤖 Bot de Telegram/
│   ├── 📄 bot.py                   # Bot principal de Telegram
│   ├── 📄 fetcher.py               # Integración con APIs meteorológicas
│   ├── 📄 aggregator.py            # Agregación inteligente de datos
│   ├── 📄 cache.py                 # Sistema de caché (Redis/memoria)
│   ├── 📄 models.py                # Modelos de datos con Pydantic
│   └── 📄 requirements.txt         # Dependencias de Python
│
├── 📱 Widget iOS/
│   ├── 📄 weather_widget.js        # Script para Scriptable
│   └── 📄 WIDGET_SETUP.md          # Guía de instalación del widget
│
├── 🔧 GitHub/
│   ├── 📁 workflows/
│   │   └── 📄 test.yml             # CI/CD con GitHub Actions
│   ├── 📁 ISSUE_TEMPLATE/
│   │   ├── 📄 bug_report.md        # Template para reportar bugs
│   │   └── 📄 feature_request.md   # Template para solicitar features
│   └── 📄 pull_request_template.md # Template para pull requests
│
└── 📚 Documentación/ (futura)
    ├── 📁 images/                  # Screenshots y diagramas
    ├── 📄 API_GUIDE.md             # Guía detallada de APIs
    └── 📄 DEPLOYMENT.md            # Guía de despliegue
```

## 🎯 Propósito de cada archivo

### 📋 Documentación Principal
- **README.md** - Punto de entrada, instalación y uso
- **CHANGELOG.md** - Historial de versiones y cambios
- **CONTRIBUTING.md** - Cómo contribuir al proyecto
- **SECURITY.md** - Política de seguridad y reportes
- **LICENSE** - Licencia MIT del proyecto

### 🤖 Bot de Telegram
- **bot.py** - Lógica principal del bot, comandos y handlers
- **fetcher.py** - Conexión con APIs meteorológicas
- **aggregator.py** - Combinación inteligente de datos
- **cache.py** - Sistema de caché para optimización
- **models.py** - Estructuras de datos con validación
- **requirements.txt** - Dependencias de Python

### 📱 Widget iOS
- **weather_widget.js** - Script completo para Scriptable
- **WIDGET_SETUP.md** - Instrucciones específicas del widget

### ⚙️ Configuración
- **.env.example** - Plantilla de variables de entorno
- **.gitignore** - Archivos excluidos del control de versiones

### 🔧 GitHub
- **workflows/test.yml** - Automatización de tests
- **ISSUE_TEMPLATE/** - Templates para issues
- **pull_request_template.md** - Template para PRs

## 🚀 Flujo de trabajo

### Para usuarios del Bot de Telegram:
1. Clonar repositorio
2. Configurar `.env` con claves API
3. Instalar dependencias con `pip install -r requirements.txt`
4. Ejecutar `python bot.py`

### Para usuarios del Widget iOS:
1. Descargar Scriptable
2. Copiar `weather_widget.js`
3. Configurar claves API en el script
4. Agregar widget a pantalla de inicio

### Para contribuidores:
1. Fork del repositorio
2. Crear rama feature
3. Seguir guías en `CONTRIBUTING.md`
4. Abrir Pull Request

## 📊 Estadísticas del proyecto

- **Archivos de código:** 6 (Python) + 1 (JavaScript)
- **Archivos de documentación:** 8
- **Archivos de configuración:** 6
- **APIs soportadas:** 5
- **Plataformas:** 2 (Telegram + iOS)
- **Licencia:** MIT (Open Source)

## 🎨 Características técnicas

### Bot de Telegram
- **Lenguaje:** Python 3.8+
- **Framework:** python-telegram-bot
- **APIs:** 5 fuentes meteorológicas
- **Caché:** Redis o memoria
- **Validación:** Pydantic

### Widget iOS
- **Plataforma:** Scriptable (iOS 14+)
- **Lenguaje:** JavaScript
- **APIs:** 3 fuentes meteorológicas
- **Actualización:** Automática cada hora
- **Diseño:** 2 columnas optimizado

## 🔄 Próximos pasos

1. **Tests unitarios** - Agregar cobertura de tests
2. **Docker** - Containerización para fácil despliegue
3. **Más idiomas** - Internacionalización
4. **Android widget** - Expansión a más plataformas
5. **Web dashboard** - Interfaz web opcional