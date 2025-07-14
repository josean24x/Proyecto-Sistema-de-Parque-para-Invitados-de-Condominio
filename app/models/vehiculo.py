"""
Módulo para la gestión de vehículos.
Contiene la clase Vehículo y su gestor para operaciones con la base de datos.
"""
from datetime import datetime
from .base import ModeloBase, GestorBase
from app.db_config import get_conexion

class Vehiculo(ModeloBase): # Hereda de Clase padre ModeloBase
    """
    Clase que representa un vehículo en el sistema.
    
    Atributos:
        _placa (str): Número de placa del vehículo
        _marca (str): Marca del vehículo
        _modelo (str): Modelo del vehículo
        _id_usuario (int): ID del propietario
        _hora_entrada (datetime): Hora de entrada al parqueo
        _hora_salida (datetime): Hora de salida del parqueo
    """
    
    def __init__(self, placa: str, marca: str, modelo: str, id_usuario: int):
        """
        Inicializa una nueva instancia de Vehículo.
        
        Args:
            placa: Número de placa
            marca: Marca del vehículo
            modelo: Modelo del vehículo
            id_usuario: ID del usuario propietario
        """
        super().__init__()
        self._placa = placa
        self._marca = marca
        self._modelo = modelo
        self._id_usuario = id_usuario
        self._hora_entrada = None
        self._hora_salida = None

    @property
    def placa(self) -> str:
        """Devuelve el número de placa."""
        return self._placa

    @property
    def marca(self) -> str:
        """Devuelve la marca del vehículo."""
        return self._marca

    @property
    def modelo(self) -> str:
        """Devuelve el modelo del vehículo."""
        return self._modelo

    @property
    def id_usuario(self) -> int:
        """Devuelve el ID del propietario."""
        return self._id_usuario

    @property
    def hora_entrada(self) -> datetime:
        """Devuelve la hora de entrada al parqueo."""
        return self._hora_entrada

    @property
    def hora_salida(self) -> datetime:
        """Devuelve la hora de salida del parqueo."""
        return self._hora_salida

    def registrar_entrada(self):
        """Registra la hora actual como entrada al parqueo."""
        self._hora_entrada = datetime.now()
        self._hora_salida = None

    def registrar_salida(self):
        """Registra la hora actual como salida del parqueo."""
        self._hora_salida = datetime.now()

class GestorVehiculos(GestorBase):
    """
    Gestor para operaciones de vehículos en la base de datos.
    Implementa los métodos CRUD requeridos por GestorBase.
    """
    
    def crear(self, vehiculo: Vehiculo) -> bool:
        """
        Crea un nuevo vehículo en la base de datos.
        
        Args:
            vehiculo: Instancia de Vehículo a crear
            
        Returns:
            bool: True si se creó correctamente, False si falló
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO Vehiculos (placa, marca, modelo, id_usuario) VALUES (?, ?, ?, ?)""",
                (vehiculo.placa, vehiculo.marca, vehiculo.modelo, vehiculo.id_usuario)
            )
            conn.commit()
            return True
            
        except Exception as error:
            print(f"Error al crear vehículo: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def obtener(self, id_vehiculo: int) -> Vehiculo:
        """
        Obtiene un vehículo por su ID.
        
        Args:
            id_vehiculo: ID del vehículo a buscar
            
        Returns:
            Vehiculo: Instancia del vehículo encontrado o None
        """
        try:
            conn = get_conexion()
            if not conn:
                return None
                
            cursor = conn.cursor()
            cursor.execute(
                """SELECT v.id_vehiculo, v.placa, v.marca, v.modelo, 
               v.id_usuario, v.hora_entrada, v.hora_salida, u.nombre 
               FROM Vehiculos v 
               JOIN Usuarios u ON v.id_usuario = u.id_usuario 
               WHERE v.id_vehiculo =  ?""",
                (id_vehiculo,)
            )
            row = cursor.fetchone()
            
            if row:
                vehiculo = Vehiculo(row[1], row[2], row[3], row[4])
                vehiculo._id = row[0]
                vehiculo._hora_entrada = row[5]
                vehiculo._hora_salida = row[6]
                return vehiculo
            return None
            
        except Exception as error:
            print(f"Error al obtener vehículo: {str(error)}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todos(self) -> list[Vehiculo]:
        """
        Obtiene todos los vehículos registrados en el sistema.
        
        Returns:
            list[Vehiculo]: Lista de vehículos
        """
        try:
            conn = get_conexion()
            if not conn:
                return []
                
            cursor = conn.cursor()
            cursor.execute(
                """SELECT v.id_vehiculo, v.placa, v.marca, v.modelo, 
               v.id_usuario, v.hora_entrada, v.hora_salida, u.nombre 
               FROM Vehiculos v 
               JOIN Usuarios u ON v.id_usuario = u.id_usuario"""
            )
            
            vehiculos = []
            for row in cursor.fetchall():
                vehiculo = Vehiculo(row[1], row[2], row[3], row[4])
                vehiculo._id = row[0]
                vehiculo._hora_entrada = row[5]
                vehiculo._hora_salida = row[6]
                vehiculo.propietario = row[7]  # Nombre del propietario
                vehiculos.append(vehiculo)
                
            return vehiculos
            
        except Exception as error:
            print(f"Error al obtener vehículos: {str(error)}")
            return []
        finally:
            if conn:
                conn.close()

    def actualizar(self, vehiculo: Vehiculo) -> bool:
        """
        Actualiza los datos de un vehículo existente.
        
        Args:
            vehiculo: Instancia de Vehículo con los datos actualizados
            
        Returns:
            bool: True si se actualizó correctamente, False si falló
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE Vehiculos 
                SET placa = ?, marca = ?, modelo = ?, id_usuario = ?,
                    hora_entrada = ?, hora_salida = ?
                WHERE id_vehiculo = ?""",
                (vehiculo.placa, vehiculo.marca, vehiculo.modelo,
                 vehiculo.id_usuario, vehiculo.hora_entrada,
                 vehiculo.hora_salida, vehiculo.id)
            )
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as error:
            print(f"Error al actualizar vehículo: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar(self, id_vehiculo: int) -> bool:
        """
        Elimina un vehículo del sistema.
        
        Args:
            id_vehiculo: ID del vehículo a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si falló
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM Vehiculos WHERE id_vehiculo = ?",
                (id_vehiculo,)
            )
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as error:
            print(f"Error al eliminar vehículo: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def contar(self) -> int:
        """
        Cuenta el total de vehículos registrados en el sistema.
        
        Returns:
            int: Número total de vehículos
        """
        try:
            conn = get_conexion()
            if not conn:
                return 0
                
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Vehiculos")
            return cursor.fetchone()[0]
            
        except Exception as error:
            print(f"Error al contar vehículos: {str(error)}")
            return 0
        finally:
            if conn:
                conn.close()

    def existe_placa(self, placa: str) -> bool:
        """
        Verifica si ya existe un vehículo con la placa especificada.
        
        Args:
            placa: Número de placa a verificar
            
        Returns:
            bool: True si existe, False si no
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM Vehiculos WHERE placa = ?",
                (placa,)
            )
            return cursor.fetchone()[0] > 0
            
        except Exception as error:
            print(f"Error al verificar placa: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def obtener_por_usuario(self, id_usuario: int) -> list[Vehiculo]:
        """
        Obtiene todos los vehículos de un usuario específico.
        
        Args:
            id_usuario: ID del propietario
            
        Returns:
            list[Vehiculo]: Lista de vehículos del usuario
        """
        try:
            conn = get_conexion()
            if not conn:
                return []
                
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id_vehiculo, placa, marca, modelo, id_usuario, 
                   hora_entrada, hora_salida 
                   FROM Vehiculos WHERE id_usuario = ?""",
                (id_usuario,)
            )
            
            vehiculos = []
            for row in cursor.fetchall():
                vehiculo = Vehiculo(row[1], row[2], row[3], row[4])
                vehiculo._id = row[0]
                vehiculo._hora_entrada = row[5]
                vehiculo._hora_salida = row[6]
                vehiculos.append(vehiculo)
                
            return vehiculos
            
        except Exception as error:
            print(f"Error al obtener vehículos por usuario: {str(error)}")
            return []
        finally:
            if conn:
                conn.close()
