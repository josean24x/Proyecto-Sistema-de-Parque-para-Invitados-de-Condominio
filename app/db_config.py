"""
Configuración de conexión a la base de datos.
Utiliza variables de entorno para mayor seguridad.
"""
import pyodbc

def get_conexion():
    try:
        return pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=SJO-5CG427530D\\SQLEXPRESS;'
            'DATABASE=ParkingSystem;'
            'Trusted_Connection=yes;'
        )
    except pyodbc.Error as e:
        print(f"Error de conexión ODBC: {str(e)}")
        return None
