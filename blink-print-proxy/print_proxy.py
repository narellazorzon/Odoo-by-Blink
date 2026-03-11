"""
Blink Print Proxy - IoT Box virtual para impresion directa desde Odoo POS.

Emula los endpoints de hw_proxy que el POS de Odoo espera, recibe imagenes
JPEG del recibo y las envia a la impresora via Windows GDI.
"""

import base64
import io
import logging
import sys
import traceback

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

from config import PROXY_PORT, PROXY_HOST, PRINTER_NAME

# Windows-only imports
try:
    import win32print
    import win32ui
    import win32con
except ImportError:
    print("ERROR: pywin32 no esta instalado. Ejecutar: pip install pywin32")
    sys.exit(1)

app = Flask(__name__)
CORS(app, origins="*")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("blink-print-proxy")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_printer_name():
    """Retorna el nombre de la impresora configurada o la predeterminada."""
    if PRINTER_NAME:
        return PRINTER_NAME
    return win32print.GetDefaultPrinter()


def print_image(img_data_b64):
    """Recibe imagen en base64, la imprime via Windows GDI."""
    printer_name = get_printer_name()
    log.info("Imprimiendo en: %s", printer_name)

    # Decodificar imagen
    raw = img_data_b64
    # Quitar prefijo data URI si existe
    if "," in raw[:100]:
        raw = raw.split(",", 1)[1]
    img_bytes = base64.b64decode(raw)
    img = Image.open(io.BytesIO(img_bytes))

    # Convertir a RGB si es necesario
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Obtener tamaño de la imagen
    img_w, img_h = img.size

    # Abrir impresora y obtener DC
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    # Obtener area imprimible de la impresora (en pixels de la impresora)
    printer_w = hdc.GetDeviceCaps(win32con.HORZRES)
    printer_h = hdc.GetDeviceCaps(win32con.VERTRES)

    # Escalar imagen para que ocupe el ancho completo de la impresora,
    # manteniendo la proporcion
    scale = printer_w / img_w
    scaled_w = printer_w
    scaled_h = int(img_h * scale)

    hdc.StartDoc("Recibo POS")
    hdc.StartPage()

    # Crear bitmap compatible
    dib = Image.frombytes("RGB", (img_w, img_h), img.tobytes())
    hdc.StretchDIBits(
        (0, 0, scaled_w, scaled_h),    # destino
        (0, 0, img_w, img_h),          # fuente
        dib.tobytes(),                  # data
        [(0, 0, 0, 0)] * 0,           # placeholder - no se usa con BI_RGB
        win32con.DIB_RGB_COLORS,
        win32con.SRCCOPY,
        # BitmapInfoHeader
        img_w, img_h,
    )

    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()
    log.info("Impresion enviada correctamente")


def print_image_gdi(img_data_b64):
    """Imprime imagen via GDI usando approach robusto con SetDIBitsToDevice."""
    printer_name = get_printer_name()
    log.info("Imprimiendo en: %s", printer_name)

    # Decodificar imagen
    raw = img_data_b64
    if "," in raw[:100]:
        raw = raw.split(",", 1)[1]
    img_bytes = base64.b64decode(raw)
    img = Image.open(io.BytesIO(img_bytes))

    if img.mode != "RGB":
        img = img.convert("RGB")

    img_w, img_h = img.size

    # Abrir impresora
    hprinter = win32print.OpenPrinter(printer_name)
    try:
        # Crear DC de la impresora
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)

        printer_w = hdc.GetDeviceCaps(win32con.HORZRES)
        printer_h = hdc.GetDeviceCaps(win32con.VERTRES)

        # Escalar al ancho de la impresora
        scale = printer_w / img_w
        scaled_w = printer_w
        scaled_h = int(img_h * scale)

        hdc.StartDoc("Recibo POS - Blink")
        hdc.StartPage()

        # Usar StretchBlt con un bitmap compatible
        import ctypes
        from ctypes import wintypes

        gdi32 = ctypes.windll.gdi32

        # Crear BITMAPINFO header
        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wintypes.DWORD),
                ("biWidth", ctypes.c_long),
                ("biHeight", ctypes.c_long),
                ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", ctypes.c_long),
                ("biYPelsPerMeter", ctypes.c_long),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD),
            ]

        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = img_w
        bmi.biHeight = -img_h  # Negativo = top-down
        bmi.biPlanes = 1
        bmi.biBitCount = 24
        bmi.biCompression = 0  # BI_RGB

        # Preparar pixel data (BGR para Windows)
        img_bgr = img.copy()
        r, g, b = img_bgr.split()
        img_bgr = Image.merge("RGB", (b, g, r))

        # Alinear filas a 4 bytes (requerimiento BMP)
        row_bytes = img_w * 3
        padding = (4 - (row_bytes % 4)) % 4
        if padding:
            import struct
            raw_data = bytearray()
            pixels = img_bgr.tobytes()
            for y in range(img_h):
                offset = y * row_bytes
                raw_data.extend(pixels[offset:offset + row_bytes])
                raw_data.extend(b'\x00' * padding)
            pixel_data = bytes(raw_data)
        else:
            pixel_data = img_bgr.tobytes()

        hdc_handle = hdc.GetSafeHdc()

        # StretchDIBits para escalar e imprimir
        BI_RGB = 0
        DIB_RGB_COLORS = 0
        SRCCOPY = 0x00CC0020

        result = gdi32.StretchDIBits(
            hdc_handle,
            0, 0, scaled_w, scaled_h,       # destino
            0, 0, img_w, img_h,             # fuente
            pixel_data,                      # bits
            ctypes.byref(bmi),               # bitmap info
            DIB_RGB_COLORS,
            SRCCOPY,
        )

        if result == 0:
            log.error("StretchDIBits fallo")

        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()
        log.info("Impresion enviada correctamente (%dx%d -> %dx%d)",
                 img_w, img_h, scaled_w, scaled_h)
    finally:
        win32print.ClosePrinter(hprinter)


# ---------------------------------------------------------------------------
# JSON-RPC helper
# ---------------------------------------------------------------------------

def jsonrpc_response(result=None):
    """Construye una respuesta JSON-RPC 2.0 valida."""
    req_id = None
    if request.is_json:
        req_id = request.json.get("id")
    return jsonify({
        "jsonrpc": "2.0",
        "id": req_id,
        "result": result,
    })


# ---------------------------------------------------------------------------
# Endpoints - emulacion de IoT Box hw_proxy
# ---------------------------------------------------------------------------

@app.route("/hw_proxy/hello", methods=["GET"])
def hello():
    """Health check - el POS usa fetch() directo (no JSON-RPC)."""
    return "ping"


@app.route("/hw_proxy/handshake", methods=["POST"])
def handshake():
    """Handshake de conexion. Retorna True para indicar exito."""
    return jsonrpc_response(True)


@app.route("/hw_proxy/status_json", methods=["GET", "POST"])
def status_json():
    """Estado de los dispositivos. El POS lo usa para keepalive."""
    printer_name = get_printer_name()
    drivers = {
        "printer": {
            "status": "connected",
            "messages": "",
            "name": printer_name,
        }
    }
    if request.method == "GET":
        return jsonify(drivers)
    return jsonrpc_response(drivers)


@app.route("/hw_proxy/default_printer_action", methods=["POST"])
def default_printer_action():
    """
    Accion principal de impresion.
    El POS envia: { jsonrpc: "2.0", params: { data: { action, receipt } } }
    """
    try:
        params = {}
        if request.is_json:
            body = request.json
            params = body.get("params", {})

        data = params.get("data", {})
        action = data.get("action", "")

        if action == "print_receipt":
            receipt_b64 = data.get("receipt", "")
            if not receipt_b64:
                log.warning("print_receipt sin datos de imagen")
                return jsonrpc_response(False)
            print_image_gdi(receipt_b64)
            return jsonrpc_response(True)

        elif action == "cashbox":
            log.info("Cashbox solicitado (no implementado)")
            return jsonrpc_response(True)

        else:
            log.warning("Accion desconocida: %s", action)
            return jsonrpc_response(False)

    except Exception as e:
        log.error("Error en impresion: %s\n%s", e, traceback.format_exc())
        return jsonrpc_response(False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    printer = get_printer_name()
    log.info("=" * 60)
    log.info("Blink Print Proxy")
    log.info("Impresora: %s", printer)
    log.info("Escuchando en http://%s:%s", PROXY_HOST, PROXY_PORT)
    log.info("=" * 60)
    app.run(host=PROXY_HOST, port=PROXY_PORT, debug=False)
