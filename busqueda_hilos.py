import os
import face_recognition
import mysql.connector
from sklearn.neighbors import NearestNeighbors, KDTree
import numpy as np
import time
import threading

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

def buscar_en_base_de_datos_knn_kd_tree(caracteristicas_imagen_lejana, k_neighbors=1, num_threads=None):
    conn = conectar_a_base_de_datos()
    cursor = conn.cursor()

    start_time_threaded = time.time()

    cursor.execute("SELECT nombre, caracteristicas FROM personas_10000")
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

    tree = KDTree(caracteristicas_db, leaf_size=30)

    if num_threads is None:
        num_threads = threading.active_count()

    start_time_threaded = time.time()

    def worker(start, end, results):
        distances_threaded, indices_threaded = tree.query(caracteristicas_imagen_lejana, k=k_neighbors, return_distance=True)
        indices_threaded = indices_threaded[0]  # Tomar el primer conjunto de índices
        results.extend(indices_threaded)

    chunk_size = len(caracteristicas_db) // num_threads
    threads = []
    results = []

    for i in range(num_threads):
        start_index = i * chunk_size
        end_index = start_index + chunk_size if i < num_threads - 1 else len(caracteristicas_db)
        thread = threading.Thread(target=worker, args=(start_index, end_index, results))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    end_time_threaded = time.time()

    search_time_threaded = end_time_threaded - start_time_threaded
    print(f"Tiempo de búsqueda con hilos utilizando k-d tree ({num_threads} hilos): {search_time_threaded} segundos")

    if results:
        # Filtrar duplicados y verificar que los resultados sean iguales
        indices_threaded = np.unique(results)
        if np.array_equal(indices_threaded, np.arange(len(indices_threaded))):
            print("Los resultados con hilos son iguales a los resultados sin hilos.")
        else:
            print("¡Los resultados con hilos son diferentes a los resultados sin hilos!")

        if indices_threaded.any():
            print(f"La persona de la imagen de lejos tiene las mismas características que la(s) persona(s): {', '.join(nombres_db[i] for i in indices_threaded)} en la base de datos.")
        else:
            print("No se encontraron coincidencias en la base de datos.")
    else:
        print("No se obtuvieron resultados durante la búsqueda con hilos.")

if __name__ == "__main__":
    ruta_imagen_lejana = 'C:/VIII Semestre/Computacion paralela/python_Ejercicios/segunda_unidad/fotos/lejos/lejos_9996.jpg'

    caracteristicas_imagen_lejana = obtener_caracteristicas_imagen_lejana(ruta_imagen_lejana)

    if caracteristicas_imagen_lejana is not None:
        num_threads = 12
        buscar_en_base_de_datos_knn_kd_tree(caracteristicas_imagen_lejana, num_threads=num_threads)
