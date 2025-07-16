# 🤝 Contribuir a Universal Weather Bot

¡Gracias por tu interés en contribuir! Este proyecto es open source y las contribuciones son muy bienvenidas.

## 🚀 Formas de contribuir

### 🐛 Reportar bugs
- Usa el [issue tracker](https://github.com/tu-usuario/universal-weather-bot/issues)
- Describe el problema claramente
- Incluye pasos para reproducir el bug
- Menciona tu sistema operativo y versión de Python

### 💡 Sugerir mejoras
- Abre un [discussion](https://github.com/tu-usuario/universal-weather-bot/discussions)
- Explica tu idea y por qué sería útil
- Considera la implementación técnica

### 🔧 Contribuir código

#### Configuración del entorno de desarrollo
```bash
# 1. Fork y clonar el repositorio
git clone https://github.com/tu-usuario/universal-weather-bot.git
cd universal-weather-bot

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus claves API
```

#### Proceso de contribución
1. **Fork** el repositorio
2. **Crea una rama** para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. **Haz tus cambios** siguiendo las guías de estilo
4. **Prueba** tu código localmente
5. **Commit** con mensajes descriptivos
6. **Push** a tu fork: `git push origin feature/nueva-funcionalidad`
7. **Abre un Pull Request**

## 📋 Guías de estilo

### Python (Bot de Telegram)
- Sigue [PEP 8](https://pep8.org/)
- Usa docstrings para funciones y clases
- Nombres de variables en español cuando sea apropiado
- Comentarios en español

```python
def obtener_datos_clima(ciudad: str) -> Optional[WeatherData]:
    """
    Obtiene datos meteorológicos para una ciudad específica.
    
    Args:
        ciudad: Nombre de la ciudad a consultar
        
    Returns:
        Datos meteorológicos o None si hay error
    """
    pass
```

### JavaScript (Widget iOS)
- Usa camelCase para variables
- Comentarios en español
- Funciones bien documentadas

```javascript
// Obtiene datos del clima de múltiples fuentes
async function getWeatherData() {
    // Implementación...
}
```

## 🎯 Ideas para contribuir

### 🌟 Funcionalidades prioritarias
- [ ] Soporte para más idiomas (inglés, portugués)
- [ ] Widget para Android (Tasker/KWGT)
- [ ] Gráficos de temperatura y precipitación
- [ ] Sistema de alertas meteorológicas
- [ ] Integración con más APIs meteorológicas

### 🎨 Mejoras de diseño
- [ ] Temas de colores personalizables
- [ ] Iconos meteorológicos animados
- [ ] Modo oscuro/claro automático
- [ ] Layouts alternativos para el widget

### 🔧 Mejoras técnicas
- [ ] Tests unitarios
- [ ] CI/CD con GitHub Actions
- [ ] Docker para fácil despliegue
- [ ] Base de datos para estadísticas
- [ ] API REST para terceros

### 📱 Nuevas plataformas
- [ ] Widget para macOS
- [ ] Extensión para navegadores
- [ ] App de escritorio con Electron
- [ ] Integración con Discord

## 🧪 Testing

### Bot de Telegram
```bash
# Ejecutar tests (cuando estén disponibles)
python -m pytest tests/

# Probar manualmente
python bot.py
```

### Widget iOS
- Prueba en Scriptable antes de hacer PR
- Verifica en diferentes tamaños de widget
- Asegúrate de que funcione sin claves API (modo demo)

## 📝 Documentación

### Al agregar nuevas funcionalidades
- Actualiza el README.md
- Agrega ejemplos de uso
- Documenta nuevas variables de entorno
- Incluye capturas de pantalla si es relevante

### Comentarios en código
```python
# ✅ Bueno
def calcular_promedio_ponderado(valores: List[float], pesos: List[float]) -> float:
    """Calcula el promedio ponderado de una lista de valores."""
    
# ❌ Malo
def calc_avg(vals, weights):  # calculates average
```

## 🚀 Pull Request Guidelines

### Título del PR
- Usa prefijos: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`
- Sé descriptivo: `feat: agregar soporte para API de AccuWeather`

### Descripción del PR
```markdown
## 📋 Descripción
Breve descripción de los cambios realizados.

## 🔄 Tipo de cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Cambio que rompe compatibilidad
- [ ] Documentación

## 🧪 Testing
- [ ] Probado localmente
- [ ] Tests pasan
- [ ] Documentación actualizada

## 📷 Screenshots (si aplica)
Capturas de pantalla de los cambios visuales.
```

## 🏷️ Versionado

Usamos [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- `MAJOR`: Cambios que rompen compatibilidad
- `MINOR`: Nuevas funcionalidades compatibles
- `PATCH`: Bug fixes compatibles

## 🎉 Reconocimiento

Los contribuidores serán reconocidos en:
- README.md en sección de agradecimientos
- Releases notes
- Hall of Fame (si se implementa)

## 📞 ¿Necesitas ayuda?

- 💬 [Discussions](https://github.com/tu-usuario/universal-weather-bot/discussions)
- 📧 Email: tu-email@ejemplo.com
- 🐛 [Issues](https://github.com/tu-usuario/universal-weather-bot/issues)

¡Gracias por contribuir! 🙏