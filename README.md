# vouchers_barcode_apiwhats
Sistema en Python que genera vales personalizados con código de barras, los sube automáticamente a ImageKit y los envía por WhatsApp Cloud API a los clientes. Automatiza la creación, hosting y entrega digital de vales comerciales.


#  Generador y Envío Automático de Vales por WhatsApp

Este proyecto automatiza la creación y distribución de vales comerciales.  
A partir de un archivo CSV con vales y un archivo Excel con números telefónicos, el sistema genera imágenes personalizadas, sube cada vale a ImageKit y lo envía automáticamente al cliente final mediante **WhatsApp Cloud API**.

---

##  Características principales

- **Lectura de vales desde CSV** (`vales.csv`)
- **Lectura de teléfonos desde Excel** (`numeros.xlsx`)
-  **Generación de imágenes personalizadas**
  - Código del vale
  - Código de barras Code128
  - Monto formateado (Gs.)
  - Monto en letras
  - Cuadro de condiciones
  - Plantilla base editable
- Subida automática de cada vale a ImageKit**
- Envío automatizado del vale por WhatsApp Cloud API**
- Validación de números en formato paraguayo (09xxxxxxxx)**
- Guardado local en `/Desktop/Vales/`

---

Tecnologías utilizadas

- **Python 3.x**
- Pillow (PIL)
- pandas
- python-barcode
- requests
- ImageKit Python SDK
- WhatsApp Cloud API (Meta)

---

Estructura general del proceso

1. Leer el archivo `vales.csv` con:
   - Código del vale  
   - Monto  
2. Leer el archivo `numeros.xlsx` con:
   - Número telefónico para cada vale  
3. Generar la imagen:
   - Código del vale
   - Código de barras
   - Monto y monto en letras
   - Texto de condiciones
   - Plantilla base (`base.jpg`)
4. Guardar la imagen localmente.
5. Subirla a ImageKit → obtener URL pública.
6. Enviar esa URL al cliente vía WhatsApp Cloud API.

---

##  ¿Cómo usar?

1. Configurar rutas en el código:
   ```python
   CSV_VALES_PATH = r"C:\Users\...\vales.csv"
   CSV_NUMEROS_PATH = r"C:\Users\...\numeros.xlsx"
   IMAGE_PATH = r"C:\Users\...\base.jpg"
