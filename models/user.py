from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
from datetime import datetime
import pytz

@dataclass
class User:
    """Modelo para usuarios"""
    id: str
    email: str
    name: str
    role: str = "user"
    createdAt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Crear objeto User desde un diccionario"""
        # Crear objeto User base
        user = cls(
            id=data.get('id', ''),
            email=data.get('email', ''),
            name=data.get('name', ''),
            role=data.get('role', 'user'),
            createdAt=data.get('createdAt')
        )
        
        # Almacenar cualquier campo adicional en metadata
        excluded_fields = {'id', 'email', 'name', 'role', 'createdAt'}
        
        user.metadata = {
            k: v for k, v in data.items() if k not in excluded_fields
        }
        
        return user
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        result = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role
        }
        
        # Añadir fecha de creación si existe
        if self.createdAt:
            result['createdAt'] = self.createdAt
        else:
            # Generar fecha actual en formato adecuado
            tz = pytz.timezone('America/Denver')  # UTC-7
            result['createdAt'] = datetime.now(tz).strftime("%d de %B de %Y, %I:%M:%S%p UTC-7")
        
        # Añadir metadatos
        result.update(self.metadata)
        
        return result
    
    def is_admin(self) -> bool:
        """Verificar si el usuario es administrador"""
        return self.role == "admin"
    
    def is_monitor(self) -> bool:
        """Verificar si el usuario es monitor"""
        return self.role == "monitor"
    
    def can_view_user(self, user_id: str) -> bool:
        """Verificar si el usuario puede ver los datos de otro usuario"""
        # Los administradores pueden ver a cualquier usuario
        if self.is_admin():
            return True
        
        # Los monitores pueden ver a usuarios asignados (implementación básica)
        if self.is_monitor():
            # En una implementación real, verificaríamos en la base de datos
            # si este monitor tiene asignado al usuario con user_id
            # Para este ejemplo, asumimos que sí puede
            return True
        
        # Los usuarios normales solo pueden verse a sí mismos
        return self.id == user_id
    
    def can_edit_user(self, user_id: str) -> bool:
        """Verificar si el usuario puede editar a otro usuario"""
        # Solo los administradores pueden editar a otros usuarios
        if self.is_admin():
            return True
        
        # Cualquier usuario puede editarse a sí mismo
        return self.id == user_id
    
    def can_assign_monitors(self) -> bool:
        """Verificar si el usuario puede asignar monitores"""
        # Solo los administradores pueden asignar monitores
        return self.is_admin()
    
    def can_view_all_travels(self) -> bool:
        """Verificar si el usuario puede ver todos los viajes"""
        # Solo los administradores pueden ver todos los viajes
        return self.is_admin()

@dataclass
class UserAssignment:
    """Modelo para asignaciones de usuario a monitor"""
    user_id: str
    monitor_id: str
    assigned_at: str
    assigned_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserAssignment':
        """Crear objeto UserAssignment desde un diccionario"""
        # Crear objeto UserAssignment base
        assignment = cls(
            user_id=data.get('user_id', ''),
            monitor_id=data.get('monitor_id', ''),
            assigned_at=data.get('assigned_at', ''),
            assigned_by=data.get('assigned_by')
        )
        
        # Almacenar cualquier campo adicional en metadata
        excluded_fields = {'user_id', 'monitor_id', 'assigned_at', 'assigned_by'}
        
        assignment.metadata = {
            k: v for k, v in data.items() if k not in excluded_fields
        }
        
        return assignment
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        result = {
            'user_id': self.user_id,
            'monitor_id': self.monitor_id,
            'assigned_at': self.assigned_at
        }
        
        # Añadir asignador si existe
        if self.assigned_by:
            result['assigned_by'] = self.assigned_by
        
        # Añadir metadatos
        result.update(self.metadata)
        
        return result