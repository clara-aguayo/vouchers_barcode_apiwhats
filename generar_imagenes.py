import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from textwrap import wrap
import requests

# ============ CONFIGURACIÓN GENERAL ============
CSV_VALES_PATH = r"Ingresar ubicación de la carpeta datos, etc"
CSV_NUMEROS_PATH = r"Ingresar ubi del csv que se llama numeros"
IMAGE_PATH = r"ingresar ubi de la imagen base a utilizar"
OUTPUT_FOLDER_NAME = "Vales"

COLUMN_NAME = "CODIGO"
COLUMN_MONTO = "SALDO"
COLUMN_PHONE = "telefonos"

TEXT_POSITION = (340, 265)
BARCODE_POSITION = (300, 150)
TEXTBOX_POSITION = (120, 310)
TEXTBOX_SIZE = (700, 50)
TEXTBOX_FILL = (255, 255, 255)

FONT_PATH = r"C:\Windows\Fonts\Poppins-ExtraLight.ttf"
BOLD_FONT_PATH = r"C:\Windows\Fonts\arialbd.ttf"
FONT_SIZE = 30
TEXT_FILL = (0, 0, 0)

# ============ IMAGEKIT ============
from imagekitio import ImageKit

IMAGEKIT_PUBLIC_KEY = "public_bMuUDTJJgIEzdvcretZQjuS1fmo="
IMAGEKIT_PRIVATE_KEY = "private_VJ5KLMRlxHJ4TZaAcQCDqHaKA0g="
IMAGEKIT_URL_ENDPOINT = "https://ik.imagekit.io/caguayo25/"

ik = ImageKit(
    public_key=IMAGEKIT_PUBLIC_KEY,
    private_key=IMAGEKIT_PRIVATE_KEY,
    url_endpoint=IMAGEKIT_URL_ENDPOINT
)

# ============ WHATSAPP CLOUD API ============ OJO
WHATSAPP_TOKEN = "INGRESAR TOKEN"
PHONE_NUMBER_ID = "Ingresar_whats"
WHATSAPP_API_URL = f"ingresar link ejemplo: https://graph.facebook.com/"

WHATSAPP_MESSAGE = (
    "Holaa, se le ha asignado un vale de la X, "
    "puede pasar a realizar sus compras en cualquiera de nuestras tiendas."
)

# ============ FUNCIONES ============

def limpiar_codigo_vale(valor):
    """Convierte códigos como 5,07E+17 a enteros correctos."""
    s = str(valor).strip().replace(",", ".")
    try:
        return str(int(float(s)))
    except:
        return "".join(c for c in s if c.isdigit())


def formatear_monto(valor):
    monto_raw = str(valor).strip()
    monto_limpio = "".join(c for c in monto_raw if c.isdigit()) or "0"
    return f"{int(monto_limpio):,}".replace(",", ".") + " Gs"


UNIDADES = ["", "uno", "dos", "tres", "cuatro", "cinco",
            "seis", "siete", "ocho", "nueve"]
DECENAS = ["", "diez", "veinte", "treinta", "cuarenta",
           "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]
ESPECIALES = {11:"once",12:"doce",13:"trece",14:"catorce",15:"quince",
              16:"dieciseis",17:"diecisiete",18:"dieciocho",19:"diecinueve"}


def numero_a_letras(n):
    n = int(n)
    if n == 0:
        return "cero guaranies"

    miles = n // 1000
    resto = n % 1000
    letras = ""

    if miles > 0:
        letras += f"{numero_a_letras(miles).replace(' guaranies','')} mil "

    centenas = resto // 100
    decenas = (resto % 100) // 10
    unidades = resto % 100 % 10

    if resto % 100 in ESPECIALES:
        letras += ESPECIALES[resto % 100]
    else:
        if centenas > 0:
            if centenas == 1 and resto % 100 == 0:
                letras += "cien "
            elif centenas == 1:
                letras += "ciento "
            elif centenas == 5:
                letras += "quinientos "
            elif centenas == 7:
                letras += "setecientos "
            elif centenas == 9:
                letras += "novecientos "
            else:
                letras += UNIDADES[centenas] + "cientos "

        if decenas > 0:
            letras += DECENAS[decenas]
            if unidades > 0:
                letras += " y "

        if unidades > 0:
            letras += UNIDADES[unidades]

    return letras.strip() + " guaranies"


def validar_numero(numero):
    return numero.isdigit() and len(numero) == 10 and numero.startswith("09")


def subir_a_imagekit(filepath, filename):
    """Sube un archivo a ImageKit y retorna la URL pública."""
    try:
        with open(filepath, "rb") as f:
            upload = ik.upload_file(
                file=f,
                file_name=filename,
                # opcional: folder="/vales",
            )

        raw = upload.response_metadata.raw  # dict con la respuesta completa
        return raw.get("url")
    except Exception as e:
        print("Error al subir a ImageKit:", e)
        return None


def enviar_whatsapp_por_url(numero, image_url, mensaje_texto):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": f"595{numero[1:]}",
        "type": "image",
        "image": {"link": image_url},
        "caption": mensaje_texto
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    return response.status_code, response.text


def generate_barcode_image(number):
    number_digits = "".join(filter(str.isdigit, number))
    code = barcode.get("code128", number_digits, writer=ImageWriter())
    temp_path = Path("temp_barcode")
    saved_path = code.save(str(temp_path), {"module_height": 90, "quiet_zone": 2, "write_text": False})
    barcode_img = Image.open(saved_path).convert("RGBA")
    os.remove(saved_path)

    CM_TO_PX = 37.8
    barcode_img = barcode_img.resize((int(10 * CM_TO_PX), int(3 * CM_TO_PX)), Image.LANCZOS)
    return barcode_img


def load_font(font_path, size):
    try:
        return ImageFont.truetype(font_path, size=size)
    except:
        return ImageFont.load_default()


def get_desktop_vales_folder():
    folder = Path.home() / "Desktop" / OUTPUT_FOLDER_NAME
    folder.mkdir(parents=True, exist_ok=True)
    return folder


# ============ MAIN ============

def main():
    # Validar archivos
    if not os.path.exists(CSV_VALES_PATH) or not os.path.exists(CSV_NUMEROS_PATH) or not os.path.exists(IMAGE_PATH):
        print("Archivos faltantes")
        return

    # Leer archivos
    df_vales = pd.read_csv(CSV_VALES_PATH, sep=';')
    df_vales.columns = [c.strip() for c in df_vales.columns]

    df_numeros = pd.read_excel(CSV_NUMEROS_PATH, dtype=str)
    df_numeros.columns = [c.strip() for c in df_numeros.columns]

    # Validar cantidad
    if len(df_vales) != len(df_numeros):
        print("Cantidad de vales y teléfonos no coincide")
        return

    # Preparar entorno
    out_folder = get_desktop_vales_folder()
    font = load_font(FONT_PATH, FONT_SIZE)
    base_img = Image.open(IMAGE_PATH).convert("RGB")

    # Procesar cada vale
    for idx, row in df_vales.iterrows():
        img = base_img.copy()
        draw = ImageDraw.Draw(img)

        # Limpiar código
        num_vale = limpiar_codigo_vale(row[COLUMN_NAME])

        monto_final = formatear_monto(row[COLUMN_MONTO])
        monto_letras = numero_a_letras(row[COLUMN_MONTO])

        # Código de barras
        barcode_img = generate_barcode_image(num_vale)
        img.paste(barcode_img, BARCODE_POSITION, barcode_img)

        draw.text(TEXT_POSITION, num_vale, font=font, fill=TEXT_FILL)

        # Texto grande
        x, y = TEXTBOX_POSITION
        draw.rectangle([(x, y), (x + TEXTBOX_SIZE[0], y + TEXTBOX_SIZE[1])], fill=TEXTBOX_FILL)
        texto = (
            f"Con la sola presentación de esta orden y su documento de identidad "
            f"se le expedirá mercaderías por el valor de Gs. {monto_final} ({monto_letras})\n"
            "Orden válida en cualquiera de las sucursales de CADENA REAL S.A"
        )
        for line in wrap(texto, 60):
            draw.text((x + 8, y + 5), line, font=font, fill=TEXT_FILL)
            y += FONT_SIZE + 5

        # Guardar imagen local
        filename = f"{num_vale}.jpg"
        img_path = out_folder / filename
        img.save(img_path, quality=95)

        # Validar número
        telefono = str(df_numeros.iloc[idx][COLUMN_PHONE]).strip().zfill(10)
        if not validar_numero(telefono):
            print(f"Número inválido para el vale {num_vale}: {telefono}")
            continue

        # Subir a IMAGEKIT
        print(f"Subiendo {filename} a ImageKit...")
        url_publica = subir_a_imagekit(str(img_path), filename)

        if not url_publica:
            print(f"No se pudo subir el vale {num_vale}")
            continue

        print(f"URL pública: {url_publica}")

        # Enviar por WhatsApp
        print(f"Enviando a {telefono}...")
        status, resp = enviar_whatsapp_por_url(telefono, url_publica, WHATSAPP_MESSAGE)

        if status == 200:
            print(f"Vale {num_vale} enviado correctamente.")
        else:
            print(f"Error enviando vale {num_vale}: {resp}")

    print("\n Todos los vales fueron procesados correctamente.")


if __name__ == "__main__":
    main()
