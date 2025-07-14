"""
Módulo para la gestión de usuarios.
Contiene la clase Usuario y su gestor para operaciones con la base de datos.
"""
from .base import ModeloBase, GestorBase
from app.db_config import get_conexion

class Usuario(ModeloBase): # Hereda de Clase padre ModeloBase
    """
    Clase que representa a un usuario del sistema.
    
    Atributos:
        _cedula (str): Número de identificación
        _nombre (str): Nombre completo
        _telefono (str): Número de teléfono
        _email (str): Dirección de correo electrónico
    """
    
    def __init__(self, cedula: str, nombre: str, telefono: str, email: str = ''):
        """
        Inicializa una nueva instancia de Usuario.
        
        Args:
            cedula: Número de identificación único
            nombre: Nombre completo del usuario
            telefono: Número de contacto
            email: Dirección de correo (opcional)
        """
        super().__init__()
        self._cedula = cedula
        self._nombre = nombre
        self._telefono = telefono
        self._email = email

    @property
    def cedula(self) -> str:
        """Devuelve el número de cédula del usuario."""
        return self._cedula

    @property
    def nombre(self) -> str:
        """Devuelve el nombre completo del usuario."""
        return self._nombre

    @property
    def telefono(self) -> str:
        """Devuelve el número de teléfono del usuario."""
        return self._telefono

    @property
    def email(self) -> str:
        """Devuelve la dirección de email del usuario."""
        return self._email

    @email.setter
    def email(self, value: str):
        """
        Establece la dirección de email con validación básica.
        
        Args:
            value: Nueva dirección de email
            
        Raises:
            ValueError: Si el email no contiene '@'
        """
        if '@' not in value:
            raise ValueError("El email debe contener @")
        self._email = value

class GestorUsuarios(GestorBase):
    """
    Gestor para operaciones de usuarios en la base de datos.
    Hereda de GestorBase e implementa los métodos CRUD.
    """
    
    def crear(self, usuario: Usuario) -> bool:
        """
        Crea un nuevo usuario en la base de datos.
        
        Args:
            usuario: Instancia de Usuario a crear
            
        Returns:
            bool: True si se creó correctamente, False si falló
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Usuarios (cedula, nombre, telefono, email) VALUES (?, ?, ?, ?)",
                (usuario.cedula, usuario.nombre, usuario.telefono, usuario.email)
            )
            conn.commit()
            return True
            
        except Exception as error:
            print(f"Error al crear usuario: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def obtener(self, id_usuario: int) -> Usuario:
        """
        Obtiene un usuario por su ID.
        
        Args:
            id_usuario: ID del usuario a buscar
            
        Returns:
            Usuario: Instancia del usuario encontrado o None
        """
        try:
            conn = get_conexion()
            if not conn:
                return None
                
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_usuario, cedula, nombre, telefono, email FROM Usuarios WHERE id_usuario = ?",
                (id_usuario,)
            )
            fila = cursor.fetchone()
            
            if fila:
                usuario = Usuario(
                    cedula=fila[1],
                    nombre=fila[2],
                    telefono=fila[3],
                    email=fila[4]
                )
                usuario._id = fila[0]
                return usuario
            return None
            
        except Exception as error:
            print(f"Error al obtener usuario: {str(error)}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_todos(self) -> list[Usuario]:
        """
        Obtiene todos los usuarios registrados en el sistema.
        
        Returns:
            list[Usuario]: Lista de objetos Usuario
        """
        try:
            conn = get_conexion()
            if not conn:
                return []
                
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_usuario, cedula, nombre, telefono, email FROM Usuarios"
            )
            
            usuarios = []
            for fila in cursor.fetchall():
                usuario = Usuario(
                    cedula=fila[1],
                    nombre=fila[2],
                    telefono=fila[3],
                    email=fila[4]
                )
                usuario._id = fila[0]
                usuarios.append(usuario)
                
            return usuarios
            
        except Exception as error:
            print(f"Error al obtener usuarios: {str(error)}")
            return []
        finally:
            if conn:
                conn.close()

    def actualizar(self, usuario: Usuario) -> bool:
        """
        Actualiza los datos de un usuario existente.
        
        Args:
            usuario: Instancia de Usuario con los datos actualizados
            
        Returns:
            bool: True si se actualizó correctamente, False si falló
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE Usuarios 
                SET cedula = ?, nombre = ?, telefono = ?, email = ? 
                WHERE id = ?""",
                (usuario.cedula, usuario.nombre, 
                 usuario.telefono, usuario.email, 
                 usuario.id)
            )
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as error:
            print(f"Error al actualizar usuario: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def eliminar(self, id_usuario: int) -> bool:
        """
        Elimina un usuario del sistema.
        
        Args:
            id_usuario: ID del usuario a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si falló
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM Usuarios WHERE id = ?",
                (id_usuario,)
            )
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as error:
            print(f"Error al eliminar usuario: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()

    def contar(self) -> int:
        """
        Cuenta el total de usuarios registrados en el sistema.
        
        Returns:
            int: Número total de usuarios
        """
        try:
            conn = get_conexion()
            if not conn:
                return 0
                
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Usuarios")
            return cursor.fetchone()[0]
            
        except Exception as error:
            print(f"Error al contar usuarios: {str(error)}")
            return 0
        finally:
            if conn:
                conn.close()

    def existe_cedula(self, cedula: str) -> bool:
        """
        Verifica si ya existe un usuario con la cédula especificada.
        
        Args:
            cedula: Número de cédula a verificar
            
        Returns:
            bool: True si existe, False si no
        """
        try:
            conn = get_conexion()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM Usuarios WHERE cedula = ?",
                (cedula,)
            )
            return cursor.fetchone()[0] > 0
            
        except Exception as error:
            print(f"Error al verificar cédula: {str(error)}")
            return False
        finally:
            if conn:
                conn.close()