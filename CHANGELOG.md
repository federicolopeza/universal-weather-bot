# 📋 Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🔄 En desarrollo
- Tests unitarios
- Soporte para más idiomas
- Gráficos de temperatura

## [1.0.0] - 2025-01-16

### ✨ Agregado
- **Bot de Telegram** con comandos completos
  - `/ubicacion` - Pronóstico por GPS
  - `/tiempo hoy <ciudad>` - Pronóstico horario
  - `/tiempo semana <ciudad>` - Pronóstico semanal
  - Comandos para grupos (`/actualizar`, `/matutino`, `/vespertino`)
- **Widget de iOS** para Scriptable
  - Diseño en 2 columnas optimizado
  - Actualización automática cada hora
  - Solo muestra horas futuras
- **Múltiples APIs meteorológicas**
  - WeatherAPI (principal)
  - MET Norway (gratuito)
  - Visual Crossing
  - Tomorrow.io (opcional)
  - OpenWeatherMap (opcional)
- **Agregación inteligente** de datos con pesos por fuente
- **Sistema de caché** (Redis o memoria)
- **Recomendaciones automáticas** basadas en condiciones
- **Información completa**
  - Temperatura actual y rango
  - Precipitación con probabilidades
  - Viento en km/h
  - Humedad relativa
  - Sensación térmica

### 🎨 Diseño
- **Emojis del clima** según condiciones
- **Colores codificados** para temperaturas
- **Layout responsivo** para widget medium
- **Interfaz moderna** con Markdown en Telegram

### 🔧 Técnico
- **Arquitectura modular** (bot, fetcher, aggregator, cache, models)
- **Manejo de errores** robusto
- **Fallback automático** entre APIs
- **Configuración por variables de entorno**
- **Documentación completa**

### 📱 Plataformas
- **Telegram** - Funcionalidad completa para cualquier ciudad
- **iOS (Scriptable)** - Widget fijo para Montevideo

---

## 🏷️ Formato de Versiones

### Tipos de cambios
- **✨ Agregado** - Nuevas funcionalidades
- **🔄 Cambiado** - Cambios en funcionalidades existentes
- **🗑️ Deprecado** - Funcionalidades que serán removidas
- **❌ Removido** - Funcionalidades removidas
- **🐛 Arreglado** - Bug fixes
- **🔒 Seguridad** - Vulnerabilidades arregladas

### Versionado Semántico
- **MAJOR** (1.0.0): Cambios que rompen compatibilidad
- **MINOR** (0.1.0): Nuevas funcionalidades compatibles
- **PATCH** (0.0.1): Bug fixes compatibles