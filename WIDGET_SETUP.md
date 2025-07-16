# 📱 Widget de Clima para iOS - Scriptable

Este widget replica la funcionalidad del **Universal Weather Bot** directamente en tu pantalla de inicio de iOS.

> **⚠️ IMPORTANTE:** Este widget está configurado para mostrar el clima de **Montevideo** únicamente. Para otras ciudades, usa el Bot de Telegram.

## 🚀 Instalación

### 1. Descargar Scriptable
- Descarga la app **Scriptable** desde la App Store (es gratuita)
- [Enlace directo a Scriptable](https://apps.apple.com/app/scriptable/id1405459188)

### 2. Obtener Claves API (REQUERIDO)

#### WeatherAPI (Principal)
1. Ve a [weatherapi.com](https://www.weatherapi.com/)
2. Regístrate gratis (1M llamadas/mes)
3. Copia tu API key desde el dashboard

#### Visual Crossing (Secundaria)
1. Ve a [visualcrossing.com](https://www.visualcrossing.com/)
2. Regístrate gratis (1000 registros/día)
3. Copia tu API key

### 3. Configurar el Script
1. Abre Scriptable
2. Toca el **+** para crear un nuevo script
3. Copia y pega todo el contenido del archivo `weather_widget.js`
4. **IMPORTANTE**: Reemplaza las claves API:
   ```javascript
   const API_KEYS = {
       weatherapi: "TU_CLAVE_WEATHERAPI_AQUI",
       visualcrossing: "TU_CLAVE_VISUALCROSSING_AQUI"
   };
   ```
5. Guarda el script con el nombre "Weather Widget"

### 4. Agregar Widget a la Pantalla de Inicio
1. Mantén presionada la pantalla de inicio hasta que las apps tiemblen
2. Toca el **+** en la esquina superior izquierda
3. Busca **Scriptable**
4. Selecciona el tamaño **Medium** (recomendado)
5. Toca **Add Widget**
6. Toca el widget recién agregado para configurarlo
7. Selecciona tu script "Weather Widget"
8. ¡Listo!

## ⚙️ Configuración

### Personalización
```javascript
// Cambiar ciudad por defecto
const DEFAULT_CITY = "Madrid"; // Tu ciudad

// Personalizar colores
const WIDGET_CONFIG = {
  backgroundColor: new Color("#1a1a2e"), // Fondo oscuro
  titleColor: new Color("#ffffff"),      // Texto principal
  textColor: new Color("#e0e0e0"),       // Texto secundario
  accentColor: new Color("#4fc3f7"),     // Color de acentos
  warningColor: new Color("#ff9800"),    // Advertencias
  dangerColor: new Color("#f44336")      // Errores
};
```

### Actualización Automática
- El widget se actualiza automáticamente cada hora
- También puedes forzar la actualización tocando el widget

## 📊 Información Mostrada

### 🌡️ Datos Actuales
- Temperatura actual con emoji del clima
- Condición meteorológica
- Ciudad y país

### 📈 Resumen del Día
- Rango de temperatura (min/max)
- Precipitación total y probabilidad
- Viento promedio con descripción

### ⏰ Próximas Horas
- Pronóstico de las próximas 3 horas
- Temperatura y condición por hora

### 💡 Recomendaciones
- Consejos automáticos basados en el clima:
  - ☀️ Usar protector solar
  - ☔ Llevar paraguas
  - 💨 Cuidado con el viento
  - 🧥 Abrigarse bien

## 🎨 Diseño

El widget usa un diseño moderno con:
- **Fondo oscuro** para mejor legibilidad
- **Emojis** para representar condiciones climáticas
- **Colores codificados** para temperaturas
- **Layout responsivo** que se adapta al tamaño

## 🔧 Solución de Problemas

### Widget muestra "Error"
1. Verifica que tu clave API sea correcta
2. Asegúrate de tener conexión a internet
3. Comprueba que el nombre de la ciudad sea correcto

### Widget no se actualiza
1. Abre Scriptable y ejecuta el script manualmente
2. Verifica los permisos de ubicación si usas GPS
3. Reinicia el widget eliminándolo y agregándolo de nuevo

### Personalizar para tu ubicación
```javascript
// Para usar tu ubicación actual (requiere permisos)
const location = await Location.current();
const DEFAULT_CITY = `${location.latitude},${location.longitude}`;
```

## 🌟 Características

✅ **Actualización automática** cada hora
✅ **Diseño moderno** con emojis y colores
✅ **Información completa** del clima
✅ **Recomendaciones inteligentes**
✅ **Funciona offline** (usa datos en caché)
✅ **Personalizable** (colores, ciudad, etc.)

## 📱 Tamaños de Widget

- **Small**: Solo temperatura y condición actual
- **Medium**: Información completa (recomendado)
- **Large**: Información extendida con más horas

## 🔄 Actualizaciones

Para actualizar el widget:
1. Abre Scriptable
2. Edita tu script "Weather Widget"
3. Copia el nuevo código
4. Guarda los cambios
5. El widget se actualizará automáticamente

¡Disfruta de tu nuevo widget de clima personalizado! 🌤️