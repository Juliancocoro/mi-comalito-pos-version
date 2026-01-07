"""
Diálogo de configuración de impresora térmica
No genera errores si faltan dependencias
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QFrame,
    QMessageBox, QTabWidget, QWidget, QGroupBox,
    QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class DetectPrintersThread(QThread):
    """Hilo para detectar impresoras sin bloquear la UI"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, printer_manager):
        super().__init__()
        self.printer_manager = printer_manager

    def run(self):
        try:
            printers = self.printer_manager.get_all_printers()
            self.finished.emit(printers)
        except Exception as e:
            self.error.emit(str(e))


class PrinterConfigDialog(QDialog):
    """Diálogo para configurar la impresora térmica"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.printer_manager = None
        self.detected_printers = []

        # Intentar cargar el módulo de impresora
        try:
            from impresora import PrinterManager
            self.printer_manager = PrinterManager()
        except ImportError:
            pass

        self.setWindowTitle("Configurar Impresora")
        self.setFixedSize(550, 500)

        self.setup_ui()
        self.load_current_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("Configuración de Impresora Térmica")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Verificar si hay módulo disponible
        if not self.printer_manager:
            error_label = QLabel(
                "⚠️ Módulo de impresora no disponible.\n\n"
                "Instala las dependencias:\n"
                "pip install python-escpos pyserial"
            )
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("font-size: 14px; color: #d93025; padding: 40px;")
            layout.addWidget(error_label)
            return

        # Tabs para diferentes tipos de conexión
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #1a73e8;
                color: white;
                border-radius: 5px;
            }
        """)

        # Tab Windows (primero porque es el más fácil)
        self.tab_windows = self.create_windows_tab()
        self.tabs.addTab(self.tab_windows, "Windows")

        # Tab USB
        self.tab_usb = self.create_usb_tab()
        self.tabs.addTab(self.tab_usb, "USB")

        # Tab Red
        self.tab_network = self.create_network_tab()
        self.tabs.addTab(self.tab_network, "Red")

        layout.addWidget(self.tabs)

        # Botones de acción
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_test = QPushButton("Probar Impresión")
        self.btn_test.setFixedHeight(45)
        self.btn_test.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                color: white;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d8a47;
            }
        """)
        self.btn_test.clicked.connect(self.test_print)

        self.btn_save = QPushButton("Guardar Configuración")
        self.btn_save.setFixedHeight(45)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1558b0;
            }
        """)
        self.btn_save.clicked.connect(self.save_config)

        btn_layout.addWidget(self.btn_test)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

        # Estado
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(self.status_label)

    def create_windows_tab(self):
        """Crea el tab para impresoras de Windows"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        info = QLabel("Selecciona una impresora instalada en Windows:")
        info.setStyleSheet("font-size: 13px; color: #333;")
        layout.addWidget(info)

        # Botón detectar
        self.btn_detect_win = QPushButton("Detectar Impresoras")
        self.btn_detect_win.setFixedHeight(40)
        self.btn_detect_win.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        self.btn_detect_win.clicked.connect(self.detect_windows_printers)
        layout.addWidget(self.btn_detect_win)

        # Lista de impresoras
        self.windows_printer_list = QListWidget()
        self.windows_printer_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background: #1a73e8;
                color: white;
            }
        """)
        layout.addWidget(self.windows_printer_list)

        # Nota
        note = QLabel(
            "💡 La impresora debe estar instalada en Windows.\n"
            "Conéctala y usa el driver del fabricante."
        )
        note.setAlignment(Qt.AlignCenter)
        note.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(note)

        return widget

    def create_usb_tab(self):
        """Crea el tab de configuración USB"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # Botón detectar
        self.btn_detect = QPushButton("Detectar Impresoras USB")
        self.btn_detect.setFixedHeight(40)
        self.btn_detect.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        self.btn_detect.clicked.connect(self.detect_printers)
        layout.addWidget(self.btn_detect)

        # Lista de impresoras detectadas
        self.printer_list = QListWidget()
        self.printer_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background: #1a73e8;
                color: white;
            }
        """)
        layout.addWidget(self.printer_list)

        # Configuración manual
        manual_group = QGroupBox("Configuración Manual (Vendor ID : Product ID)")
        manual_layout = QHBoxLayout(manual_group)

        self.vendor_input = QLineEdit()
        self.vendor_input.setPlaceholderText("Ej: 0x04b8")
        self.vendor_input.setFixedHeight(35)

        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("Ej: 0x0202")
        self.product_input.setFixedHeight(35)

        manual_layout.addWidget(QLabel("Vendor:"))
        manual_layout.addWidget(self.vendor_input)
        manual_layout.addWidget(QLabel("Product:"))
        manual_layout.addWidget(self.product_input)

        layout.addWidget(manual_group)

        return widget

    def create_network_tab(self):
        """Crea el tab de configuración de red"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # IP
        ip_group = QGroupBox("Dirección IP de la Impresora")
        ip_layout = QHBoxLayout(ip_group)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Ej: 192.168.1.100")
        self.ip_input.setFixedHeight(40)
        self.ip_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)

        ip_layout.addWidget(self.ip_input)
        layout.addWidget(ip_group)

        # Puerto
        port_group = QGroupBox("Puerto (por defecto: 9100)")
        port_layout = QHBoxLayout(port_group)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("9100")
        self.port_input.setText("9100")
        self.port_input.setFixedHeight(40)
        self.port_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)

        port_layout.addWidget(self.port_input)
        layout.addWidget(port_group)

        layout.addStretch()

        note = QLabel(
            "💡 La mayoría de impresoras térmicas de red\n"
            "usan el puerto 9100 por defecto."
        )
        note.setAlignment(Qt.AlignCenter)
        note.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(note)

        return widget

    def detect_printers(self):
        """Detecta impresoras USB"""
        if not self.printer_manager:
            return

        self.btn_detect.setEnabled(False)
        self.btn_detect.setText("Detectando...")
        self.printer_list.clear()

        self.detect_thread = DetectPrintersThread(self.printer_manager)
        self.detect_thread.finished.connect(self.on_printers_detected)
        self.detect_thread.error.connect(self.on_detection_error)
        self.detect_thread.start()

    def on_printers_detected(self, printers):
        """Callback cuando se detectan impresoras"""
        self.btn_detect.setEnabled(True)
        self.btn_detect.setText("Detectar Impresoras USB")

        self.detected_printers = [p for p in printers if p["type"] == "usb"]

        if not self.detected_printers:
            self.printer_list.addItem("No se detectaron impresoras USB")
            self.status_label.setText("Conecta tu impresora y vuelve a intentar")
            return

        for printer in self.detected_printers:
            item = QListWidgetItem(f"{printer['name']}\nID: {printer['id']}")
            item.setData(Qt.UserRole, printer)
            self.printer_list.addItem(item)

        self.status_label.setText(f"Se detectaron {len(self.detected_printers)} impresora(s)")

    def on_detection_error(self, error):
        """Callback en caso de error"""
        self.btn_detect.setEnabled(True)
        self.btn_detect.setText("Detectar Impresoras USB")
        self.status_label.setText(f"Error: {error}")

    def detect_windows_printers(self):
        """Detecta impresoras de Windows"""
        if not self.printer_manager:
            return

        self.windows_printer_list.clear()

        printers = self.printer_manager.detect_windows_printers()

        if not printers:
            self.windows_printer_list.addItem("No se detectaron impresoras")
            self.status_label.setText("Instala una impresora en Windows primero")
            return

        for printer in printers:
            item = QListWidgetItem(f"{printer['name']}")
            item.setData(Qt.UserRole, printer)
            self.windows_printer_list.addItem(item)

        self.status_label.setText(f"Se detectaron {len(printers)} impresora(s)")

    def load_current_config(self):
        """Carga la configuración actual"""
        if not self.printer_manager:
            return

        config = self.printer_manager.config

        if not config:
            return

        printer_type = config.get("type")

        if printer_type == "usb":
            self.tabs.setCurrentIndex(1)
            self.vendor_input.setText(hex(config.get("vendor_id", 0)))
            self.product_input.setText(hex(config.get("product_id", 0)))

        elif printer_type == "network":
            self.tabs.setCurrentIndex(2)
            self.ip_input.setText(config.get("ip", ""))
            self.port_input.setText(str(config.get("port", 9100)))

        elif printer_type == "windows":
            self.tabs.setCurrentIndex(0)

    def get_current_config(self):
        """Obtiene la configuración actual del diálogo"""
        if not self.printer_manager:
            return None

        current_tab = self.tabs.currentIndex()

        if current_tab == 0:  # Windows
            selected = self.windows_printer_list.currentItem()
            if not selected or not selected.data(Qt.UserRole):
                return None

            printer = selected.data(Qt.UserRole)
            return {
                "type": "windows",
                "name": printer["name"]
            }

        elif current_tab == 1:  # USB
            selected = self.printer_list.currentItem()
            if selected and selected.data(Qt.UserRole):
                printer = selected.data(Qt.UserRole)
                return {
                    "type": "usb",
                    "vendor_id": printer["vendor_id"],
                    "product_id": printer["product_id"],
                    "name": printer["name"]
                }
            else:
                vendor = self.vendor_input.text().strip()
                product = self.product_input.text().strip()

                if not vendor or not product:
                    return None

                try:
                    return {
                        "type": "usb",
                        "vendor_id": int(vendor, 16),
                        "product_id": int(product, 16),
                        "name": f"Manual ({vendor}:{product})"
                    }
                except:
                    return None

        elif current_tab == 2:  # Red
            ip = self.ip_input.text().strip()
            port = self.port_input.text().strip()

            if not ip:
                return None

            return {
                "type": "network",
                "ip": ip,
                "port": int(port) if port else 9100,
                "name": f"Red ({ip})"
            }

        return None

    def test_print(self):
        """Realiza una impresión de prueba"""
        if not self.printer_manager:
            QMessageBox.warning(self, "Error", "Módulo de impresora no disponible")
            return

        config = self.get_current_config()

        if not config:
            QMessageBox.warning(
                self,
                "Configuración",
                "Por favor selecciona o configura una impresora"
            )
            return

        try:
            self.printer_manager.save_config(config)

            if not self.printer_manager.connect_from_config():
                raise Exception("No se pudo conectar a la impresora")

            if self.printer_manager.print_test():
                QMessageBox.information(
                    self,
                    "Prueba",
                    "Impresión de prueba enviada correctamente"
                )
            else:
                raise Exception("Error al enviar impresión")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al imprimir:\n{str(e)}\n\n"
                "Verifica que la impresora esté conectada y encendida."
            )

    def save_config(self):
        """Guarda la configuración"""
        if not self.printer_manager:
            QMessageBox.warning(self, "Error", "Módulo de impresora no disponible")
            return

        config = self.get_current_config()

        if not config:
            QMessageBox.warning(
                self,
                "Configuración",
                "Por favor selecciona o configura una impresora"
            )
            return

        try:
            self.printer_manager.save_config(config)
            QMessageBox.information(
                self,
                "Guardado",
                f"Configuración guardada:\n{config['name']}"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar:\n{str(e)}"
            )