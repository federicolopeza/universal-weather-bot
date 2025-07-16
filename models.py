"""
Modelos de datos meteorológicos usando Pydantic
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class HourlyWeather(BaseModel):
    """Datos meteorológicos por hora"""
    datetime: datetime
    temperature: float = Field(description="Temperatura en °C")
    precipitation: float = Field(description="Precipitación en mm/h")
    wind_speed: float = Field(description="Velocidad del viento en m/s")
    source: str = Field(description="Fuente de los datos")


class DailyWeather(BaseModel):
    """Datos meteorológicos diarios"""
    date: datetime
    temp_min: float = Field(description="Temperatura mínima en °C")
    temp_max: float = Field(description="Temperatura máxima en °C")
    precipitation: float = Field(description="Precipitación total en mm")
    wind_speed: float = Field(description="Velocidad promedio del viento en m/s")
    source: str = Field(description="Fuente de los datos")


class WeatherData(BaseModel):
    """Datos meteorológicos completos"""
    city: str
    country: str
    timezone: str
    hourly: List[HourlyWeather] = []
    daily: List[DailyWeather] = []
    last_updated: datetime = Field(default_factory=datetime.now)


class CityInfo(BaseModel):
    """Información de la ciudad"""
    name: str
    country: str
    latitude: float
    longitude: float
    timezone: str