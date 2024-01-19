import os
import face_recognition
import mysql.connector
from mysql.connector import Error

def conectar_a_base_de_datos():
    return mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='bd_personas'
    )

def obtener_ultimo_id():
    conn = conectar_a_base_de_datos()
    cursor = conn.cursor()
    
    cursor.execute('SELECT MAX(id) FROM personas_10000')
    ultimo_id = cursor.fetchone()[0]

    conn.close()

    return ultimo_id

def obtener_primer_id_disponible():
    ultimo_id = obtener_ultimo_id() or 0

    conn = conectar_a_base_de_datos()
    cursor = conn.cursor()

    while True:
        cursor.execute('SELECT id FROM personas_10000 WHERE id = %s', (ultimo_id + 1,))
        if not cursor.fetchone():
            break
        ultimo_id += 1

    conn.close()

    return ultimo_id + 1

def agregar_a_base_de_datos(nombre, caracteristicas):
    conn = conectar_a_base_de_datos()
    cursor = conn.cursor()

    nuevo_id = obtener_primer_id_disponible()

    try:
        cursor.execute('''
            INSERT INTO personas_10000 (id, nombre, caracteristicas) VALUES (%s, %s, %s)
        ''', (nuevo_id, nombre, caracteristicas))

        conn.commit()
    except Error as e:
        print(f"Error al agregar a la base de datos: {e}")

    conn.close()

def procesar_carpeta_personas(carpeta_personas):
    for archivo in os.listdir(carpeta_personas):
        if archivo.endswith(".jpg") or archivo.endswith(".JPG") or archivo.endswith(".png"):
            ruta_completa = os.path.join(carpeta_personas, archivo)

            imagen = face_recognition.load_image_file(ruta_completa)
            rostros_persona = face_recognition.face_encodings(imagen)

            if not rostros_persona:
                print(f"No se encontraron rostros en la imagen de {archivo}.")
                continue

            rostro_persona = rostros_persona[0]

            nombre_persona = os.path.splitext(archivo)[0]

            caracteristicas_str = ','.join(map(str, rostro_persona))

            # Agregar a la base de datos
            agregar_a_base_de_datos(nombre_persona, caracteristicas_str)

if __name__ == "__main__":
    carpeta_personas_path = 'C:/VIII Semestre/Computacion paralela/python_Ejercicios/segunda_unidad/fotos/perfil_10000'

    procesar_carpeta_personas(carpeta_personas_path)
