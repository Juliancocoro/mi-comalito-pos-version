"""
Módulo de impresión para tickets térmicos ESC/POS
Soporta impresoras USB, de red y Windows
Si no hay impresora, no genera errores
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

    def _generate_ticket_text(self, items, total, ticket_num=None):
        """Genera el texto del ticket"""
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