import os
import face_recognition
import mysql.connector
import concurrent.futures
import time

def conectar_a_base_de_datos():
    # Ajusta los valores de usuario, contraseña, host y base de datos según tu configuración de XAMPP
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

    # Tomar el primer rostro (asumiendo una sola persona por imagen)
    return rostros_persona[0]

def buscar_en_base_de_datos(caracteristicas_imagen_lejana, resultados, index_start, index_end):
    conn = conectar_a_base_de_datos()

    coincidencias = []

    for i in range(index_start, index_end):
        nombre, caracteristicas_bd_str = resultados[i]
        caracteristicas_bd = list(map(float, caracteristicas_bd_str.split(',')))
        distancia = distancia_de_hamming(caracteristicas_imagen_lejana, caracteristicas_bd)

        if distancia == 0:
            coincidencias.append(nombre)

    conn.close()

    if coincidencias:
        print(f"La persona de la imagen de lejos tiene las mismas características que la(s) persona(s): {', '.join(coincidencias)} en la base de datos.")
    else:
        print("No se encontraron coincidencias en la base de datos.")

def distancia_de_hamming(caracteristicas_1, caracteristicas_2):
    if len(caracteristicas_1) != len(caracteristicas_2):
        raise ValueError("Los vectores de características deben tener la misma longitud.")

    distancia = 0
    for i in range(len(caracteristicas_1)):
        if caracteristicas_1[i] != caracteristicas_2[i]:
            distancia += 1

    return distancia

if __name__ == "__main__":
    ruta_imagen_lejana = 'C:/VIII Semestre/Computacion paralela/python_Ejercicios/segunda_unidad/fotos/lejos/lejos_10.png'

    caracteristicas_imagen_lejana = obtener_caracteristicas_imagen_lejana(ruta_imagen_lejana)

    if caracteristicas_imagen_lejana is not None:
        conn = conectar_a_base_de_datos()
        cursor = conn.cursor()

        cursor.execute("SELECT nombre, caracteristicas FROM personas_100")
        resultados = cursor.fetchall()

        # Especifica el número de hilos (puedes ajustarlo según la cantidad de datos)
        num_hilos = 12

        # Divide los resultados entre los hilos
        chunk_size = len(resultados) // num_hilos
        chunks = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_hilos - 1)]
        chunks.append(((num_hilos - 1) * chunk_size, len(resultados)))

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_hilos) as executor:
            futures = [executor.submit(buscar_en_base_de_datos, caracteristicas_imagen_lejana, resultados, start, end) for start, end in chunks]

            # Espera a que todos los hilos completen
            concurrent.futures.wait(futures)

        end_time = time.time()
        total_time = end_time - start_time

        print(f"Tiempo total de ejecución: {total_time} segundos")

        conn.close()
