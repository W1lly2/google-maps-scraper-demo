from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# 🔹 FUNCIONES
def obtener_keywords():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
    client = gspread.authorize(creds)
    hoja = client.open("keywords_scraper").sheet1
    datos = hoja.col_values(1)[1:]  # Salta encabezado
    return datos


def buscar_en_google_maps(keyword):
    print(f"\n🔍 Buscando: {keyword}")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
    driver.get(url)
    time.sleep(5)  # Esperar carga

    resultados = []

    negocios = driver.find_elements(By.CLASS_NAME, 'hfpxzc')  # Tarjetas de negocio

    for negocio in negocios[:10]:  # Limita a 10
        try:
            negocio.click()
            time.sleep(3)

            nombre = driver.find_element(By.CLASS_NAME, 'DUwDvf').text
            direccion = driver.find_element(By.CLASS_NAME, 'Io6YTe').text
            telefono = ''
            website = ''

            detalles = driver.find_elements(By.CLASS_NAME, 'UsdlK')
            for d in detalles:
                texto = d.text
                if "http" in texto:
                    website = texto
                elif texto.startswith("+") or texto.replace(" ", "").isdigit():
                    telefono = texto

            resultados.append({
                'nombre': nombre,
                'direccion': direccion,
                'telefono': telefono,
                'website': website
            })
        except Exception as e:
            print("❌ Error con un negocio:", e)

    driver.quit()
    return resultados

def guardar_resultados_en_hoja(keyword, resultados):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
    client = gspread.authorize(creds)

    hoja_resultados = client.open("keywords_scraper").worksheet("resultados")

    for r in resultados:
        fila = [
            keyword,
            r['nombre'],
            r['direccion'],
            r['telefono'],
            r['website']
        ]
        hoja_resultados.append_row(fila)

# 🔹 PROGRAMA PRINCIPAL
if __name__ == "__main__":
    keywords = obtener_keywords()
    print("\n📋 Keywords encontradas en Google Sheets:")
    for kw in keywords:
        print("-", kw)

    for kw in keywords:
        resultados = buscar_en_google_maps(kw)
        guardar_resultados_en_hoja(kw, resultados)
        print(f"✅ Guardado {len(resultados)} resultados para '{kw}'")