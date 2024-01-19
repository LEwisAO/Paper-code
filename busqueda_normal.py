import os
import face_recognition
import mysql.connector
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
    #print(imagen_persona)
    #print(rostros_persona)
    if not rostros_persona:
        print("No se encontraron rostros en la imagen de lejos.")
        return None

    # Tomar el primer rostro (asumiendo una sola persona por imagen)
    return rostros_persona[0]

def buscar_en_base_de_datos(caracteristicas_imagen_lejana):
    conn = conectar_a_base_de_datos()
    cursor = conn.cursor()

    # Medir el tiempo de búsqueda
    start_time = time.time()

    cursor.execute("SELECT nombre, caracteristicas FROM personas_10000")
    resultados = cursor.fetchall()

    coincidencias = []

    for nombre, caracteristicas_bd_str in resultados:
        caracteristicas_bd = list(map(float, caracteristicas_bd_str.split(',')))
        distancia = distancia_de_hamming(caracteristicas_imagen_lejana, caracteristicas_bd)

        if distancia == 0:
            coincidencias.append(nombre)

    conn.close()

    end_time = time.time()

    # Calcular y mostrar el tiempo de búsqueda
    search_time = end_time - start_time
    print(f"Tiempo de búsqueda: {search_time} segundos")

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
    ruta_imagen_lejana = 'C:/VIII Semestre/Computacion paralela/python_Ejercicios/segunda_unidad/fotos/lejos/lejos_9996.jpg'

    caracteristicas_imagen_lejana = obtener_caracteristicas_imagen_lejana(ruta_imagen_lejana)

    if caracteristicas_imagen_lejana is not None:
        buscar_en_base_de_datos(caracteristicas_imagen_lejana)