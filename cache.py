"""
Sistema de caché para datos meteorológicos
Soporta caché en memoria y Redis
"""
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class WeatherCache:
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL')
        self.use_redis = REDIS_AVAILABLE and self.redis_url
        
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                self.redis_client.ping()
                print("✅ Conectado a Redis para caché")
            except Exception as e:
                print(f"❌ Error conectando a Redis: {e}")
                self.use_redis = False
                self.memory_cache = {}
        else:
            self.memory_cache = {}
            print("📝 Usando caché en memoria")
    
    def _get_cache_key(self, city: str, data_type: str) -> str:
        """Genera clave única para el caché"""
        return f"weather:{city.lower().replace(' ', '_')}:{data_type}"
    
    def get(self, city: str, data_type: str) -> Optional[Dict[Any, Any]]:
        """Obtiene datos del caché"""
        key = self._get_cache_key(city, data_type)
        
        try:
            if self.use_redis:
                data = self.redis_client.get(key)
                if data:
                    cached_data = json.loads(data)
                    # Verificar si no ha expirado
                    if datetime.fromisoformat(cached_data['expires_at']) > datetime.now():
                        return cached_data['data']
                    else:
                        self.redis_client.delete(key)
            else:
                if key in self.memory_cache:
                    cached_data = self.memory_cache[key]
                    if datetime.fromisoformat(cached_data['expires_at']) > datetime.now():
                        return cached_data['data']
                    else:
                        del self.memory_cache[key]
        except Exception as e:
            print(f"Error obteniendo del caché: {e}")
        
        return None
    
    def set(self, city: str, data_type: str, data: Dict[Any, Any], ttl_minutes: int = 30):
        """Guarda datos en el caché"""
        key = self._get_cache_key(city, data_type)
        expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
        
        cached_data = {
            'data': data,
            'expires_at': expires_at.isoformat()
        }
        
        try:
            if self.use_redis:
                self.redis_client.setex(
                    key, 
                    ttl_minutes * 60, 
                    json.dumps(cached_data, default=str)
                )
            else:
                self.memory_cache[key] = cached_data
        except Exception as e:
            print(f"Error guardando en caché: {e}")
    
    def clear_expired(self):
        """Limpia entradas expiradas del caché en memoria"""
        if not self.use_redis:
            now = datetime.now()
            expired_keys = []
            for key, data in self.memory_cache.items():
                if datetime.fromisoformat(data['expires_at']) <= now:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]


# Instancia global del caché
weather_cache = WeatherCache()