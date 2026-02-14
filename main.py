from db  import obtener_conexion
from seguridad import hash_password
from datetime import datetime


def crear_tabla():
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            codigo TEXT PRIMARY KEY,
            nombre TEXT,
            talla TEXT,
            precio INTEGER,
            stock INTEGER
        )
    """)

    conn.commit() 
    conn.close()


def insertar_producto(codigo, nombre, talla, precio, stock):
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO productos (codigo, nombre, talla, precio, stock)
        VALUES (?, ?, ?, ?, ?)
    """, (codigo, nombre, talla, precio, stock))

    conn.commit()
    conn.close()



def cargar_productos_desde_bd():
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT codigo, nombre, talla, precio, stock FROM productos")
    filas = cursor.fetchall()

    conn.close()

    productos = []
    for fila in filas:
        productos.append({
            "codigo": fila[0],
            "nombre": fila[1],
            "talla": fila[2],
            "precio": fila[3],
            "stock": fila[4]
        })

    return productos


def vender_producto_por_codigo_bd(codigo, usuario):
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT stock FROM productos WHERE codigo = ?",
        (codigo,)
    )
    resultado = cursor.fetchone()

    if not resultado:
        conn.close()
        return {"ok": False, "mensaje": "Producto no encontrado"}

    stock = resultado[0]

    if stock <= 0:
        conn.close()
        return {"ok": False, "mensaje": "No hay stock disponible"}

    cursor.execute(
        "UPDATE productos SET stock = stock - 1 WHERE codigo = ?",
        (codigo,)
    )

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO ventas (usuario, codigo_producto, cantidad, fecha) VALUES (?, ?, ?, ?)",
        (usuario, codigo, 1, fecha)
    )

    conn.commit()
    conn.close()

    return {"ok": True, "mensaje": "Producto vendido correctamente"}

def crear_tabla_usuarios():
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            password TEXT,
            rol TEXT
        )
    """)

    conn.commit()
    conn.close()


def crear_usuario(usuario, password, rol):
    
    password_hash = hash_password(password)
    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)",
            (usuario, password_hash, rol)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print("El usuario ya existe")
    finally:
        conn.close()


def crear_tabla_ventas():
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            codigo_producto TEXT,
            cantidad INTEGER,
            fecha TEXT
        )
    """)

    conn.commit()
    conn.close()

    from datetime import datetime

def registrar_venta(usuario, codigo, cantidad):
    conn = obtener_conexion()
    cursor = conn.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO ventas (usuario, codigo_producto, cantidad, fecha) VALUES (?, ?, ?, ?)",
        (usuario, codigo, cantidad, fecha)
    )
    conn.commit()
    conn.close()



def login(usuario, password):
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT rol FROM usuarios WHERE usuario = ? AND password = ?",
        (usuario, password)
    )

    fila = cursor.fetchone()
    conn.close()

    if fila is None:
        return {"ok": False, "mensaje": "Credenciales inválidas"}

    return {
        "ok": True,
        "usuario": usuario,
        "rol": fila[0]
    }


def calcular_valor_total(inventario):
    total = 0

    for producto in inventario:
        total += producto["precio"] * producto["stock"]

    return total

def mostrar_valor_total(inventario):
    total = calcular_valor_total(inventario)
    print(f"Valor total del inventario: ${total}")
    

def vender_producto(usuario_actual):
    codigo = input("Ingresa el código del producto a vender: ")
    resultado = vender_producto_por_codigo_bd(codigo, usuario_actual["usuario"])
    print(resultado["mensaje"])

def agregar_stock(codigo, cantidad):
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT stock FROM productos WHERE codigo = ?",
        (codigo,)
    )
    resultado = cursor.fetchone()

    if not resultado:
        conn.close()
        return {"ok": False, "mensaje": "Producto no encontrado"}

    cursor.execute(
        "UPDATE productos SET stock = stock + ? WHERE codigo = ?",
        (cantidad, codigo)
    )

    conn.commit()
    conn.close()

    return {"ok": True, "mensaje": f"Stock aumentado en {cantidad} unidades"}

def agregar_stock_interactivo():
    codigo = input("Código del producto: ")
    try:
        cantidad = int(input("Cantidad a agregar: "))
    except ValueError:
        print("Cantidad inválida")
        return

    if cantidad <= 0:
        print("La cantidad debe ser mayor que cero")
        return

    resultado = agregar_stock(codigo, cantidad)
    print(resultado["mensaje"])


def procesar_opcion(opcion, usuario_actual):
    if opcion == "1":
        print("\nInventario:")
        inventario = cargar_productos_desde_bd()
        for producto in inventario:
            print(f'{producto["nombre"]} - Stock: {producto["stock"]}')

    elif opcion == "2":
        inventario = cargar_productos_desde_bd()
        mostrar_valor_total(inventario)

    elif opcion == "3":
        if usuario_actual["rol"] not in ("admin", "vendedor"):
            print("No tienes permiso para vender productos")
            return True
        
        vender_producto(usuario_actual)

    elif opcion == "4":
        print("Saliendo del sistema...")
        return False

    else:
        print("Opción no válida")

    return True


def mostrar_menu(rol):
    print("\nSISTEMA DE INVENTARIO 2026")
    print("1. Ver inventario")
    print("2. Ver valor total")

    if rol == "vendedor":    
        print("3. Vender producto")

    print("4. Salir")


def borrar_usuario():
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios;")

    conn.commit()
    conn.close()

    print("Usuarios eliminados correctamente")


def ver_usuarios():
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT usuario, rol FROM usuarios")
    filas = cursor.fetchall()

    conn.close()

    print("\nUSUARIOS REGISTRADOS:")
    for usuario, rol in filas:
        print(f" - usuario: {usuario} | Rol: {rol}")


def ver_tabla(nombre_tabla):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {nombre_tabla}")
    filas = cursor.fetchall()

    if not filas:
        print("No hay informacion en la Tabla")

    conn.close
    for fila in filas:
        print(fila)


def ver_tablas():
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """)

    tablas = cursor.fetchall()
    conn.close()

    if not tablas:
        print("No hay tablas en la base de datos")
        return

    print("\nTABLAS EN LA BASE DE DATOS")
    print("-" * 30)

    for tabla in tablas:
        print(f"- {tabla[0]}")



def main():
    print("=== LOGIN ===")
    usuario = input("Usuario: ")
    password = input("Contraseña: ")
    password_hash = hash_password(password)

    resultado = login(usuario, password_hash)

    if not resultado["ok"]:
        print(resultado["mensaje"])
        return  # corta el programa

    usuario_actual = {
        "usuario": resultado["usuario"],
        "rol": resultado["rol"]
    }


    inventario = cargar_productos_desde_bd()
    print(usuario)

    while True:
        mostrar_menu(usuario_actual["rol"])
        opcion = input("Elige una opción: ")

        continuar = procesar_opcion(opcion, usuario_actual)
        if not continuar:
            break

if __name__ == "__main__":
    #main()
    #agregar_stock_interactivo()
    ver_tabla("ventas")
    #ver_tabla("usuarios")
    #crear_usuario("stewart", "123", "vendedor)

