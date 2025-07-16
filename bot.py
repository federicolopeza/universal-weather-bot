"""
Bot de Telegram para pronósticos meteorológicos universales
"""
import os
import logging
from datetime import datetime, time
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode
from dotenv import load_dotenv
from aggregator import weather_aggregator
from cache import weather_cache
import asyncio
import requests

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class UniversalWeatherBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en .env")
        
        self.group_chat_id = os.getenv('GROUP_CHAT_ID')
        self.default_city = os.getenv('DEFAULT_CITY', 'Montevideo')
        
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura los manejadores de comandos"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("tiempo", self.weather_command))
        self.application.add_handler(CommandHandler("chatid", self.get_chat_id))
        self.application.add_handler(CommandHandler("actualizar", self.manual_update_command))
        self.application.add_handler(CommandHandler("matutino", self.morning_update_command))
        self.application.add_handler(CommandHandler("vespertino", self.evening_update_command))
        self.application.add_handler(CommandHandler("ubicacion", self.location_weather_command))
        self.application.add_handler(MessageHandler(filters.LOCATION, self.handle_location))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        welcome_message = """
🌤️ **Bienvenido a Universal Weather Bot**

Obtén pronósticos meteorológicos precisos para cualquier ciudad del mundo.

**Comandos disponibles:**
• `/ubicacion` - 📍 Pronóstico de tu ubicación actual
• `/tiempo hoy <ciudad>` - Pronóstico horario para hoy
• `/tiempo semana <ciudad>` - Pronóstico semanal
• `/help` - Mostrar esta ayuda

**Ejemplos:**
• `/ubicacion` - ¡Comparte tu ubicación!
• `/tiempo hoy Madrid`
• `/tiempo semana Buenos Aires`

¡Comienza escribiendo un comando! 🚀
        """
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_message = """
🌤️ **Universal Weather Bot - Ayuda**

**Comandos básicos:**
• `/ubicacion` - 📍 Pronóstico de tu ubicación actual
• `/tiempo hoy <ciudad>` - Pronóstico horario (00:00 - 23:00)
• `/tiempo semana <ciudad>` - Pronóstico de 7 días

**Comandos para grupos:**
• `/actualizar [ciudad]` - Envía actualización al grupo
• `/matutino` - Envía pronóstico matutino al grupo
• `/vespertino` - Envía pronóstico semanal al grupo
• `/chatid` - Obtiene ID del chat para configuración

**Información mostrada:**
📊 **Pronóstico horario:**
• Temperatura (°C)
• Precipitación (mm/h)
• Viento (km/h)

📅 **Pronóstico semanal:**
• Temperatura mín/máx (°C)
• Precipitación total (mm)
• Viento promedio (km/h)

**Fuentes de datos:**
• OpenWeatherMap
• MET Norway
• WeatherAPI
• Tomorrow.io
• Visual Crossing

Los datos se combinan inteligentemente para mayor precisión.
        """
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def get_chat_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para obtener el ID del chat"""
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        chat_title = update.effective_chat.title or "Chat privado"
        
        message = f"""
📋 **Información del Chat**

🆔 **ID del Chat**: `{chat_id}`
📝 **Tipo**: {chat_type}
🏷️ **Nombre**: {chat_title}

💡 **Para configurar actualizaciones automáticas:**
Agrega este ID al archivo .env como `GROUP_CHAT_ID={chat_id}`
        """
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /tiempo"""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ **Uso incorrecto**\n\n"
                "**Formato correcto:**\n"
                "• `/tiempo hoy <ciudad>`\n"
                "• `/tiempo semana <ciudad>`\n\n"
                "**Ejemplos:**\n"
                "• `/tiempo hoy Madrid`\n"
                "• `/tiempo semana Buenos Aires`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        command_type = context.args[0].lower()
        city = ' '.join(context.args[1:])
        
        if command_type not in ['hoy', 'semana']:
            await update.message.reply_text(
                "❌ **Comando no válido**\n\n"
                "Usa `hoy` o `semana`:\n"
                "• `/tiempo hoy <ciudad>`\n"
                "• `/tiempo semana <ciudad>`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Mostrar mensaje de carga
        loading_msg = await update.message.reply_text(
            f"🔄 Obteniendo pronóstico para **{city}**...\n"
            "Consultando múltiples fuentes meteorológicas...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Obtener datos agregados
            weather_data = weather_aggregator.get_aggregated_weather(city)
            
            if not weather_data:
                await loading_msg.edit_text(
                    f"❌ **Ciudad no encontrada**\n\n"
                    f"No se pudo obtener información meteorológica para: **{city}**\n\n"
                    "Verifica que el nombre de la ciudad sea correcto.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Generar respuesta según el tipo de comando
            if command_type == 'hoy':
                response = self._format_hourly_weather(weather_data)
            else:  # semana
                response = self._format_daily_weather(weather_data)
            
            await loading_msg.edit_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error procesando comando weather: {e}")
            await loading_msg.edit_text(
                "❌ **Error interno**\n\n"
                "Ocurrió un error al obtener los datos meteorológicos. "
                "Por favor, inténtalo de nuevo en unos minutos.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    def _get_weather_emoji(self, temp, precipitation, wind_speed):
        """Obtiene el emoji del clima según las condiciones"""
        if precipitation > 5.0:
            if temp < 2:
                return "🌨️"  # Nieve
            elif precipitation > 10:
                return "⛈️"  # Tormenta
            else:
                return "🌧️"  # Lluvia
        elif precipitation > 0.5:
            return "🌦️"  # Lluvia ligera
        elif wind_speed > 8:
            return "💨"  # Viento fuerte
        elif temp > 25:
            return "☀️"  # Soleado caliente
        elif temp > 15:
            return "🌤️"  # Parcialmente nublado
        elif temp > 5:
            return "⛅"  # Nublado
        else:
            return "🌫️"  # Frío/niebla
    
    def _get_rain_probability(self, precipitation):
        """Calcula la probabilidad de lluvia basada en precipitación"""
        if precipitation == 0:
            return 0
        elif precipitation < 0.1:
            return 10
        elif precipitation < 0.5:
            return 30
        elif precipitation < 2.0:
            return 60
        elif precipitation < 5.0:
            return 80
        else:
            return 95
    
    def _get_temp_color_emoji(self, temp):
        """Obtiene emoji de color según temperatura"""
        if temp >= 30:
            return "🔴"  # Muy caliente
        elif temp >= 25:
            return "🟠"  # Caliente
        elif temp >= 20:
            return "🟡"  # Templado
        elif temp >= 15:
            return "🟢"  # Agradable
        elif temp >= 10:
            return "🔵"  # Fresco
        elif temp >= 5:
            return "🟣"  # Frío
        else:
            return "⚪"  # Muy frío
    
    def _format_hourly_weather(self, weather_data) -> str:
        """Formatea el pronóstico horario con diseño moderno"""
        if not weather_data.hourly:
            return "❌ No hay datos horarios disponibles"
        
        # Header con información de la ciudad
        header = f"🌍 **{weather_data.city}, {weather_data.country}**\n"
        header += f"📅 {datetime.now().strftime('%A, %d de %B %Y')}\n"
        header += f"🕐 {weather_data.timezone}\n\n"
        
        # Pronóstico por horas con diseño moderno (sin tablas markdown)
        forecast_text = "⏰ **Pronóstico por horas:**\n\n"
        
        # Agrupar por bloques de 6 horas para mejor legibilidad
        time_blocks = [
            ("🌅 Madrugada", weather_data.hourly[0:6]),
            ("☀️ Mañana", weather_data.hourly[6:12]),
            ("🌞 Tarde", weather_data.hourly[12:18]),
            ("🌙 Noche", weather_data.hourly[18:24])
        ]
        
        for block_name, hours in time_blocks:
            if not hours:
                continue
                
            forecast_text += f"{block_name}\n"
            
            for hour_data in hours:
                hour_str = hour_data.datetime.strftime("%H:%M")
                temp = hour_data.temperature
                precip = hour_data.precipitation
                wind_kmh = hour_data.wind_speed * 3.6  # Convertir m/s a km/h
                
                # Obtener emoji del clima para esta hora
                weather_emoji = self._get_weather_emoji(temp, precip, hour_data.wind_speed)
                temp_emoji = self._get_temp_color_emoji(temp)
                
                # Probabilidad de lluvia
                rain_prob = self._get_rain_probability(precip)
                
                # Formatear línea de pronóstico
                line = f"{hour_str} {weather_emoji} {temp_emoji} **{temp:.1f}°C**"
                
                if precip > 0:
                    line += f" 🌧️ {precip:.1f}mm ({rain_prob}%)"
                else:
                    line += f" ☀️ Sin lluvia"
                
                line += f" 💨 {wind_kmh:.0f}km/h\n"
                forecast_text += line
            
            forecast_text += "\n"
        
        # Resumen visual del día
        temps = [h.temperature for h in weather_data.hourly[:24]]
        precips = [h.precipitation for h in weather_data.hourly[:24]]
        winds = [h.wind_speed * 3.6 for h in weather_data.hourly[:24]]  # Convertir a km/h
        
        min_temp = min(temps)
        max_temp = max(temps)
        total_precip = sum(precips)
        avg_wind = sum(winds) / len(winds)
        max_precip = max(precips)
        
        # Condiciones destacadas
        weather_emoji = self._get_weather_emoji(max_temp, max_precip, max(winds)/3.6)
        temp_emoji = self._get_temp_color_emoji(max_temp)
        
        summary = f"{weather_emoji} **Resumen del día:**\n\n"
        summary += f"{temp_emoji} **Temperatura:** {min_temp:.1f}°C - {max_temp:.1f}°C\n"
        
        if total_precip > 0:
            rain_prob = self._get_rain_probability(max_precip)
            summary += f"🌧️ **Precipitación:** {total_precip:.1f}mm total ({rain_prob}% prob.)\n"
        else:
            summary += f"☀️ **Sin lluvia** esperada hoy\n"
        
        # Clasificación del viento (ahora en km/h)
        if avg_wind < 7:
            wind_desc = "Calma"
        elif avg_wind < 18:
            wind_desc = "Brisa ligera"
        elif avg_wind < 29:
            wind_desc = "Brisa moderada"
        elif avg_wind < 43:
            wind_desc = "Viento fuerte"
        else:
            wind_desc = "Viento muy fuerte"
        
        summary += f"💨 **Viento:** {avg_wind:.0f}km/h ({wind_desc})\n\n"
        
        # Recomendaciones
        recommendations = "💡 **Recomendaciones:**\n"
        if max_temp > 25:
            recommendations += "• ☀️ Usa protector solar y mantente hidratado\n"
        if total_precip > 2:
            recommendations += "• ☔ Lleva paraguas o impermeable\n"
        if avg_wind > 29:  # Más de 29 km/h
            recommendations += "• 💨 Cuidado con objetos que puedan volar\n"
        if min_temp < 10:
            recommendations += "• 🧥 Abrígate bien, especialmente en la mañana\n"
        
        if recommendations == "💡 **Recomendaciones:**\n":
            recommendations += "• 😊 ¡Día perfecto para actividades al aire libre!\n"
        
        recommendations += f"\n🔄 **Actualizado:** {weather_data.last_updated.strftime('%H:%M')}"
        
        return header + forecast_text + summary + recommendations
    
    def _get_day_emoji(self, day_name):
        """Obtiene emoji para cada día de la semana"""
        day_emojis = {
            'Mon': '🌙', 'Tue': '🔥', 'Wed': '🌊', 'Thu': '⚡', 
            'Fri': '🌟', 'Sat': '🎉', 'Sun': '☀️'
        }
        return day_emojis.get(day_name, '📅')
    
    def _format_daily_weather(self, weather_data) -> str:
        """Formatea el pronóstico semanal con diseño moderno"""
        if not weather_data.daily:
            return "❌ No hay datos diarios disponibles"
        
        # Header con información de la ciudad
        header = f"🗓️ **{weather_data.city}, {weather_data.country}**\n"
        header += f"📅 Pronóstico de 7 días\n"
        header += f"🕐 {weather_data.timezone}\n\n"
        
        # Pronóstico semanal con diseño moderno (sin tablas markdown)
        forecast_text = "📅 **Pronóstico semanal:**\n\n"
        
        for day_data in weather_data.daily[:7]:
            date_str = day_data.date.strftime("%d/%m")
            day_name_full = day_data.date.strftime("%A")
            day_name_short = day_data.date.strftime("%a")
            
            # Formatear datos
            temp_min = day_data.temp_min
            temp_max = day_data.temp_max
            precip = day_data.precipitation
            wind_kmh = day_data.wind_speed * 3.6  # Convertir m/s a km/h
            
            # Obtener emojis para este día
            day_emoji = self._get_day_emoji(day_name_short)
            weather_emoji = self._get_weather_emoji(temp_max, precip, day_data.wind_speed)
            temp_emoji = self._get_temp_color_emoji(temp_max)
            
            # Probabilidad de lluvia
            rain_prob = self._get_rain_probability(precip)
            
            # Formatear línea del día
            day_line = f"{day_emoji} **{day_name_full} {date_str}**\n"
            day_line += f"{weather_emoji} {temp_emoji} **{temp_min:.1f}°C - {temp_max:.1f}°C**"
            
            if precip > 0:
                day_line += f" 🌧️ {precip:.1f}mm ({rain_prob}%)"
            else:
                day_line += f" ☀️ Sin lluvia"
            
            day_line += f" 💨 {wind_kmh:.0f}km/h\n\n"
            forecast_text += day_line
        
        # Análisis semanal detallado
        min_temps = [d.temp_min for d in weather_data.daily[:7]]
        max_temps = [d.temp_max for d in weather_data.daily[:7]]
        precips = [d.precipitation for d in weather_data.daily[:7]]
        winds = [d.wind_speed for d in weather_data.daily[:7]]
        
        min_week_temp = min(min_temps)
        max_week_temp = max(max_temps)
        total_precip = sum(precips)
        avg_wind = sum(winds) / len(winds)
        max_daily_precip = max(precips)
        
        # Día más caluroso y más frío
        hottest_day_idx = max_temps.index(max_week_temp)
        coldest_day_idx = min_temps.index(min_week_temp)
        rainiest_day_idx = precips.index(max_daily_precip)
        
        hottest_day = weather_data.daily[hottest_day_idx].date.strftime("%A")
        coldest_day = weather_data.daily[coldest_day_idx].date.strftime("%A")
        rainiest_day = weather_data.daily[rainiest_day_idx].date.strftime("%A")
        
        # Condiciones destacadas de la semana
        week_weather_emoji = self._get_weather_emoji(max_week_temp, max_daily_precip, max(winds))
        temp_emoji = self._get_temp_color_emoji(max_week_temp)
        
        summary = f"{week_weather_emoji} **Resumen de la semana:**\n\n"
        summary += f"{temp_emoji} **Temperaturas:** {min_week_temp:.1f}°C - {max_week_temp:.1f}°C\n"
        summary += f"🔥 **Día más caluroso:** {hottest_day} ({max_week_temp:.1f}°C)\n"
        summary += f"🧊 **Día más frío:** {coldest_day} ({min_week_temp:.1f}°C)\n\n"
        
        if total_precip > 0:
            rain_days = sum(1 for p in precips if p > 0.5)
            summary += f"🌧️ **Precipitación:** {total_precip:.1f}mm total\n"
            summary += f"☔ **Días con lluvia:** {rain_days} de 7\n"
            if max_daily_precip > 2:
                summary += f"🌊 **Día más lluvioso:** {rainiest_day} ({max_daily_precip:.1f}mm)\n"
        else:
            summary += f"☀️ **Semana seca:** Sin lluvia esperada\n"
        
        avg_wind_kmh = avg_wind * 3.6  # Convertir a km/h
        summary += f"\n💨 **Viento promedio:** {avg_wind_kmh:.0f}km/h\n"
        
        # Clasificación del viento semanal (en km/h)
        if avg_wind_kmh < 11:
            wind_desc = "Vientos suaves"
        elif avg_wind_kmh < 22:
            wind_desc = "Brisas moderadas"
        elif avg_wind_kmh < 36:
            wind_desc = "Vientos fuertes"
        else:
            wind_desc = "Vientos muy fuertes"
        
        summary += f"🌪️ **Condición:** {wind_desc}\n\n"
        
        # Recomendaciones semanales
        recommendations = "📋 **Recomendaciones para la semana:**\n"
        
        if max_week_temp > 28:
            recommendations += "• 🌞 Semana calurosa - mantente hidratado\n"
        if min_week_temp < 5:
            recommendations += "• 🧥 Prepara ropa de abrigo para los días fríos\n"
        if total_precip > 10:
            recommendations += "• ☔ Semana lluviosa - ten paraguas a mano\n"
        if avg_wind > 8:
            recommendations += "• 💨 Vientos fuertes esperados - precaución al aire libre\n"
        
        # Mejor día de la semana
        best_day_score = []
        for i, day in enumerate(weather_data.daily[:7]):
            score = 0
            # Temperatura ideal (15-25°C)
            if 15 <= day.temp_max <= 25:
                score += 3
            elif 10 <= day.temp_max <= 30:
                score += 2
            else:
                score += 1
            
            # Poca lluvia
            if day.precipitation < 0.5:
                score += 3
            elif day.precipitation < 2:
                score += 2
            else:
                score += 1
            
            # Viento moderado
            if day.wind_speed < 5:
                score += 2
            elif day.wind_speed < 8:
                score += 1
            
            best_day_score.append((score, i, day))
        
        best_day = max(best_day_score, key=lambda x: x[0])
        best_day_name = best_day[2].date.strftime("%A")
        
        recommendations += f"• 🌟 **Mejor día:** {best_day_name} - ideal para actividades\n"
        
        if not any([max_week_temp > 28, min_week_temp < 5, total_precip > 10, avg_wind > 8]):
            recommendations += "• 😊 ¡Excelente semana para planes al aire libre!\n"
        
        recommendations += f"\n🔄 **Actualizado:** {weather_data.last_updated.strftime('%d/%m/%Y %H:%M')}"
        
        return header + forecast_text + summary + recommendations
    
    async def send_morning_weather(self):
        """Envía el pronóstico matutino al grupo"""
        if not self.group_chat_id:
            logger.warning("GROUP_CHAT_ID no configurado, no se pueden enviar actualizaciones automáticas")
            return
        
        try:
            weather_data = weather_aggregator.get_aggregated_weather(self.default_city)
            if weather_data:
                message = f"🌅 **Buenos días! Pronóstico para hoy**\n\n"
                message += self._format_hourly_weather(weather_data)
                
                await self.application.bot.send_message(
                    chat_id=self.group_chat_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"Pronóstico matutino enviado al grupo {self.group_chat_id}")
            else:
                logger.error(f"No se pudo obtener datos meteorológicos para {self.default_city}")
                
        except Exception as e:
            logger.error(f"Error enviando pronóstico matutino: {e}")
    
    async def send_evening_weather(self):
        """Envía el pronóstico vespertino al grupo"""
        if not self.group_chat_id:
            logger.warning("GROUP_CHAT_ID no configurado, no se pueden enviar actualizaciones automáticas")
            return
        
        try:
            weather_data = weather_aggregator.get_aggregated_weather(self.default_city)
            if weather_data:
                message = f"🌆 **Pronóstico para mañana**\n\n"
                message += self._format_daily_weather(weather_data)
                
                await self.application.bot.send_message(
                    chat_id=self.group_chat_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"Pronóstico vespertino enviado al grupo {self.group_chat_id}")
            else:
                logger.error(f"No se pudo obtener datos meteorológicos para {self.default_city}")
                
        except Exception as e:
            logger.error(f"Error enviando pronóstico vespertino: {e}")
    
    async def send_manual_update(self, city=None):
        """Envía una actualización manual al grupo"""
        if not self.group_chat_id:
            logger.warning("GROUP_CHAT_ID no configurado")
            return
        
        city = city or self.default_city
        
        try:
            weather_data = weather_aggregator.get_aggregated_weather(city)
            if weather_data:
                message = f"🔄 **Actualización del tiempo - {city}**\n\n"
                message += self._format_hourly_weather(weather_data)
                
                await self.application.bot.send_message(
                    chat_id=self.group_chat_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"Actualización manual enviada al grupo {self.group_chat_id}")
                return True
            else:
                logger.error(f"No se pudo obtener datos meteorológicos para {city}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando actualización manual: {e}")
            return False
    
    async def manual_update_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /actualizar - Envía actualización manual al grupo"""
        city = ' '.join(context.args) if context.args else self.default_city
        
        loading_msg = await update.message.reply_text(
            f"🔄 Enviando actualización del tiempo para **{city}** al grupo...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        success = await self.send_manual_update(city)
        
        if success:
            await loading_msg.edit_text(
                f"✅ **Actualización enviada**\n\n"
                f"Se envió el pronóstico de **{city}** al grupo correctamente.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await loading_msg.edit_text(
                f"❌ **Error**\n\n"
                f"No se pudo enviar la actualización para **{city}**.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def morning_update_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /matutino - Envía pronóstico matutino al grupo"""
        loading_msg = await update.message.reply_text(
            "🌅 Enviando pronóstico matutino al grupo...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            await self.send_morning_weather()
            await loading_msg.edit_text(
                "✅ **Pronóstico matutino enviado**\n\n"
                "Se envió el pronóstico del día al grupo correctamente.",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error en comando matutino: {e}")
            await loading_msg.edit_text(
                "❌ **Error**\n\n"
                "No se pudo enviar el pronóstico matutino.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def evening_update_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /vespertino - Envía pronóstico vespertino al grupo"""
        loading_msg = await update.message.reply_text(
            "🌆 Enviando pronóstico vespertino al grupo...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            await self.send_evening_weather()
            await loading_msg.edit_text(
                "✅ **Pronóstico vespertino enviado**\n\n"
                "Se envió el pronóstico semanal al grupo correctamente.",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error en comando vespertino: {e}")
            await loading_msg.edit_text(
                "❌ **Error**\n\n"
                "No se pudo enviar el pronóstico vespertino.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def location_weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ubicacion - Solicita ubicación del usuario"""
        # Crear botón para solicitar ubicación
        location_button = KeyboardButton(
            text="📍 Compartir mi ubicación",
            request_location=True
        )
        
        keyboard = ReplyKeyboardMarkup(
            [[location_button]],
            one_time_keyboard=True,
            resize_keyboard=True
        )
        
        await update.message.reply_text(
            "📍 **Pronóstico por ubicación**\n\n"
            "Para obtener el pronóstico de tu ubicación actual, "
            "toca el botón de abajo para compartir tu ubicación GPS.\n\n"
            "🔒 **Privacidad:** Tu ubicación solo se usa para obtener el pronóstico "
            "y no se almacena.",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja la ubicación enviada por el usuario"""
        location = update.message.location
        latitude = location.latitude
        longitude = location.longitude
        
        # Remover el teclado personalizado
        from telegram import ReplyKeyboardRemove
        await update.message.reply_text(
            "📍 **Ubicación recibida**\n\n"
            f"🌐 Coordenadas: {latitude:.4f}, {longitude:.4f}\n"
            "🔄 Obteniendo nombre de la ciudad y pronóstico...",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Obtener nombre de la ciudad usando geocodificación inversa
            city_name = await self._get_city_from_coordinates(latitude, longitude)
            
            if not city_name:
                await update.message.reply_text(
                    "❌ **Error de ubicación**\n\n"
                    "No se pudo determinar la ciudad de tu ubicación. "
                    "Intenta con una ubicación más específica o usa el comando "
                    "`/tiempo hoy <ciudad>` manualmente.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Mostrar mensaje de carga con la ciudad encontrada
            loading_msg = await update.message.reply_text(
                f"🏙️ **Ciudad encontrada:** {city_name}\n\n"
                "🔄 Obteniendo pronóstico meteorológico...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Obtener datos meteorológicos
            weather_data = weather_aggregator.get_aggregated_weather(city_name)
            
            if not weather_data:
                await loading_msg.edit_text(
                    f"❌ **Sin datos meteorológicos**\n\n"
                    f"No se pudo obtener información meteorológica para **{city_name}**.\n\n"
                    "Intenta de nuevo en unos minutos.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Generar respuesta con pronóstico horario por defecto
            response = f"📍 **Pronóstico para tu ubicación**\n\n"
            response += self._format_hourly_weather(weather_data)
            
            await loading_msg.edit_text(response, parse_mode=ParseMode.MARKDOWN)
            
            # Ofrecer opciones adicionales
            await update.message.reply_text(
                "💡 **¿Quieres más información?**\n\n"
                f"• `/tiempo semana {city_name}` - Pronóstico de 7 días\n"
                f"• `/actualizar {city_name}` - Enviar al grupo (si está configurado)\n\n"
                "O simplemente envía tu ubicación de nuevo para actualizar.",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error procesando ubicación: {e}")
            await update.message.reply_text(
                "❌ **Error interno**\n\n"
                "Ocurrió un error al procesar tu ubicación. "
                "Por favor, inténtalo de nuevo en unos minutos.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def _get_city_from_coordinates(self, latitude: float, longitude: float) -> str:
        """Obtiene el nombre de la ciudad usando geocodificación inversa"""
        try:
            # Intentar con OpenWeatherMap primero (si está configurado)
            owm_key = os.getenv('OWM_KEY')
            if owm_key and owm_key != 'your_openweathermap_api_key_here':
                url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={latitude}&lon={longitude}&limit=1&appid={owm_key}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        city = data[0].get('name', '')
                        country = data[0].get('country', '')
                        if city:
                            return f"{city}, {country}" if country else city
            
            # Alternativa: usar un servicio gratuito de geocodificación
            # Nominatim (OpenStreetMap) - gratuito pero con límites de uso
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=10&addressdetails=1"
            headers = {'User-Agent': 'UniversalWeatherBot/1.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                
                # Intentar obtener la ciudad de diferentes campos
                city = (address.get('city') or 
                       address.get('town') or 
                       address.get('village') or 
                       address.get('municipality') or
                       address.get('county'))
                
                country = address.get('country')
                
                if city:
                    return f"{city}, {country}" if country else city
                elif country:
                    return country
            
            return None
            
        except Exception as e:
            logger.error(f"Error en geocodificación inversa: {e}")
            return None
    
    def run(self):
        """Ejecuta el bot"""
        print("🤖 Iniciando Universal Weather Bot...")
        print("🔄 Limpiando caché expirado...")
        weather_cache.clear_expired()
        print("✅ Bot iniciado correctamente")
        
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Función principal"""
    try:
        bot = UniversalWeatherBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        logger.error(f"Error crítico: {e}")


if __name__ == '__main__':
    main()