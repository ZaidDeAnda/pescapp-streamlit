from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
from datetime import datetime
import pytz

@dataclass
class UserProfile:
    """Modelo para perfiles de usuario"""
    id_user: str
    embarcacion: str
    potencia_motor: float
    especies_captura: str
    nombre_contacto: str
    telefono_contacto: str
    tipo_organizacion: str
    
    # Campos opcionales
    unidad_potencia: str = "HP"
    relacion_contacto: Optional[str] = None
    nombre_organizacion: Optional[str] = None
    experiencia_anos: int = 0
    observaciones: Optional[str] = None
    consentimiento: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        """Crear objeto UserProfile desde un diccionario"""
        # Crear objeto base con campos requeridos
        profile = cls(
            id_user=data.get('id_user', ''),
            embarcacion=data.get('embarcacion', ''),
            potencia_motor=float(data.get('potencia_motor', 0)),
            especies_captura=data.get('especies_captura', ''),
            nombre_contacto=data.get('nombre_contacto', ''),
            telefono_contacto=data.get('telefono_contacto', ''),
            tipo_organizacion=data.get('tipo_organizacion', 'Cooperativa')
        )
        
        # Añadir campos opcionales
        profile.unidad_potencia = data.get('unidad_potencia', 'HP')
        profile.relacion_contacto = data.get('relacion_contacto')
        profile.nombre_organizacion = data.get('nombre_organizacion')
        profile.experiencia_anos = int(data.get('experiencia_anos', 0))
        profile.observaciones = data.get('observaciones')
        profile.consentimiento = data.get('consentimiento', False)
        profile.created_at = data.get('created_at')
        profile.updated_at = data.get('updated_at')
        
        # Almacenar campos adicionales en metadata
        excluded_fields = {
            'id_user', 'embarcacion', 'potencia_motor', 'especies_captura', 
            'nombre_contacto', 'telefono_contacto', 'tipo_organizacion',
            'unidad_potencia', 'relacion_contacto', 'nombre_organizacion',
            'experiencia_anos', 'observaciones', 'consentimiento',
            'created_at', 'updated_at'
        }
        
        profile.metadata = {
            k: v for k, v in data.items() if k not in excluded_fields
        }
        
        return profile
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        result = {
            'id_user': self.id_user,
            'embarcacion': self.embarcacion,
            'potencia_motor': self.potencia_motor,
            'especies_captura': self.especies_captura,
            'nombre_contacto': self.nombre_contacto,
            'telefono_contacto': self.telefono_contacto,
            'tipo_organizacion': self.tipo_organizacion,
            'unidad_potencia': self.unidad_potencia,
            'consentimiento': self.consentimiento
        }
        
        # Añadir campos opcionales si tienen valor
        if self.relacion_contacto:
            result['relacion_contacto'] = self.relacion_contacto
        
        if self.nombre_organizacion:
            result['nombre_organizacion'] = self.nombre_organizacion
        
        if self.experiencia_anos > 0:
            result['experiencia_anos'] = self.experiencia_anos
        
        if self.observaciones:
            result['observaciones'] = self.observaciones
        
        # Añadir fechas
        if self.created_at:
            result['created_at'] = self.created_at
        else:
            # Generar fecha actual en formato adecuado
            tz = pytz.timezone('America/Denver')  # UTC-7
            result['created_at'] = datetime.now(tz).isoformat()
        
        if self.updated_at:
            result['updated_at'] = self.updated_at
        else:
            # Usar la misma fecha de creación
            result['updated_at'] = result['created_at']
        
        # Añadir metadatos
        result.update(self.metadata)
        
        return result
    
    def is_complete(self) -> bool:
        """Verificar si el perfil tiene toda la información requerida"""
        return (
            bool(self.embarcacion) and
            self.potencia_motor > 0 and
            bool(self.especies_captura) and
            bool(self.nombre_contacto) and
            bool(self.telefono_contacto) and
            bool(self.tipo_organizacion) and
            self.consentimiento
        )