"""
Módulo de impresión para tickets térmicos ESC/POS
Soporta impresoras USB, de red y Windows
Incluye soporte para imprimir imágenes/logos
"""

import os
import sys
from datetime import datetime


def resource_path(relative_path):
    """Obtiene la ruta correcta para recursos empaquetados"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class PrinterManager:
    """Administra la conexión y configuración de impresoras térmicas"""

    def __init__(self):
        self.printer = None
        self.printer_type = None
        self.printer_name = None
        self.config = self.load_config()

    def load_config(self):
        """Carga configuración de impresora desde archivo"""
        try:
            import json
            from pathlib import Path

            config_file = Path("printer_config.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_config(self, config):
        """Guarda configuración de impresora"""
        try:
            import json

            with open("printer_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            self.config = config
        except Exception as e:
            print(f"Error guardando config: {e}")

    def detect_usb_printers(self):
        """Detecta impresoras USB conectadas"""
        printers = []

        try:
            import usb.core
            import usb.util

            devices = usb.core.find(find_all=True)
            if devices is None:
                return printers

            for device in devices:
                try:
                    vendor_id = device.idVendor
                    product_id = device.idProduct

                    try:
                        manufacturer = usb.util.get_string(device, device.iManufacturer) or "Desconocido"
                    except:
                        manufacturer = "Desconocido"

                    try:
                        product = usb.util.get_string(device, device.iProduct) or "Dispositivo USB"
                    except:
                        product = "Dispositivo USB"

                    is_printer = False

                    if device.bDeviceClass == 7:
                        is_printer = True

                    try:
                        for cfg in device:
                            for intf in cfg:
                                if intf.bInterfaceClass == 7:
                                    is_printer = True
                                    break
                    except:
                        pass

                    known_printer_vendors = [
                        0x04b8, 0x0519, 0x0dd4, 0x0fe6, 0x1504,
                        0x0416, 0x0483, 0x1fc9, 0x0525, 0x28e9,
                        0x6868, 0x0456, 0x067b, 0x1a86, 0x10c4
                    ]

                    if vendor_id in known_printer_vendors:
                        is_printer = True

                    product_lower = product.lower() if product else ""
                    if any(kw in product_lower for kw in ['printer', 'pos', 'receipt', 'thermal', 'escpos']):
                        is_printer = True

                    if is_printer:
                        printers.append({
                            "type": "usb",
                            "vendor_id": vendor_id,
                            "product_id": product_id,
                            "manufacturer": manufacturer,
                            "product": product,
                            "name": f"{manufacturer} - {product}",
                            "id": f"0x{vendor_id:04x}:0x{product_id:04x}"
                        })

                except:
                    continue

        except ImportError:
            pass
        except:
            pass

        return printers

    def detect_windows_printers(self):
        """Detecta impresoras instaladas en Windows"""
        printers = []

        if sys.platform != 'win32':
            return printers

        try:
            import win32print

            printer_list = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            )

            for printer in printer_list:
                printers.append({
                    "type": "windows",
                    "name": printer[2],
                    "id": printer[2]
                })

        except ImportError:
            pass
        except:
            pass

        return printers

    def get_all_printers(self):
        """Obtiene todas las impresoras disponibles"""
        all_printers = []

        usb_printers = self.detect_usb_printers()
        all_printers.extend(usb_printers)

        if sys.platform == 'win32':
            win_printers = self.detect_windows_printers()
            all_printers.extend(win_printers)

        return all_printers

    def connect_usb(self, vendor_id, product_id):
        """Conecta a una impresora USB"""
        try:
            from escpos.printer import Usb
            self.printer = Usb(vendor_id, product_id, 0)
            self.printer_type = "usb"
            return True
        except:
            return False

    def connect_network(self, ip, port=9100):
        """Conecta a una impresora de red"""
        try:
            from escpos.printer import Network
            self.printer = Network(ip, port)
            self.printer_type = "network"
            return True
        except:
            return False

    def connect_windows(self, printer_name):
        """Conecta a una impresora de Windows usando método directo"""
        try:
            self.printer_name = printer_name
            self.printer_type = "windows"
            self.printer = "windows_raw"
            return True
        except:
            return False

    def connect_from_config(self):
        """Conecta usando la configuración guardada"""
        if not self.config:
            return False

        printer_type = self.config.get("type")

        try:
            if printer_type == "usb":
                return self.connect_usb(
                    self.config.get("vendor_id"),
                    self.config.get("product_id")
                )
            elif printer_type == "network":
                return self.connect_network(
                    self.config.get("ip"),
                    self.config.get("port", 9100)
                )
            elif printer_type == "windows":
                return self.connect_windows(
                    self.config.get("name")
                )
        except:
            pass

        return False

    def is_connected(self):
        """Verifica si hay una impresora conectada"""
        return self.printer is not None

    def _image_to_escpos_bits(self, image_path, max_width=384):
        """
        Convierte una imagen a comandos ESC/POS de bits
        
        La impresora POS58 tiene 384 puntos de ancho (58mm)
        Cada byte representa 8 puntos horizontales
        """
        try:
            from PIL import Image
            
            # Cargar imagen
            img = Image.open(image_path)
            
            # Convertir a escala de grises
            img = img.convert('L')
            
            # Calcular nuevo tamaño manteniendo proporción
            # Máximo 384 pixeles de ancho para impresora de 58mm
            width = min(img.width, max_width)
            ratio = width / img.width
            height = int(img.height * ratio)
            
            # Redimensionar
            img = img.resize((width, height), Image.LANCZOS)
            
            # Convertir a blanco y negro puro (1 bit)
            # Umbral: pixeles < 128 = negro (1), >= 128 = blanco (0)
            img = img.point(lambda x: 0 if x < 128 else 255, '1')
            
            # Asegurar que el ancho sea múltiplo de 8
            width_bytes = (width + 7) // 8
            new_width = width_bytes * 8
            
            if new_width != width:
                # Crear nueva imagen con ancho ajustado
                new_img = Image.new('1', (new_width, height), 1)  # 1 = blanco
                new_img.paste(img, (0, 0))
                img = new_img
                width = new_width
            
            # Generar datos de imagen en formato ESC/POS
            # Usamos el comando GS v 0 (raster bit image)
            
            width_bytes = width // 8
            height_pixels = height
            
            # Comando: GS v 0 m xL xH yL yH [datos]
            # m = 0 (modo normal)
            # xL xH = ancho en bytes (little endian)
            # yL yH = alto en pixeles (little endian)
            
            cmd = bytearray()
            
            # Inicializar impresora
            cmd.extend(b'\x1b\x40')  # ESC @ - Initialize
            
            # Centrar imagen
            cmd.extend(b'\x1b\x61\x01')  # ESC a 1 - Center
            
            # Comando GS v 0
            cmd.extend(b'\x1d\x76\x30\x00')  # GS v 0 m (m=0)
            
            # Ancho en bytes (little endian)
            cmd.append(width_bytes & 0xFF)
            cmd.append((width_bytes >> 8) & 0xFF)
            
            # Alto en pixeles (little endian)
            cmd.append(height_pixels & 0xFF)
            cmd.append((height_pixels >> 8) & 0xFF)
            
            # Datos de imagen
            # En modo '1' de PIL: 0 = negro, 255 = blanco
            # En ESC/POS: 1 = punto negro, 0 = punto blanco
            # Entonces invertimos
            
            pixels = list(img.getdata())
            
            for y in range(height):
                for x_byte in range(width_bytes):
                    byte_val = 0
                    for bit in range(8):
                        x = x_byte * 8 + bit
                        pixel_index = y * width + x
                        
                        if pixel_index < len(pixels):
                            # PIL '1' mode: 0 = negro, 255 = blanco
                            # ESC/POS: 1 = imprimir (negro), 0 = no imprimir (blanco)
                            if pixels[pixel_index] == 0:  # Negro en PIL
                                byte_val |= (1 << (7 - bit))  # Bit 1 = imprimir
                    
                    cmd.append(byte_val)
            
            # Salto de línea después de imagen
            cmd.extend(b'\n')
            
            return bytes(cmd)
            
        except ImportError:
            print("PIL no está instalado")
            return None
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return None

    def _print_windows_raw(self, data):
        """Imprime datos raw directamente a impresora Windows"""
        try:
            import win32print
            
            # Si es string, convertir a bytes
            if isinstance(data, str):
                data = data.encode('cp437', errors='replace')
            
            # Método 1: Intentar con RAW
            try:
                hprinter = win32print.OpenPrinter(self.printer_name)
                try:
                    win32print.StartDocPrinter(hprinter, 1, ("Ticket", None, "RAW"))
                    try:
                        win32print.StartPagePrinter(hprinter)
                        win32print.WritePrinter(hprinter, data)
                        win32print.EndPagePrinter(hprinter)
                    finally:
                        win32print.EndDocPrinter(hprinter)
                finally:
                    win32print.ClosePrinter(hprinter)
                return True
            except Exception as e1:
                # Método 2: Intentar con TEXT
                try:
                    hprinter = win32print.OpenPrinter(self.printer_name)
                    try:
                        win32print.StartDocPrinter(hprinter, 1, ("Ticket", None, "TEXT"))
                        try:
                            win32print.StartPagePrinter(hprinter)
                            win32print.WritePrinter(hprinter, data)
                            win32print.EndPagePrinter(hprinter)
                        finally:
                            win32print.EndDocPrinter(hprinter)
                    finally:
                        win32print.ClosePrinter(hprinter)
                    return True
                except Exception as e2:
                    raise Exception(f"RAW: {e1}, TEXT: {e2}")
                
        except Exception as e:
            print(f"Error imprimiendo: {e}")
            raise e

    def _generate_ticket_with_logo(self, items, total, ticket_num=None):
        """Genera ticket completo con logo en formato ESC/POS"""
        now = datetime.now()
        
        data = bytearray()
        
        # Inicializar impresora
        data.extend(b'\x1b\x40')  # ESC @ - Initialize
        
        # Intentar agregar logo
        logo_path = resource_path("loguito.jpeg")
        if os.path.exists(logo_path):
            logo_data = self._image_to_escpos_bits(logo_path, max_width=300)
            if logo_data:
                data.extend(logo_data)
        else:
            # Si no hay logo, usar texto
            data.extend(b'\x1b\x61\x01')  # Centrar
            data.extend(b'\x1b\x21\x30')  # Doble alto y ancho
            data.extend("MI COMALITO\n".encode('cp437', errors='replace'))
            data.extend(b'\x1b\x21\x00')  # Normal
            data.extend("Gorditas y Algo Mas..\n".encode('cp437', errors='replace'))
        
        # Centrar texto
        data.extend(b'\x1b\x61\x01')
        
        data.extend(("=" * 32 + "\n").encode('cp437'))
        data.extend(f"Fecha: {now.strftime('%d/%m/%Y')}\n".encode('cp437'))
        data.extend(f"Hora:  {now.strftime('%H:%M:%S')}\n".encode('cp437'))
        
        if ticket_num:
            data.extend(f"Ticket: #{ticket_num}\n".encode('cp437'))
        
        data.extend(("-" * 32 + "\n").encode('cp437'))
        
        # Alinear a la izquierda para productos
        data.extend(b'\x1b\x61\x00')
        
        for item in items:
            qty = item.get("qty", 1)
            categoria = item.get("categoria", "")
            tipo = item.get("tipo", "")
            subtotal = item.get("subtotal", 0)
            
            producto = f"{categoria}"
            if tipo:
                producto += f" - {tipo}"
            
            data.extend(f"{qty} x {producto}\n".encode('cp437', errors='replace'))
            # Alinear derecha para precio
            data.extend(b'\x1b\x61\x02')
            data.extend(f"${subtotal:.2f}\n".encode('cp437'))
            data.extend(b'\x1b\x61\x00')
        
        data.extend(("-" * 32 + "\n").encode('cp437'))
        
        # Total en grande y a la derecha
        data.extend(b'\x1b\x61\x02')
        data.extend(b'\x1b\x21\x30')  # Doble
        data.extend(f"TOTAL: ${total:.2f}\n".encode('cp437'))
        data.extend(b'\x1b\x21\x00')  # Normal
        
        # Centrar para despedida
        data.extend(b'\x1b\x61\x01')
        data.extend(("=" * 32 + "\n").encode('cp437'))
        data.extend("GRACIAS POR SU COMPRA!\n".encode('cp437'))
        data.extend(("=" * 32 + "\n").encode('cp437'))
        
        # Espacios y corte
        data.extend(b'\n\n\n')
        data.extend(b'\x1d\x56\x00')  # Cortar papel
        
        return bytes(data)

    def _generate_ticket_text(self, items, total, ticket_num=None):
        """Genera el texto del ticket (sin logo, solo texto)"""
        now = datetime.now()
        
        lines = []
        lines.append("=" * 32)
        lines.append("       MI COMALITO")
        lines.append("   Gorditas y Algo Mas..")
        lines.append("=" * 32)
        lines.append(f"Fecha: {now.strftime('%d/%m/%Y')}")
        lines.append(f"Hora:  {now.strftime('%H:%M:%S')}")
        
        if ticket_num:
            lines.append(f"Ticket: #{ticket_num}")
        
        lines.append("-" * 32)
        
        for item in items:
            qty = item.get("qty", 1)
            categoria = item.get("categoria", "")
            tipo = item.get("tipo", "")
            subtotal = item.get("subtotal", 0)
            
            producto = f"{categoria}"
            if tipo:
                producto += f" - {tipo}"
            
            lines.append(f"{qty} x {producto}")
            lines.append(f"              ${subtotal:.2f}")
        
        lines.append("-" * 32)
        lines.append(f"TOTAL: ${total:.2f}")
        lines.append("=" * 32)
        lines.append("  GRACIAS POR SU COMPRA!")
        lines.append("=" * 32)
        lines.append("")
        lines.append("")
        lines.append("")
        lines.append("\x1d\x56\x00")  # Comando ESC/POS para cortar papel
        
        return "\n".join(lines)

    def _generate_test_text(self):
        """Genera texto de prueba"""
        now = datetime.now()
        
        lines = []
        lines.append("=" * 32)
        lines.append("        PRUEBA")
        lines.append("=" * 32)
        lines.append(f"Fecha: {now.strftime('%d/%m/%Y %H:%M')}")
        lines.append("")
        lines.append("Si puedes leer esto,")
        lines.append("la impresora funciona")
        lines.append("correctamente!")
        lines.append("")
        lines.append("=" * 32)
        lines.append("")
        lines.append("")
        lines.append("")
        lines.append("\x1d\x56\x00")  # Cortar papel
        
        return "\n".join(lines)

    def _generate_corte_text(self, total_vendido, tickets_pagados):
        """Genera texto del corte"""
        now = datetime.now()
        
        lines = []
        lines.append("=" * 32)
        lines.append("     CORTE DEL DIA")
        lines.append("      MI COMALITO")
        lines.append("=" * 32)
        lines.append(f"Fecha: {now.strftime('%d/%m/%Y')}")
        lines.append(f"Hora:  {now.strftime('%H:%M:%S')}")
        lines.append("-" * 32)
        lines.append(f"Tickets cobrados: {tickets_pagados}")
        lines.append(f"TOTAL: ${total_vendido:.2f}")
        lines.append("-" * 32)
        lines.append("     FIN DEL CORTE")
        lines.append("=" * 32)
        lines.append("")
        lines.append("")
        lines.append("")
        lines.append("\x1d\x56\x00")  # Cortar papel
        
        return "\n".join(lines)

    def print_ticket(self, items, total, ticket_num=None):
        """Imprime un ticket de venta"""
        if not self.printer:
            return False

        try:
            if self.printer_type == "windows":
                # Intentar con logo primero
                try:
                    data = self._generate_ticket_with_logo(items, total, ticket_num)
                    return self._print_windows_raw(data)
                except Exception as e:
                    print(f"Error con logo, usando texto: {e}")
                    # Si falla, usar solo texto
                    text = self._generate_ticket_text(items, total, ticket_num)
                    return self._print_windows_raw(text)
            else:
                # Método ESC/POS para USB y Red
                p = self.printer
                now = datetime.now()

                p.set(align='center')
                p.text("=" * 32 + "\n")
                p.set(align='center', text_type='B', width=2, height=2)
                p.text("MI COMALITO\n")
                p.set(align='center', text_type='normal', width=1, height=1)
                p.text("Gorditas y Algo Mas..\n")
                p.text("=" * 32 + "\n")

                p.text(f"Fecha: {now.strftime('%d/%m/%Y')}\n")
                p.text(f"Hora:  {now.strftime('%H:%M:%S')}\n")

                if ticket_num:
                    p.text(f"Ticket: #{ticket_num}\n")

                p.text("-" * 32 + "\n")
                p.set(align='left')

                for item in items:
                    qty = item.get("qty", 1)
                    categoria = item.get("categoria", "")
                    tipo = item.get("tipo", "")
                    subtotal = item.get("subtotal", 0)

                    producto = f"{categoria}"
                    if tipo:
                        producto += f" - {tipo}"

                    p.text(f"{qty} x {producto}\n")
                    p.set(align='right')
                    p.text(f"${subtotal:.2f}\n")
                    p.set(align='left')

                p.text("-" * 32 + "\n")
                p.set(align='right', text_type='B', width=2, height=2)
                p.text(f"TOTAL: ${total:.2f}\n")

                p.set(align='center', text_type='normal', width=1, height=1)
                p.text("=" * 32 + "\n")
                p.text("GRACIAS POR SU COMPRA!\n")
                p.text("=" * 32 + "\n")
                p.text("\n\n\n")
                p.cut()

                return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def print_test(self):
        """Imprime una página de prueba"""
        if not self.printer:
            return False

        try:
            if self.printer_type == "windows":
                text = self._generate_test_text()
                return self._print_windows_raw(text)
            else:
                p = self.printer
                now = datetime.now()

                p.set(align='center')
                p.text("=" * 32 + "\n")
                p.set(align='center', text_type='B', width=2, height=2)
                p.text("PRUEBA\n")
                p.set(align='center', text_type='normal', width=1, height=1)
                p.text("=" * 32 + "\n")
                p.text(f"Fecha: {now.strftime('%d/%m/%Y %H:%M')}\n")
                p.text("\n")
                p.text("Si puedes leer esto,\n")
                p.text("la impresora funciona\n")
                p.text("correctamente!\n")
                p.text("\n")
                p.text("=" * 32 + "\n")
                p.text("\n\n\n")
                p.cut()

                return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def print_corte(self, total_vendido, tickets_pagados):
        """Imprime el corte del día"""
        if not self.printer:
            return False

        try:
            if self.printer_type == "windows":
                text = self._generate_corte_text(total_vendido, tickets_pagados)
                return self._print_windows_raw(text)
            else:
                p = self.printer
                now = datetime.now()

                p.set(align='center')
                p.text("=" * 32 + "\n")
                p.set(align='center', text_type='B', width=2, height=2)
                p.text("CORTE DEL DIA\n")
                p.set(align='center', text_type='normal', width=1, height=1)
                p.text("MI COMALITO\n")
                p.text("=" * 32 + "\n")

                p.text(f"Fecha: {now.strftime('%d/%m/%Y')}\n")
                p.text(f"Hora:  {now.strftime('%H:%M:%S')}\n")
                p.text("-" * 32 + "\n")

                p.set(align='left')
                p.text(f"Tickets cobrados: {tickets_pagados}\n")

                p.set(align='right', text_type='B', width=2, height=1)
                p.text(f"TOTAL: ${total_vendido:.2f}\n")

                p.set(align='center', text_type='normal', width=1, height=1)
                p.text("-" * 32 + "\n")
                p.text("FIN DEL CORTE\n")
                p.text("=" * 32 + "\n")
                p.text("\n\n\n")
                p.cut()

                return True

        except Exception as e:
            print(f"Error: {e}")
            return False