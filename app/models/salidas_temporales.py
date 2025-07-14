"""
Módulo para gestión de vehículos en estacionamientos en fila.
Implementa pila LIFO para mover vehículos temporalmente.
"""
from datetime import datetime
from .base import ModeloBase, GestorBase
from app.db_config import get_conexion

class SalidaTemporal(ModeloBase): # Hereda de Clase padre ModeloBase
    """
    Maneja los movimientos temporales de vehículos en fila.
    """
    def __init__(self, id_vehiculo: int, id_espacio_fila: int, posicion_origen: int):
        super().__init__()
        self._id_vehiculo = id_vehiculo
        self._id_espacio_fila = id_espacio_fila
        self._posicion_origen = posicion_origen
        self._fecha_movimiento = datetime.now()
        self._fecha_retorno = None
        self._placa = None

    @property
    def id_vehiculo(self) -> int:
        return self._id_vehiculo

    @property
    def id_espacio_fila(self) -> int:
        return self._id_espacio_fila

    @property
    def posicion_origen(self) -> int:
        return self._posicion_origen

    @property
    def placa(self) -> str:
        return self._placa

class GestorSalidasTemporales(GestorBase):
    def crear(self, movimiento: SalidaTemporal) -> bool:
        try:
            conn = get_conexion()
            if not conn:
                return False

            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO MovimientosTemporales 
                   (id_vehiculo, id_espacio_fila, posicion_origen)
                   VALUES (?, ?, ?)""",
                (movimiento.id_vehiculo, 
                 movimiento.id_espacio_fila,
                 movimiento.posicion_origen)
            )
            conn.commit()
            return True
        except Exception as error:
            print(f"Error al registrar movimiento temporal: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def obtener(self, id_movimiento: int) -> SalidaTemporal:
        """Implementación requerida de GestorBase"""
        try:
            conn = get_conexion()
            if not conn:
                return None
                
            cursor = conn.cursor()
            cursor.execute(
                """SELECT mt.id_movimiento, mt.id_vehiculo, mt.id_espacio_fila,
                          mt.posicion_origen, mt.fecha_movimiento, mt.fecha_retorno,
                          v.placa 
                   FROM MovimientosTemporales mt
                   JOIN Vehiculos v ON mt.id_vehiculo = v.id_vehiculo
                   WHERE mt.id_movimiento = ?""",
                (id_movimiento,)
            )
            row = cursor.fetchone()
            
            if row:
                movimiento = SalidaTemporal(row[1], row[2], row[3])
                movimiento._id = row[0]
                movimiento._fecha_movimiento = row[4]
                movimiento._fecha_retorno = row[5]
                movimiento._placa = row[6]
                return movimiento
            return None
                
        except Exception as error:
            print(f"Error al obtener movimiento temporal: {str(error)}")
            return None
        finally:
            if conn:
                conn.close()

    def actualizar(self, movimiento: SalidaTemporal) -> bool:
        """Implementación requerida de GestorBase"""
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE MovimientosTemporales 
                   SET id_vehiculo = ?, id_espacio_fila = ?,
                       posicion_origen = ?, fecha_retorno = ?
                   WHERE id_movimiento = ?""",
                (movimiento.id_vehiculo, movimiento.id_espacio_fila,
                 movimiento.posicion_origen, movimiento.fecha_retorno,
                 movimiento.id)
            )
            conn.commit()
            return cursor.rowcount > 0
                
        except Exception as error:
            print(f"Error al actualizar movimiento temporal: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar(self, id_movimiento: int) -> bool:
        """Implementación requerida de GestorBase"""
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM MovimientosTemporales WHERE id_movimiento = ?",
                (id_movimiento,)
            )
            conn.commit()
            return cursor.rowcount > 0
                
        except Exception as error:
            print(f"Error al eliminar movimiento temporal: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def obtener_vehiculos_a_mover(self, id_espacio_fila: int, posicion_objetivo: int) -> list:
        """
        Obtiene los vehículos que deben moverse para llegar al vehículo objetivo.
        """
        try:
            conn = get_conexion()
            if not conn:
                return []

            cursor = conn.cursor()
            cursor.execute(
                """SELECT v.id_vehiculo, v.placa, pv.posicion
                   FROM PilaVehiculos pv
                   JOIN Vehiculos v ON pv.id_vehiculo = v.id_vehiculo
                   WHERE pv.id_espacio_fila = ? 
                   AND pv.posicion < ?
                   ORDER BY pv.posicion DESC""",
                (id_espacio_fila, posicion_objetivo)
            )
            
            return cursor.fetchall()
        except Exception as error:
            print(f"Error al obtener vehículos a mover: {str(error)}")
            return []
        finally:
            if conn:
                conn.close()

    def registrar_retorno(self, id_movimiento: int) -> bool:
        try:
            conn = get_conexion()
            if not conn:
                return False

            cursor = conn.cursor()
            cursor.execute(
                """UPDATE MovimientosTemporales 
                   SET fecha_retorno = GETDATE()
                   WHERE id_movimiento = ?""",
                (id_movimiento,)
            )
            conn.commit()
            return True
        except Exception as error:
            print(f"Error al registrar retorno: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def obtener_movimientos_pendientes(self, id_espacio_fila: int) -> list:
        """
        Obtiene los vehículos que están temporalmente fuera de su posición.
        """
        try:
            conn = get_conexion()
            if not conn:
                return []

            cursor = conn.cursor()
            cursor.execute(
                """SELECT mt.id_movimiento, mt.id_vehiculo, v.placa, 
                          mt.posicion_origen, mt.fecha_movimiento
                   FROM MovimientosTemporales mt
                   JOIN Vehiculos v ON mt.id_vehiculo = v.id_vehiculo
                   WHERE mt.id_espacio_fila = ?
                   AND mt.fecha_retorno IS NULL
                   ORDER BY mt.fecha_movimiento DESC""",
                (id_espacio_fila,)
            )
            return cursor.fetchall()
        except Exception as error:
            print(f"Error al obtener movimientos pendientes: {str(error)}")
            return []
        finally:
            if conn:
                conn.close()
