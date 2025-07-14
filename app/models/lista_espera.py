"""
Módulo para gestión de lista de espera cuando el parqueo está lleno.
Implementa una cola FIFO (First In, First Out).
"""
from datetime import datetime
from .base import ModeloBase, GestorBase
from app.db_config import get_conexion

class ListaEspera(ModeloBase): # Hereda de Clase padre ModeloBase
    """
    Elemento de la lista de espera para espacios de parqueo.
    
    Atributos:
        _id_vehiculo (int): ID del vehículo en espera
        _fecha_solicitud (datetime): Fecha/hora de la solicitud
        _estado (str): Estado (pendiente/atendido/cancelado)
    """
    
    ESTADOS_VALIDOS = ['pendiente', 'cancelado']
    
    def __init__(self, id_vehiculo: int):
        """
        Inicializa una nueva solicitud en lista de espera.
        
        Args:
            id_vehiculo: ID del vehículo que espera
        """
        super().__init__()
        self._id_vehiculo = int(id_vehiculo)
        self._fecha_solicitud = datetime.now()
        self._estado = 'pendiente'
        self._placa = None  # Para almacenar info adicional

    @property
    def id_vehiculo(self) -> int:
        """Devuelve el ID del vehículo en espera."""
        return self._id_vehiculo

    @property
    def fecha_solicitud(self) -> datetime:
        """Devuelve la fecha/hora de la solicitud."""
        return self._fecha_solicitud

    @property
    def estado(self) -> str:
        """Devuelve el estado actual."""
        return self._estado

    @property
    def placa(self) -> str:
        """Devuelve la placa del vehículo (si está disponible)."""
        return self._placa

    @estado.setter
    def estado(self, nuevo_estado: str):
        """
        Establece el estado de la solicitud.
        
        Args:
            nuevo_estado: Nuevo estado a asignar
            
        Raises:
            ValueError: Si el estado no es válido
        """
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado debe ser uno de: {self.ESTADOS_VALIDOS}")
        self._estado = nuevo_estado

    @classmethod
    def from_db_row(cls, row):
        """
        Crea una instancia a partir de una fila de la base de datos.
        
        Args:
            row: Tupla con datos de la base de datos
            
        Returns:
            ListaEspera: Instancia creada
        """
        item = cls(row[1])
        item._id = row[0]
        item._fecha_solicitud = row[2]
        item._estado = row[3]
        return item

class GestorListaEspera(GestorBase):
    """
    Gestor para operaciones con la lista de espera.
    Implementa una cola FIFO (First In, First Out).
    """
    
    def crear(self, lista_espera: ListaEspera) -> bool:
        """
        Agrega un nuevo vehículo a la lista de espera.
        
        Args:
            lista_espera: Instancia de ListaEspera a crear
            
        Returns:
            bool: True si se creó correctamente, False si falló
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO ListaEspera 
                (id_vehiculo, fecha_solicitud, estado)
                VALUES (?, ?, ?)""",
                (lista_espera.id_vehiculo, 
                 lista_espera.fecha_solicitud,
                 lista_espera.estado)
            )
            conn.commit()
            return True
            
        except Exception as error:
            print(f"Error al agregar a lista de espera: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def obtener(self, id_espera: int) -> ListaEspera:
        """
        Obtiene un elemento de la lista de espera por su ID.
        
        Args:
            id_espera: ID del elemento a buscar
            
        Returns:
            ListaEspera: Instancia encontrada o None
        """
        try:
            conn = get_conexion()
            if not conn:
                return None
                
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id_espera, id_vehiculo, fecha_solicitud, estado
                FROM ListaEspera WHERE id_espera = ?""",
                (id_espera,)
            )
            row = cursor.fetchone()
            
            if row:
                return ListaEspera.from_db_row(row)
            return None
            
        except Exception as error:
            print(f"Error al obtener elemento de lista de espera: {str(error)}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todos(self) -> list[ListaEspera]:
        """
        Obtiene todos los elementos de la lista de espera con información del vehículo.
        
        Returns:
            list[ListaEspera]: Lista completa de espera
        """
        try:
            conn = get_conexion()
            if not conn:
                return []
                
            cursor = conn.cursor()
            cursor.execute(
                """SELECT le.id_espera, le.id_vehiculo, le.fecha_solicitud, le.estado,
                   v.placa
                FROM ListaEspera le
                JOIN Vehiculos v ON le.id_vehiculo = v.id_vehiculo
                ORDER BY le.fecha_solicitud"""
            )
            
            items = []
            for row in cursor.fetchall():
                item = ListaEspera.from_db_row(row)
                item._placa = row[4]  # Agregar placa del vehículo
                items.append(item)
                
            return items
            
        except Exception as error:
            print(f"Error al obtener lista de espera: {str(error)}")
            return []
        finally:
            if conn:
                conn.close()

    def obtener_pendientes(self) -> list:
        try:
            conn = get_conexion()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT le.id_espera, le.id_vehiculo, le.fecha_solicitud, le.estado,
                       v.placa, v.marca, u.nombre as propietario
                FROM ListaEspera le
                JOIN Vehiculos v ON le.id_vehiculo = v.id_vehiculo
                JOIN Usuarios u ON v.id_usuario = u.id_usuario
                WHERE le.estado = 'pendiente'
                ORDER BY le.fecha_solicitud
            """)
            
            items = []
            for row in cursor.fetchall():
                item = {
                    'id': row[0],
                    'placa': row[4],
                    'marca': row[5],
                    'propietario': row[6],
                    'fecha_ingreso': row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else ''
                }
                items.append(item)
                    
            conn.close()
            return items
                
        except Exception as error:
            print(f"Error al obtener lista de espera pendiente: {str(error)}")
            return []

    def eliminar(self, id_espera: int) -> bool:
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE ListaEspera 
                SET estado = 'cancelado'
                WHERE id_espera = ?""",
                (id_espera,)
            )
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as error:
            print(f"Error al cancelar elemento de lista de espera: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def actualizar(self, lista_espera: ListaEspera) -> bool:
        """
        Actualiza el estado de un elemento en la lista de espera.
        
        Args:
            lista_espera: Instancia con datos actualizados
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE ListaEspera 
                SET estado = ?
                WHERE id_espera = ?""",
                (lista_espera.estado, lista_espera.id)
            )
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as error:
            print(f"Error al actualizar lista de espera: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar(self, id_espera: int) -> bool:
        """
        Elimina (cancela) un elemento de la lista de espera.
        
        Args:
            id_espera: ID del elemento a cancelar
            
        Returns:
            bool: True si se canceló correctamente
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE ListaEspera 
                SET estado = 'cancelado'
                WHERE id_espera = ?""",
                (id_espera,)
            )
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as error:
            print(f"Error al cancelar elemento de lista de espera: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def procesar_siguiente(self) -> bool:
        """
        Procesa el siguiente vehículo en la lista de espera (FIFO).
        
        Returns:
            bool: True si se procesó exitosamente
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            # Obtener el más antiguo pendiente
            cursor.execute(
                """SELECT TOP 1 id_espera, id_vehiculo 
                FROM ListaEspera
                WHERE estado = 'pendiente'
                ORDER BY fecha_solicitud"""
            )
            resultado = cursor.fetchone()
            
            if not resultado:
                return False  # No hay pendientes
                
            # Marcar como atendido
            cursor.execute(
                """UPDATE ListaEspera
                SET estado = 'atendido'
                WHERE id_espera = ?""",
                (resultado[0],)
            )
            conn.commit()
            return True
            
        except Exception as error:
            print(f"Error al procesar lista de espera: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def contar_pendientes(self) -> int:
        """
        Cuenta los vehículos pendientes en la lista de espera.
        
        Returns:
            int: Número de vehículos pendientes
        """
        try:
            conn = get_conexion()
            if not conn:
                return 0
                
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM ListaEspera WHERE estado = 'pendiente'"
            )
            return cursor.fetchone()[0]
            
        except Exception as error:
            print(f"Error al contar pendientes: {str(error)}")
            return 0
        finally:
            if conn:
                conn.close()
