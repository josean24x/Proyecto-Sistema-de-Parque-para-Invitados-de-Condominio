"""
Módulo base para modelos y gestores.
Define las clases base abstractas que deben implementar los modelos concretos.
"""
from abc import ABC, abstractmethod

class ModeloBase:
    """
    Clase base abstracta para todos los modelos del sistema.
    
    Atributos:
        _id (int): Identificador único del modelo
    """
    
    def __init__(self):
        """Inicializa el modelo con ID None."""
        self._id = None

    @property
    def id(self) -> int:
        """Devuelve el ID del modelo."""
        return self._id

class GestorBase(ABC):
    """
    Clase base abstracta para todos los gestores del sistema.
    Define la interfaz CRUD que deben implementar los gestores concretos.
    """
    
    @abstractmethod
    def crear(self, modelo) -> bool:
        """Crea un nuevo registro en la base de datos."""
        pass
    
    @abstractmethod
    def obtener(self, id_modelo) -> ModeloBase:
        """Obtiene un registro por su ID."""
        pass
    
    @abstractmethod
    def actualizar(self, modelo) -> bool:
        """Actualiza un registro existente."""
        pass
    
    @abstractmethod
    def eliminar(self, id_modelo) -> bool:
        """Elimina un registro por su ID."""
        pass