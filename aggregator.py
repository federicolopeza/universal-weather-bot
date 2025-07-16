"""
Agregador inteligente para combinar datos de múltiples fuentes meteorológicas
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics
from models import WeatherData, HourlyWeather, DailyWeather
from fetcher import weather_fetcher


class WeatherAggregator:
    def __init__(self):
        self.source_weights = {
            'OpenWeatherMap': 0.25,
            'MET Norway': 0.25,
            'WeatherAPI': 0.20,
            'Tomorrow.io': 0.15,
            'Visual Crossing': 0.15
        }
    
    def get_aggregated_weather(self, city: str) -> Optional[WeatherData]:
        """Obtiene y agrega datos de todas las fuentes disponibles"""
        sources_data = []
        
        # Obtener datos de todas las fuentes
        fetchers = [
            weather_fetcher.fetch_openweathermap,
            weather_fetcher.fetch_metno,
            weather_fetcher.fetch_weatherapi,
            weather_fetcher.fetch_tomorrow,
            weather_fetcher.fetch_visualcrossing
        ]
        
        for fetcher in fetchers:
            try:
                data = fetcher(city)
                if data:
                    sources_data.append(data)
                    print(f"✅ Datos obtenidos de {data.hourly[0].source if data.hourly else 'fuente desconocida'}")
            except Exception as e:
                print(f"❌ Error obteniendo datos: {e}")
        
        if not sources_data:
            return None
        
        # Usar la primera fuente como base para información de ciudad
        base_data = sources_data[0]
        
        # Agregar datos horarios
        aggregated_hourly = self._aggregate_hourly_data(sources_data)
        
        # Agregar datos diarios
        aggregated_daily = self._aggregate_daily_data(sources_data)
        
        return WeatherData(
            city=base_data.city,
            country=base_data.country,
            timezone=base_data.timezone,
            hourly=aggregated_hourly,
            daily=aggregated_daily
        )
    
    def _aggregate_hourly_data(self, sources_data: List[WeatherData]) -> List[HourlyWeather]:
        """Agrega datos horarios de múltiples fuentes"""
        # Agrupar por hora
        hourly_groups = {}
        
        for source in sources_data:
            for hour_data in source.hourly:
                # Redondear a la hora más cercana y normalizar timezone
                dt = hour_data.datetime
                if dt.tzinfo is not None:
                    # Convertir a UTC y luego remover timezone info para comparación
                    dt = dt.utctimetuple()
                    dt = datetime(*dt[:6])
                
                hour_key = dt.replace(minute=0, second=0, microsecond=0)
                
                if hour_key not in hourly_groups:
                    hourly_groups[hour_key] = []
                
                hourly_groups[hour_key].append(hour_data)
        
        # Agregar datos para cada hora
        aggregated_hourly = []
        for hour_key in sorted(hourly_groups.keys())[:24]:  # Solo 24 horas
            hour_group = hourly_groups[hour_key]
            
            # Calcular promedios ponderados
            temp_values = []
            precip_values = []
            wind_values = []
            weights = []
            
            for hour_data in hour_group:
                weight = self.source_weights.get(hour_data.source, 0.1)
                temp_values.append(hour_data.temperature * weight)
                precip_values.append(hour_data.precipitation * weight)
                wind_values.append(hour_data.wind_speed * weight)
                weights.append(weight)
            
            total_weight = sum(weights)
            if total_weight > 0:
                avg_temp = sum(temp_values) / total_weight
                avg_precip = sum(precip_values) / total_weight
                avg_wind = sum(wind_values) / total_weight
            else:
                avg_temp = statistics.mean([h.temperature for h in hour_group])
                avg_precip = statistics.mean([h.precipitation for h in hour_group])
                avg_wind = statistics.mean([h.wind_speed for h in hour_group])
            
            aggregated_hourly.append(HourlyWeather(
                datetime=hour_key,
                temperature=round(avg_temp, 1),
                precipitation=round(avg_precip, 2),
                wind_speed=round(avg_wind, 1),
                source=f"Agregado ({len(hour_group)} fuentes)"
            ))
        
        return aggregated_hourly
    
    def _aggregate_daily_data(self, sources_data: List[WeatherData]) -> List[DailyWeather]:
        """Agrega datos diarios de múltiples fuentes"""
        # Agrupar por día
        daily_groups = {}
        
        for source in sources_data:
            for day_data in source.daily:
                # Normalizar fecha para comparación
                dt = day_data.date
                if hasattr(dt, 'date'):
                    day_key = dt.date()
                else:
                    day_key = dt
                
                if day_key not in daily_groups:
                    daily_groups[day_key] = []
                
                daily_groups[day_key].append(day_data)
        
        # Agregar datos para cada día
        aggregated_daily = []
        for day_key in sorted(daily_groups.keys())[:7]:  # Solo 7 días
            day_group = daily_groups[day_key]
            
            # Calcular promedios ponderados
            temp_min_values = []
            temp_max_values = []
            precip_values = []
            wind_values = []
            weights = []
            
            for day_data in day_group:
                weight = self.source_weights.get(day_data.source, 0.1)
                temp_min_values.append(day_data.temp_min * weight)
                temp_max_values.append(day_data.temp_max * weight)
                precip_values.append(day_data.precipitation * weight)
                wind_values.append(day_data.wind_speed * weight)
                weights.append(weight)
            
            total_weight = sum(weights)
            if total_weight > 0:
                avg_temp_min = sum(temp_min_values) / total_weight
                avg_temp_max = sum(temp_max_values) / total_weight
                avg_precip = sum(precip_values) / total_weight
                avg_wind = sum(wind_values) / total_weight
            else:
                avg_temp_min = statistics.mean([d.temp_min for d in day_group])
                avg_temp_max = statistics.mean([d.temp_max for d in day_group])
                avg_precip = statistics.mean([d.precipitation for d in day_group])
                avg_wind = statistics.mean([d.wind_speed for d in day_group])
            
            aggregated_daily.append(DailyWeather(
                date=datetime.combine(day_key, datetime.min.time()),
                temp_min=round(avg_temp_min, 1),
                temp_max=round(avg_temp_max, 1),
                precipitation=round(avg_precip, 2),
                wind_speed=round(avg_wind, 1),
                source=f"Agregado ({len(day_group)} fuentes)"
            ))
        
        return aggregated_daily


def predict_weather_ml(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stub para predicción meteorológica con Machine Learning
    
    Esta función está preparada para futuras implementaciones de ML
    que podrían incluir:
    - Modelos de regresión para temperatura
    - Clasificadores para precipitación
    - Redes neuronales para patrones complejos
    - Análisis de series temporales
    
    Args:
        data: Diccionario con datos meteorológicos históricos y actuales
    
    Returns:
        Diccionario con predicciones mejoradas
    """
    # TODO: Implementar modelo de ML
    # Posibles librerías: scikit-learn, xgboost, tensorflow
    
    # Por ahora, retorna los datos sin modificar
    return data


# Instancia global del agregador
weather_aggregator = WeatherAggregator()