import os
import time
from selenium import webdriver

def capturar_pantallas(url, carpeta_destino, cantidad_capturas):
    # Configura el driver de Selenium (asegúrate de tener el driver correspondiente instalado)
    # En este ejemplo, se utiliza el driver de Chrome. Puedes cambiarlo según tu navegador.
    driver = webdriver.Chrome()

    try:
        # Abre la página web
        driver.get(url)

        # Espera un tiempo para cargar completamente la página (puedes ajustar este tiempo según tu necesidad)
        time.sleep(2)

        for i in range(1200, cantidad_capturas + 1):
            # Toma la captura de pantalla y guarda en la carpeta destino con el nombre especificado
            nombre_archivo = f"persona_{i}.png"
            ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
            driver.save_screenshot(ruta_destino)
            print(f"Captura de pantalla {i} guardada en {ruta_destino}")

            # Espera un tiempo antes de la siguiente captura
            time.sleep(2)

            # Actualiza la página para obtener una nueva imagen
            driver.refresh()
            # Espera un tiempo para cargar completamente la página después de la actualización
            time.sleep(2)

    finally:
        # Cierra el navegador al finalizar
        driver.quit()

if __name__ == "__main__":
    # Especifica la URL de la página web que genera las imágenes sintéticas
    url_pagina_web = "https://thispersondoesnotexist.com/"

    # Especifica la carpeta destino donde guardar las capturas de pantalla
    carpeta_destino = "C:/VIII Semestre/Computacion paralela/python_Ejercicios/segunda_unidad/fotos/perfil"

    # Especifica la cantidad de capturas de pantalla que deseas tomar
    cantidad_capturas = 10000

    capturar_pantallas(url_pagina_web, carpeta_destino, cantidad_capturas)
