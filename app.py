"""
Aplicación principal Flask para el sistema de reservas de parqueo.
Maneja todas las rutas y la comunicación entre frontend y backend.
"""
from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from app.db_config import get_conexion
from app.models.usuario import Usuario, GestorUsuarios  
from app.models.vehiculo import Vehiculo, GestorVehiculos
from app.models.lista_espera import ListaEspera, GestorListaEspera
from app.models.salidas_temporales import SalidaTemporal, GestorSalidasTemporales
from datetime import datetime, timedelta

app = Flask(
    __name__,
    template_folder='app/templates',
    static_folder='app/static'
)
app.config['DEBUG'] = True

gestor_usuarios = GestorUsuarios()
gestor_vehiculos = GestorVehiculos()
gestor_lista_espera = GestorListaEspera()
gestor_salidas = GestorSalidasTemporales()

@app.route('/')
def mostrar_dashboard():
    try:
        datos = {
            'usuarios': gestor_usuarios.obtener_todos(),
            'vehiculos': gestor_vehiculos.obtener_todos(),
            'lista_espera': gestor_lista_espera.obtener_pendientes(),
            'espacios_fila': obtener_datos_espacios_fila()
        }
        return render_template('index.html', **datos)
    except Exception as error:
        app.logger.error(f"Error en página principal: {str(error)}")
        datos = {
            'usuarios': [],
            'vehiculos': [],
            'lista_espera': [],
            'espacios_fila': []
        }
        return render_template('index.html', **datos)

@app.route('/usuarios')
def listar_usuarios():
    try:
        usuarios = gestor_usuarios.obtener_todos()
        return render_template('usuarios.html', usuarios=usuarios)
    except Exception as error:
        app.logger.error(f"Error al listar usuarios: {str(error)}")
        return render_template('error.html', mensaje="Error al obtener usuarios")

@app.route('/usuarios/crear', methods=['POST'])
def crear_usuario():
    try:
        campos_requeridos = ['cedula', 'nombre', 'telefono']
        if not all(campo in request.form for campo in campos_requeridos):
            return redirect(url_for('mostrar_dashboard'))
        
        nuevo_usuario = Usuario(
            cedula=request.form['cedula'],
            nombre=request.form['nombre'],
            telefono=request.form['telefono'],
            email=request.form.get('email', '')
        )
        
        if gestor_usuarios.crear(nuevo_usuario):
            return redirect(url_for('mostrar_dashboard'))
        
        return redirect(url_for('mostrar_dashboard'))
    
    except Exception as error:
        print(f"Error al crear usuario: {str(error)}")
        return redirect(url_for('mostrar_dashboard'))

@app.route('/usuarios/eliminar/<int:id_usuario>')
def eliminar_usuario(id_usuario):
    try:
        if gestor_usuarios.eliminar(id_usuario):
            return redirect(url_for('mostrar_dashboard'))
        
        raise Exception("No se pudo eliminar el usuario")
    
    except Exception as error:
        app.logger.error(f"Error al eliminar usuario: {str(error)}")
        return render_template('error.html', mensaje="Error al eliminar usuario")

@app.route('/vehiculos')
def listar_vehiculos():
    try:
        vehiculos = gestor_vehiculos.obtener_todos()
        return render_template('vehiculos.html', vehiculos=vehiculos)
    except Exception as error:
        app.logger.error(f"Error al listar vehículos: {str(error)}")
        return render_template('error.html', mensaje="Error al obtener vehículos")

@app.route('/vehiculos/crear', methods=['POST'])
def crear_vehiculo():
    try:
        campos_requeridos = ['placa', 'marca', 'modelo', 'id_usuario']
        if not all(campo in request.form for campo in campos_requeridos):
            raise ValueError("Faltan campos requeridos")
        
        nuevo_vehiculo = Vehiculo(
            placa=request.form['placa'],
            marca=request.form['marca'],
            modelo=request.form['modelo'],
            id_usuario=request.form['id_usuario']
        )
        
        if gestor_vehiculos.crear(nuevo_vehiculo):
            return redirect(url_for('mostrar_dashboard'))
        
        raise Exception("No se pudo crear el vehículo en la base de datos")
    
    except ValueError as error:
        return render_template('error.html', mensaje=str(error))
    except Exception as error:
        app.logger.error(f"Error al crear vehículo: {str(error)}")
        return render_template('error.html', mensaje="Error interno del sistema")

@app.route('/vehiculos/eliminar/<int:id_vehiculo>')
def eliminar_vehiculo(id_vehiculo):
    try:
        if gestor_vehiculos.eliminar(id_vehiculo):
            return redirect(url_for('mostrar_dashboard'))
        
        raise Exception("No se pudo eliminar el vehículo")
    
    except Exception as error:
        app.logger.error(f"Error al eliminar vehículo: {str(error)}")
        return render_template('error.html', mensaje="Error al eliminar vehículo")

@app.route('/lista_espera')
def listar_espera():
    try:
        lista_espera = gestor_lista_espera.obtener_todos()
        return render_template('lista_espera.html', lista_espera=lista_espera)
    except Exception as error:
        app.logger.error(f"Error al listar espera: {str(error)}")
        return render_template('error.html', mensaje="Error al obtener lista de espera")

@app.route('/lista_espera/agregar', methods=['POST'])
def agregar_lista_espera():
    try:
        if 'id_vehiculo' not in request.form:
            raise ValueError("Falta el ID del vehículo")
        
        nueva_espera = ListaEspera(
            id_vehiculo=request.form['id_vehiculo']
        )
        
        if gestor_lista_espera.crear(nueva_espera):
            return redirect(url_for('mostrar_dashboard'))
        
        raise Exception("No se pudo agregar a la lista de espera")
    
    except ValueError as error:
        return render_template('error.html', mensaje=str(error))
    except Exception as error:
        app.logger.error(f"Error al agregar a lista de espera: {str(error)}")
        return render_template('error.html', mensaje="Error interno del sistema")

@app.route('/lista_espera/procesar')
def procesar_lista_espera():
    try:
        lista_espera = gestor_lista_espera.obtener_pendientes()
        if not lista_espera:
            return redirect(url_for('mostrar_dashboard'))
            
        espera = lista_espera[0]
        conn = get_conexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ef.id_espacio_fila
            FROM EspaciosFila ef
            LEFT JOIN (
                SELECT id_espacio_fila, COUNT(*) as total
                FROM PilaVehiculos
                GROUP BY id_espacio_fila
            ) pv ON ef.id_espacio_fila = pv.id_espacio_fila
            WHERE pv.total IS NULL OR pv.total < 3
            ORDER BY ef.numero_espacio
        """)
        
        espacio_disponible = cursor.fetchone()
        
        if espacio_disponible:
            cursor.execute("""
                SELECT COUNT(*) FROM PilaVehiculos 
                WHERE id_espacio_fila = ?
            """, (espacio_disponible[0],))
            
            posicion = cursor.fetchone()[0] + 1
            
            cursor.execute("""
                INSERT INTO PilaVehiculos 
                (id_espacio_fila, id_vehiculo, posicion, fecha_entrada)
                VALUES (?, ?, ?, GETDATE())
            """, (espacio_disponible[0], espera['id_vehiculo'], posicion))
            
            gestor_lista_espera.eliminar(espera['id'])
        
        conn.commit()
        conn.close()
        return redirect(url_for('mostrar_dashboard'))
        
    except Exception as error:
        app.logger.error(f"Error al procesar lista de espera: {str(error)}")
        return redirect(url_for('mostrar_dashboard'))

@app.route('/lista_espera/eliminar/<int:id_espera>')
def eliminar_espera(id_espera):
    try:
        if gestor_lista_espera.eliminar(id_espera):
            return redirect(url_for('mostrar_dashboard'))
        
        raise Exception("No se pudo eliminar de la lista de espera")
    
    except Exception as error:
        app.logger.error(f"Error al eliminar de lista de espera: {str(error)}")
        return redirect(url_for('mostrar_dashboard'))
    
@app.route('/fila/mover', methods=['POST'])
def mover_vehiculo_fila():
    try:
        id_espacio_fila = request.form.get('id_espacio_fila')
        id_vehiculo = request.form.get('id_vehiculo')
        
        if id_espacio_fila and id_vehiculo:
            conn = get_conexion()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM PilaVehiculos 
                WHERE id_espacio_fila = ? AND id_vehiculo = ?
            """, (id_espacio_fila, id_vehiculo))
            
            cursor.execute("""
                SELECT TOP 1 id_espera, id_vehiculo
                FROM ListaEspera 
                WHERE estado = 'pendiente'
                ORDER BY fecha_solicitud
            """)
            
            siguiente_en_espera = cursor.fetchone()
            
            if siguiente_en_espera:
                cursor.execute("""
                    SELECT COUNT(*) FROM PilaVehiculos 
                    WHERE id_espacio_fila = ?
                """, (id_espacio_fila,))
                
                posicion = cursor.fetchone()[0] + 1
                
                if posicion <= 3:
                    cursor.execute("""
                        INSERT INTO PilaVehiculos 
                        (id_espacio_fila, id_vehiculo, posicion, fecha_entrada)
                        VALUES (?, ?, ?, GETDATE())
                    """, (id_espacio_fila, siguiente_en_espera[1], posicion))
                    
                    cursor.execute("""
                        UPDATE ListaEspera 
                        SET estado = 'atendido'
                        WHERE id_espera = ?
                    """, (siguiente_en_espera[0],))
            
            conn.commit()
            conn.close()
            
        return redirect(url_for('mostrar_dashboard'))
        
    except Exception as error:
        print(f"Error al mover vehículo: {str(error)}")
        return redirect(url_for('mostrar_dashboard'))

@app.route('/fila/retornar/<int:id_espacio_fila>')
def retornar_vehiculos_fila(id_espacio_fila):
    try:
        conn = get_conexion()
        cursor = conn.cursor()
        
        movimientos = gestor_salidas.obtener_movimientos_pendientes(id_espacio_fila)
        
        for movimiento in movimientos:
            cursor.execute("""
                INSERT INTO PilaVehiculos (id_espacio_fila, id_vehiculo, posicion, fecha_entrada)
                VALUES (?, ?, ?, GETDATE())
            """, (id_espacio_fila, movimiento[1], movimiento[3]))
            
            gestor_salidas.registrar_retorno(movimiento[0])
        
        conn.commit()
        conn.close()
            
        return redirect(url_for('mostrar_dashboard'))
        
    except Exception as error:
        app.logger.error(f"Error al retornar vehículos: {str(error)}")
        return redirect(url_for('mostrar_dashboard'))
    
@app.route('/fila/estacionar', methods=['POST'])
def estacionar_vehiculo_fila():
    try:
        id_espacio_fila = request.form.get('id_espacio_fila')
        id_vehiculo = request.form.get('id_vehiculo')
        
        if not all([id_espacio_fila, id_vehiculo]):
            return redirect(url_for('mostrar_dashboard'))
        
        conn = get_conexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM PilaVehiculos 
            WHERE id_vehiculo = ?
        """, (id_vehiculo,))
        
        if cursor.fetchone()[0] > 0:
            print("El vehículo ya está estacionado")
            return redirect(url_for('mostrar_dashboard'))
        
        cursor.execute("""
            SELECT COUNT(*) FROM PilaVehiculos 
            WHERE id_espacio_fila = ?
        """, (id_espacio_fila,))
        
        posicion_actual = cursor.fetchone()[0]
        
        if posicion_actual < 3:
            cursor.execute("""
                INSERT INTO PilaVehiculos 
                (id_espacio_fila, id_vehiculo, posicion, fecha_entrada)
                VALUES (?, ?, ?, GETDATE())
            """, (id_espacio_fila, id_vehiculo, posicion_actual + 1))
            
        else:
            cursor.execute("""
                INSERT INTO ListaEspera 
                (id_vehiculo, fecha_solicitud, estado)
                VALUES (?, GETDATE(), 'pendiente')
            """, (id_vehiculo,))
            print(f"Espacio lleno, vehículo {id_vehiculo} agregado a lista de espera")
            
        conn.commit()
        conn.close()
        return redirect(url_for('mostrar_dashboard'))
        
    except Exception as error:
        print(f"Error al estacionar vehículo: {str(error)}")
        return redirect(url_for('mostrar_dashboard'))

def obtener_datos_espacios_fila():
    espacios = []
    try:
        conn = get_conexion()
        cursor = conn.cursor()
        
        espacios_query = """
            SELECT ef.id_espacio_fila, ef.numero_espacio 
            FROM EspaciosFila ef
            ORDER BY ef.numero_espacio
        """
        cursor.execute(espacios_query)
        espacios_raw = cursor.fetchall()
        
        for espacio in espacios_raw:
            vehiculos_query = """
                SELECT v.id_vehiculo, v.placa, pv.posicion
                FROM PilaVehiculos pv
                JOIN Vehiculos v ON v.id_vehiculo = pv.id_vehiculo
                WHERE pv.id_espacio_fila = ?
                ORDER BY pv.posicion DESC
            """
            cursor.execute(vehiculos_query, (espacio[0],))
            vehiculos = cursor.fetchall()
            
            espacio_data = {
                'id': espacio[0],
                'numero_espacio': espacio[1],
                'vehiculos': vehiculos,
                'total_vehiculos': len(vehiculos),
                'movimientos_temporales': []
            }
            espacios.append(espacio_data)
            
        conn.close()
        return espacios
        
    except Exception as error:
        print(f"Error al obtener datos de espacios: {str(error)}")
        return []

if __name__ == '__main__':
    app.run(debug=True)
