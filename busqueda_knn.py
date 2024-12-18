import os
import face_recognition
import mysql.connector
from sklearn.neighbors import NearestNeighbors
import numpy as np
import time


def conectar_a_base_de_datos():
    return mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='bd_personas'
    )

def obtener_caracteristicas_imagen_lejana(ruta_imagen_lejana):
    imagen_persona = face_recognition.load_image_file(ruta_imagen_lejana)
    rostros_persona = face_recognition.face_encodings(imagen_persona)
    if not rostros_persona:
        print("No se encontraron rostros en la imagen de lejos.")
        return None

    return rostros_persona[0]

def buscar_en_base_de_datos_knn_sin_hilos(caracteristicas_imagen_lejana, k_neighbors=1):
    conn = conectar_a_base_de_datos()
    cursor = conn.cursor()

    start_time = time.time()

    cursor.execute("SELECT nombre, caracteristicas FROM personas_100")
    resultados = cursor.fetchall()

    if not resultados:
        print("La base de datos está vacía.")
        return

    nombres_db = []
    caracteristicas_db = []

    for nombre, caracteristicas_bd_str in resultados:
        nombres_db.append(nombre)
        caracteristicas_db.append(list(map(float, caracteristicas_bd_str.split(','))))

    conn.close()

    caracteristicas_db = np.array(caracteristicas_db)
    caracteristicas_imagen_lejana = np.array([caracteristicas_imagen_lejana])

    nbrs = NearestNeighbors(n_neighbors=k_neighbors, algorithm='auto').fit(caracteristicas_db)
    distances, indices = nbrs.kneighbors(caracteristicas_imagen_lejana)

    end_time = time.time()

    search_time = end_time - start_time
    print(f"Tiempo de búsqueda (sin hilos): {search_time} segundos")

    if indices.any():
        indices = indices.flatten()
        print(f"La persona de la imagen de lejos tiene las mismas características que la(s) persona(s): {', '.join(nombres_db[i] for i in indices)} en la base de datos.")
    else:
        print("No se encontraron coincidencias en la base de datos.")


if __name__ == "__main__":
    ruta_imagen_lejana = 'C:/VIII Semestre/Computacion paralela/python_Ejercicios/segunda_unidad/fotos/lejos/lejos_10.png'

    caracteristicas_imagen_lejana = obtener_caracteristicas_imagen_lejana(ruta_imagen_lejana)

    if caracteristicas_imagen_lejana is not None:
        buscar_en_base_de_datos_knn_sin_hilos(caracteristicas_imagen_lejana)
