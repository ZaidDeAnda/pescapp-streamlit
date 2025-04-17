from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
from datetime import datetime
import pytz

@dataclass
class Coordinates:
    """Modelo para coordenadas geográficas"""
    lat: float
    lon: float
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Coordinates':
        """Crear objeto Coordinates desde un diccionario"""
        return cls(
            lat=data.get('lat', 0.0),
            lon=data.get('lon', 0.0)
        )
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        return {
            'lat': self.lat,
            'lon': self.lon
        }

@dataclass
class Travel:
    """Modelo para viajes"""
    travel_id: str
    user_id: str
    timestamp: str
    type: str = "travel"
    user_email: Optional[str] = None
    end_timestamp: Optional[str] = None
    initial_coords: Optional[Coordinates] = None
    final_coords: Optional[Coordinates] = None
    coords: Optional[Coordinates] = None
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    distance: Optional[float] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Travel':
        """Crear objeto Travel desde un diccionario"""
        # Crear objeto Travel base
        travel = cls(
            travel_id=data.get('travel_id') or data.get('id', ''),
            user_id=data.get('user_id', ''),
            timestamp=data.get('timestamp', ''),
            type=data.get('type', 'travel'),
            user_email=data.get('user_email'),
            end_timestamp=data.get('end_timestamp'),
            accuracy=data.get('accuracy'),
            altitude=data.get('altitude'),
            speed=data.get('speed'),
            distance=data.get('distance'),
            duration=data.get('duration')
        )
        
        # Procesar coordenadas
        if 'coords' in data and data['coords']:
            travel.coords = Coordinates.from_dict(data['coords'])
        
        if 'initial_coords' in data and data['initial_coords']:
            travel.initial_coords = Coordinates.from_dict(data['initial_coords'])
        
        if 'final_coords' in data and data['final_coords']:
            travel.final_coords = Coordinates.from_dict(data['final_coords'])
        
        # Almacenar cualquier campo adicional en metadata
        excluded_fields = {
            'travel_id', 'id', 'user_id', 'timestamp', 'type', 'user_email',
            'end_timestamp', 'coords', 'initial_coords', 'final_coords',
            'accuracy', 'altitude', 'speed', 'distance', 'duration'
        }
        
        travel.metadata = {
            k: v for k, v in data.items() if k not in excluded_fields
        }
        
        return travel
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        result = {
            'travel_id': self.travel_id,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'type': self.type
        }
        
        # Añadir campos opcionales si existen
        if self.user_email:
            result['user_email'] = self.user_email
        
        if self.end_timestamp:
            result['end_timestamp'] = self.end_timestamp
        
        if self.coords:
            result['coords'] = self.coords.to_dict()
        
        if self.initial_coords:
            result['initial_coords'] = self.initial_coords.to_dict()
        
        if self.final_coords:
            result['final_coords'] = self.final_coords.to_dict()
        
        # Añadir campos numéricos si existen
        for field in ['accuracy', 'altitude', 'speed', 'distance', 'duration']:
            value = getattr(self, field)
            if value is not None:
                result[field] = value
        
        # Añadir metadatos
        result.update(self.metadata)
        
        return result
    
    def get_coordinates(self) -> List[Coordinates]:
        """Obtener todas las coordenadas del viaje"""
        coordinates = []
        
        # Añadir coordenadas principales si existen
        if self.coords:
            coordinates.append(self.coords)
        
        # Añadir coordenadas iniciales si existen y no están duplicadas
        if self.initial_coords and (not coordinates or 
                                    self.initial_coords.lat != coordinates[0].lat or 
                                    self.initial_coords.lon != coordinates[0].lon):
            coordinates.append(self.initial_coords)
        
        # Añadir coordenadas finales si existen y no están duplicadas
        if self.final_coords and (not coordinates or 
                                 (self.final_coords.lat != coordinates[-1].lat or 
                                  self.final_coords.lon != coordinates[-1].lon)):
            coordinates.append(self.final_coords)
        
        return coordinates
    
    def calculate_distance(self) -> float:
        """Calcular distancia del viaje en km"""
        from math import radians, sin, cos, sqrt, atan2
        
        coords = self.get_coordinates()
        
        if len(coords) < 2:
            return 0.0
        
        # Radio de la Tierra en km
        R = 6371.0
        
        total_distance = 0.0
        
        for i in range(len(coords) - 1):
            # Coordenadas en radianes
            lat1 = radians(coords[i].lat)
            lon1 = radians(coords[i].lon)
            lat2 = radians(coords[i + 1].lat)
            lon2 = radians(coords[i + 1].lon)
            
            # Diferencias
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            
            # Fórmula de Haversine
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c
            
            total_distance += distance
        
        return total_distance