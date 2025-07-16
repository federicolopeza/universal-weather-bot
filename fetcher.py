"""
Fetcher para obtener datos de múltiples APIs meteorológicas
"""
import os
import requests
import pytz
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from models import WeatherData, HourlyWeather, DailyWeather, CityInfo
from cache import weather_cache


class WeatherFetcher:
    def __init__(self):
        self.owm_key = os.getenv('OWM_KEY')
        self.weatherapi_key = os.getenv('WEATHERAPI_KEY')
        self.tomorrow_key = os.getenv('TOMORROW_KEY')
        self.visualcrossing_key = os.getenv('VISUALCROSSING_KEY')
    
    def get_city_info(self, city: str) -> Optional[CityInfo]:
        """Obtiene información de la ciudad usando OpenWeatherMap Geocoding"""
        if not self.owm_key:
            return None
        
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct"
            params = {
                'q': city,
                'limit': 1,
                'appid': self.owm_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return None
            
            location = data[0]
            
            # Obtener timezone usando coordenadas
            tz_url = f"http://api.openweathermap.org/data/2.5/weather"
            tz_params = {
                'lat': location['lat'],
                'lon': location['lon'],
                'appid': self.owm_key
            }
            
            tz_response = requests.get(tz_url, params=tz_params, timeout=10)
            tz_data = tz_response.json()
            
            # Calcular timezone offset
            timezone_offset = tz_data.get('timezone', 0)
            timezone_name = f"UTC{timezone_offset//3600:+d}"
            
            return CityInfo(
                name=location['name'],
                country=location['country'],
                latitude=location['lat'],
                longitude=location['lon'],
                timezone=timezone_name
            )
        except Exception as e:
            print(f"Error obteniendo info de ciudad: {e}")
            return None
    
    def fetch_openweathermap(self, city: str) -> Optional[WeatherData]:
        """Obtiene datos de OpenWeatherMap"""
        if not self.owm_key:
            return None
        
        # Verificar caché
        cached = weather_cache.get(city, 'openweathermap')
        if cached:
            return WeatherData(**cached)
        
        try:
            city_info = self.get_city_info(city)
            if not city_info:
                return None
            
            # OneCall API para datos completos
            url = "https://api.openweathermap.org/data/3.0/onecall"
            params = {
                'lat': city_info.latitude,
                'lon': city_info.longitude,
                'appid': self.owm_key,
                'units': 'metric',
                'exclude': 'minutely,alerts'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Procesar datos horarios
            hourly_data = []
            for hour in data.get('hourly', [])[:24]:  # Solo 24 horas
                hourly_data.append(HourlyWeather(
                    datetime=datetime.fromtimestamp(hour['dt']),
                    temperature=hour['temp'],
                    precipitation=hour.get('rain', {}).get('1h', 0) + hour.get('snow', {}).get('1h', 0),
                    wind_speed=hour['wind_speed'],
                    source='OpenWeatherMap'
                ))
            
            # Procesar datos diarios
            daily_data = []
            for day in data.get('daily', [])[:7]:  # 7 días
                daily_data.append(DailyWeather(
                    date=datetime.fromtimestamp(day['dt']),
                    temp_min=day['temp']['min'],
                    temp_max=day['temp']['max'],
                    precipitation=day.get('rain', 0) + day.get('snow', 0),
                    wind_speed=day['wind_speed'],
                    source='OpenWeatherMap'
                ))
            
            weather_data = WeatherData(
                city=city_info.name,
                country=city_info.country,
                timezone=city_info.timezone,
                hourly=hourly_data,
                daily=daily_data
            )
            
            # Guardar en caché
            weather_cache.set(city, 'openweathermap', weather_data.dict())
            return weather_data
            
        except Exception as e:
            print(f"Error con OpenWeatherMap: {e}")
            return None
    
    def fetch_metno(self, city: str) -> Optional[WeatherData]:
        """Obtiene datos de MET Norway"""
        try:
            city_info = self.get_city_info(city)
            if not city_info:
                return None
            
            # Verificar caché
            cached = weather_cache.get(city, 'metno')
            if cached:
                return WeatherData(**cached)
            
            url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
            params = {
                'lat': city_info.latitude,
                'lon': city_info.longitude
            }
            headers = {
                'User-Agent': 'UniversalWeatherBot/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            hourly_data = []
            daily_data = []
            
            # Procesar datos horarios
            for item in data['properties']['timeseries'][:24]:
                dt = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
                details = item['data']['instant']['details']
                
                precipitation = 0
                if 'next_1_hours' in item['data']:
                    precipitation = item['data']['next_1_hours']['details'].get('precipitation_amount', 0)
                
                hourly_data.append(HourlyWeather(
                    datetime=dt,
                    temperature=details['air_temperature'],
                    precipitation=precipitation,
                    wind_speed=details['wind_speed'],
                    source='MET Norway'
                ))
            
            # Agrupar por días para datos diarios
            daily_temps = {}
            daily_precip = {}
            daily_wind = {}
            
            for item in data['properties']['timeseries'][:168]:  # 7 días
                dt = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
                date_key = dt.date()
                details = item['data']['instant']['details']
                
                if date_key not in daily_temps:
                    daily_temps[date_key] = []
                    daily_precip[date_key] = []
                    daily_wind[date_key] = []
                
                daily_temps[date_key].append(details['air_temperature'])
                daily_wind[date_key].append(details['wind_speed'])
                
                if 'next_1_hours' in item['data']:
                    daily_precip[date_key].append(
                        item['data']['next_1_hours']['details'].get('precipitation_amount', 0)
                    )
            
            for date_key in list(daily_temps.keys())[:7]:
                daily_data.append(DailyWeather(
                    date=datetime.combine(date_key, datetime.min.time()),
                    temp_min=min(daily_temps[date_key]),
                    temp_max=max(daily_temps[date_key]),
                    precipitation=sum(daily_precip.get(date_key, [])),
                    wind_speed=sum(daily_wind[date_key]) / len(daily_wind[date_key]),
                    source='MET Norway'
                ))
            
            weather_data = WeatherData(
                city=city_info.name,
                country=city_info.country,
                timezone=city_info.timezone,
                hourly=hourly_data,
                daily=daily_data
            )
            
            # Guardar en caché
            weather_cache.set(city, 'metno', weather_data.dict())
            return weather_data
            
        except Exception as e:
            print(f"Error con MET Norway: {e}")
            return None
    
    def fetch_weatherapi(self, city: str) -> Optional[WeatherData]:
        """Obtiene datos de WeatherAPI"""
        if not self.weatherapi_key:
            return None
        
        # Verificar caché
        cached = weather_cache.get(city, 'weatherapi')
        if cached:
            return WeatherData(**cached)
        
        try:
            url = "http://api.weatherapi.com/v1/forecast.json"
            params = {
                'key': self.weatherapi_key,
                'q': city,
                'days': 7,
                'aqi': 'no',
                'alerts': 'no'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            location = data['location']
            
            # Datos horarios para hoy
            hourly_data = []
            today_forecast = data['forecast']['forecastday'][0]
            for hour in today_forecast['hour']:
                dt = datetime.strptime(hour['time'], '%Y-%m-%d %H:%M')
                hourly_data.append(HourlyWeather(
                    datetime=dt,
                    temperature=hour['temp_c'],
                    precipitation=hour['precip_mm'],
                    wind_speed=hour['wind_kph'] / 3.6,  # Convertir km/h a m/s
                    source='WeatherAPI'
                ))
            
            # Datos diarios
            daily_data = []
            for day in data['forecast']['forecastday']:
                dt = datetime.strptime(day['date'], '%Y-%m-%d')
                day_data = day['day']
                daily_data.append(DailyWeather(
                    date=dt,
                    temp_min=day_data['mintemp_c'],
                    temp_max=day_data['maxtemp_c'],
                    precipitation=day_data['totalprecip_mm'],
                    wind_speed=day_data['maxwind_kph'] / 3.6,  # Convertir km/h a m/s
                    source='WeatherAPI'
                ))
            
            weather_data = WeatherData(
                city=location['name'],
                country=location['country'],
                timezone=location['tz_id'],
                hourly=hourly_data,
                daily=daily_data
            )
            
            # Guardar en caché
            weather_cache.set(city, 'weatherapi', weather_data.dict())
            return weather_data
            
        except Exception as e:
            print(f"Error con WeatherAPI: {e}")
            return None
    
    def fetch_tomorrow(self, city: str) -> Optional[WeatherData]:
        """Obtiene datos de Tomorrow.io"""
        if not self.tomorrow_key:
            return None
        
        # Verificar caché
        cached = weather_cache.get(city, 'tomorrow')
        if cached:
            return WeatherData(**cached)
        
        try:
            city_info = self.get_city_info(city)
            if not city_info:
                return None
            
            url = "https://api.tomorrow.io/v4/timelines"
            params = {
                'location': f"{city_info.latitude},{city_info.longitude}",
                'fields': 'temperature,precipitationIntensity,windSpeed',
                'timesteps': '1h,1d',
                'units': 'metric',
                'apikey': self.tomorrow_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            hourly_data = []
            daily_data = []
            
            for timeline in data['data']['timelines']:
                if timeline['timestep'] == '1h':
                    # Datos horarios
                    for interval in timeline['intervals'][:24]:
                        dt = datetime.fromisoformat(interval['startTime'].replace('Z', '+00:00'))
                        values = interval['values']
                        hourly_data.append(HourlyWeather(
                            datetime=dt,
                            temperature=values['temperature'],
                            precipitation=values['precipitationIntensity'],
                            wind_speed=values['windSpeed'],
                            source='Tomorrow.io'
                        ))
                elif timeline['timestep'] == '1d':
                    # Datos diarios
                    for interval in timeline['intervals'][:7]:
                        dt = datetime.fromisoformat(interval['startTime'].replace('Z', '+00:00'))
                        values = interval['values']
                        daily_data.append(DailyWeather(
                            date=dt,
                            temp_min=values['temperature'] - 5,  # Aproximación
                            temp_max=values['temperature'] + 5,  # Aproximación
                            precipitation=values['precipitationIntensity'] * 24,
                            wind_speed=values['windSpeed'],
                            source='Tomorrow.io'
                        ))
            
            weather_data = WeatherData(
                city=city_info.name,
                country=city_info.country,
                timezone=city_info.timezone,
                hourly=hourly_data,
                daily=daily_data
            )
            
            # Guardar en caché
            weather_cache.set(city, 'tomorrow', weather_data.dict())
            return weather_data
            
        except Exception as e:
            print(f"Error con Tomorrow.io: {e}")
            return None
    
    def fetch_visualcrossing(self, city: str) -> Optional[WeatherData]:
        """Obtiene datos de Visual Crossing"""
        if not self.visualcrossing_key:
            return None
        
        # Verificar caché
        cached = weather_cache.get(city, 'visualcrossing')
        if cached:
            return WeatherData(**cached)
        
        try:
            url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}"
            params = {
                'key': self.visualcrossing_key,
                'unitGroup': 'metric',
                'include': 'hours,days',
                'elements': 'temp,tempmin,tempmax,precip,windspeed'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Datos horarios para hoy
            hourly_data = []
            if data['days']:
                today = data['days'][0]
                for hour in today.get('hours', []):
                    dt = datetime.strptime(f"{today['datetime']} {hour['datetime']}", '%Y-%m-%d %H:%M:%S')
                    hourly_data.append(HourlyWeather(
                        datetime=dt,
                        temperature=hour['temp'],
                        precipitation=hour.get('precip', 0),
                        wind_speed=hour['windspeed'] / 3.6,  # Convertir km/h a m/s
                        source='Visual Crossing'
                    ))
            
            # Datos diarios
            daily_data = []
            for day in data['days'][:7]:
                dt = datetime.strptime(day['datetime'], '%Y-%m-%d')
                daily_data.append(DailyWeather(
                    date=dt,
                    temp_min=day['tempmin'],
                    temp_max=day['tempmax'],
                    precipitation=day.get('precip', 0),
                    wind_speed=day['windspeed'] / 3.6,  # Convertir km/h a m/s
                    source='Visual Crossing'
                ))
            
            weather_data = WeatherData(
                city=data['resolvedAddress'].split(',')[0],
                country=data['resolvedAddress'].split(',')[-1].strip(),
                timezone=data['timezone'],
                hourly=hourly_data,
                daily=daily_data
            )
            
            # Guardar en caché
            weather_cache.set(city, 'visualcrossing', weather_data.dict())
            return weather_data
            
        except Exception as e:
            print(f"Error con Visual Crossing: {e}")
            return None


# Instancia global del fetcher
weather_fetcher = WeatherFetcher()