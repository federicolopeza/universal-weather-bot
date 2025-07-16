# 🌤️ Universal Weather Bot & Widget

Un sistema completo de pronósticos meteorológicos que combina datos de múltiples fuentes para mayor precisión. Disponible como **Bot de Telegram** y **Widget de iOS**.

## 🚀 Características

### 🎯 **Funcionalidades principales:**
- **Múltiples fuentes de datos** - Combina OpenWeatherMap, MET Norway, WeatherAPI, Tomorrow.io y Visual Crossing
- **Agregación inteligente** - Usa promedios ponderados para mayor precisión
- **Diseño moderno** - Interfaz limpia con emojis y colores codificados
- **Actualizaciones automáticas** - Datos siempre actualizados
- **Recomendaciones inteligentes** - Consejos basados en las condiciones

### 📊 **Información mostrada:**
- Temperatura actual y rango del día
- Precipitación con probabilidades
- Velocidad del viento (km/h)
- Humedad relativa
- Sensación térmica
- Pronóstico por horas (solo futuras)
- Recomendaciones personalizadas

## 📱 Dos formas de usar

### 1. 🤖 Bot de Telegram
**🌍 Funcionalidad completa** - Consulta cualquier ciudad del mundo

**Comandos disponibles:**
- `/ubicacion` - 📍 Pronóstico de tu ubicación GPS
- `/tiempo hoy <ciudad>` - Pronóstico horario detallado
- `/tiempo semana <ciudad>` - Pronóstico de 7 días
- `/actualizar <ciudad>` - Enviar al grupo configurado

**✨ Ventajas:**
- Cualquier ciudad del mundo
- Comandos interactivos
- Grupos y actualizaciones automáticas
- Ubicación GPS automática

### 2. 📱 Widget de iOS (Scriptable)
**🏠 Información fija** - Muestra el clima de Montevideo únicamente

**Características:**
- Actualización automática cada hora
- Diseño optimizado para widget medium
- Múltiples APIs para mayor precisión
- Solo muestra horas futuras
- Siempre visible en pantalla de inicio

**⚠️ Limitación:** Solo Montevideo (para otras ciudades usa el bot)

## 🛠️ Instalación

### 🤖 Bot de Telegram

#### Prerrequisitos
- Python 3.8+
- Claves API de servicios meteorológicos

#### 1. Clonar el repositorio
```bash
git clone https://github.com/falopp/universal-weather-bot.git
cd universal-weather-bot
```

#### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 3. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus claves API
```

#### 4. Crear bot en Telegram
1. Habla con [@BotFather](https://t.me/BotFather)
2. Usa `/newbot` y sigue las instrucciones
3. Guarda el token en `.env`

#### 5. Ejecutar el bot
```bash
python bot.py
```

### 📱 Widget de iOS

#### Prerrequisitos
- iPhone/iPad con iOS 14+
- App Scriptable (gratuita en App Store)
- Claves API de servicios meteorológicos

#### 1. Descargar Scriptable
[📲 Descargar desde App Store](https://apps.apple.com/app/scriptable/id1405459188)

#### 2. Configurar el script
1. Abre Scriptable
2. Toca **+** para crear nuevo script
3. Copia el contenido de `weather_widget.js`
4. **IMPORTANTE:** Reemplaza las claves API con las tuyas
5. Guarda como "Weather Widget"

#### 3. Agregar widget a pantalla de inicio
1. Mantén presionada la pantalla de inicio
2. Toca **+** → Busca **Scriptable**
3. Selecciona tamaño **Medium**
4. Configura para usar tu script

## 🔑 Configuración de APIs

### APIs Requeridas

#### 🌐 WeatherAPI (Recomendado)
- **Gratis:** 1M llamadas/mes
- **Registro:** [weatherapi.com](https://www.weatherapi.com/)
- **Usado en:** Bot y Widget

#### 🇳🇴 MET Norway (Gratuito)
- **Gratis:** Sin límites
- **Sin registro:** No requiere clave API
- **Usado en:** Bot y Widget

#### 🌍 Visual Crossing
- **Gratis:** 1000 registros/día
- **Registro:** [visualcrossing.com](https://www.visualcrossing.com/)
- **Usado en:** Bot y Widget

#### ⚡ Tomorrow.io (Opcional)
- **Gratis:** 1000 llamadas/día
- **Registro:** [tomorrow.io](https://www.tomorrow.io/)
- **Usado en:** Solo Bot

#### ☀️ OpenWeatherMap (Opcional)
- **Gratis:** 1000 llamadas/día
- **Registro:** [openweathermap.org](https://openweathermap.org/api)
- **Usado en:** Solo Bot

### Archivo .env
```env
# Bot de Telegram
TELEGRAM_BOT_TOKEN=tu_token_de_botfather

# APIs Meteorológicas
WEATHERAPI_KEY=tu_clave_weatherapi
VISUALCROSSING_KEY=tu_clave_visualcrossing
TOMORROW_KEY=tu_clave_tomorrow_io
OWM_KEY=tu_clave_openweathermap

# Configuración opcional
GROUP_CHAT_ID=-1234567890
DEFAULT_CITY=Montevideo
```

## 🎨 Personalización

### Bot de Telegram
- Cambiar ciudad por defecto en `.env`
- Configurar grupo para actualizaciones automáticas
- Ajustar pesos de fuentes en `aggregator.py`

### Widget de iOS
```javascript
// Cambiar ciudad (solo Montevideo por defecto)
const DEFAULT_CITY = "Montevideo";

// Personalizar colores
const WIDGET_CONFIG = {
    backgroundColor: new Color("#1a1a2e"),
    titleColor: new Color("#ffffff"),
    textColor: new Color("#e0e0e0"),
    accentColor: new Color("#4fc3f7")
};
```

## 📋 Comandos del Bot

### Básicos
- `/start` - Mensaje de bienvenida
- `/help` - Ayuda completa
- `/ubicacion` - Solicita tu ubicación GPS
- `/tiempo hoy <ciudad>` - Pronóstico horario
- `/tiempo semana <ciudad>` - Pronóstico de 7 días

### Para grupos
- `/actualizar [ciudad]` - Envía actualización al grupo
- `/matutino` - Pronóstico matutino automático
- `/vespertino` - Pronóstico vespertino automático
- `/chatid` - Obtiene ID del chat para configuración

## 🏗️ Arquitectura

### Estructura del proyecto
```
universal-weather-bot/
├── 🤖 Bot de Telegram/
│   ├── bot.py              # Bot principal
│   ├── fetcher.py          # APIs meteorológicas
│   ├── aggregator.py       # Agregación de datos
│   ├── cache.py            # Sistema de caché
│   ├── models.py           # Modelos de datos
│   └── requirements.txt    # Dependencias Python
├── 📱 iOS Widget/
│   ├── weather_widget.js   # Script de Scriptable
│   └── WIDGET_SETUP.md     # Guía de instalación
├── 📚 Documentación/
│   ├── README.md           # Este archivo
│   └── docs/               # Imágenes y guías
└── ⚙️ Configuración/
    └── .env.example        # Plantilla de configuración
```

### Flujo de datos
1. **Solicitud** → Usuario pide pronóstico
2. **Agregación** → Consulta múltiples APIs
3. **Procesamiento** → Combina datos con pesos
4. **Formato** → Genera respuesta visual
5. **Entrega** → Envía a Telegram o muestra en widget

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! 

### Cómo contribuir
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Ideas para contribuir
- 🌍 Soporte para más idiomas
- 🎨 Temas de colores adicionales
- 📊 Gráficos y visualizaciones
- 🌡️ Más fuentes de datos meteorológicos
- 📱 Widget para Android (Tasker/KWGT)
- 🔔 Sistema de alertas meteorológicas

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

⭐ **¡Si te gusta el proyecto, dale una estrella!** ⭐

Hecho con ❤️ para la comunidad open source
