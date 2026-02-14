import sqlite3

DB_NAME = "inventario.db"

def obtener_conexion():
    return sqlite3.connect(DB_NAME)
