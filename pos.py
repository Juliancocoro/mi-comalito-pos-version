import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from categorias.bebidas import BebidasDialog
from ticket import TicketWidget
from registros_semanales import RegistrosSemanalesDialog


def resource_path(relative_path):
    """Obtiene la ruta correcta para recursos empaquetados"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class ImageFrame(QFrame):
    def __init__(self, image_path):
        super().__init__()
        self.pixmap = QPixmap(image_path)
        self.bg_label = QLabel(self)
        self.bg_label.lower()
        self.bg_label.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.pixmap.isNull():
            self.bg_label.setGeometry(0, 0, self.width(), self.height())
            self.bg_label.setPixmap(
                self.pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )


class POSWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Punto de Venta - Mi Comalito")
        self.showMaximized()

        # ======================================================
        # BARRA SUPERIOR
        # ======================================================
        top_bar = QHBoxLayout()
        top_bar.setSpacing(15)

        # Botón de configurar impresora
        self.btn_printer = QPushButton("Impresora")
        self.btn_printer.setFixedHeight(45)
        self.btn_printer.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        self.btn_printer.clicked.connect(self.open_printer_config)

        # 🔒 BOTÓN EDITAR MENÚ (OCULTO)
        self.btn_editar_menu = QPushButton("⚙️ Editar Menú")
        self.btn_editar_menu.setFixedHeight(45)
        self.btn_editar_menu.setStyleSheet("""
            QPushButton {
                background-color: #9c27b0;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #7b1fa2;
            }
        """)
        self.btn_editar_menu.hide()
        self.btn_editar_menu.clicked.connect(self.open_editar_menu)

        # Botón registros semanales
        self.btn_registros = QPushButton("Registros Semanales")
        self.btn_registros.setFixedHeight(45)
        self.btn_registros.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #1b5e20;
            }
        """)

        top_bar.addWidget(self.btn_printer)
        top_bar.addWidget(self.btn_editar_menu)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_registros)

        # =========================
        # PANEL IZQUIERDO
        # =========================
        products_frame = ImageFrame(resource_path("comidas.jpg"))
        products_frame.setStyleSheet("""
            QFrame {
                border: 2px solid black;
                border-radius: 14px;
            }
        """)
        products_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        products_layout = QVBoxLayout(products_frame)
        products_layout.setContentsMargins(25, 25, 25, 25)
        products_layout.setSpacing(25)

        grid = QGridLayout()
        grid.setSpacing(25)

        btn_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.93);
                border: 2px solid black;
                border-radius: 22px;
                font-size: 18px;
                padding: 25px;
            }
            QPushButton:hover {
                background-color: rgba(230, 230, 230, 0.96);
            }
        """

        self.buttons = {}

        categorias = [
            "Gorditas", "Bocoles", "Migadas",
            "Taco de maiz", "Taco de Harina", "Quesadillas",
            "Big Quesadilla", "Café", "Bebidas", "Postres"
        ]

        row = col = 0
        for nombre in categorias:
            btn = QPushButton(nombre)
            btn.setStyleSheet(btn_style)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            grid.addWidget(btn, row, col)
            self.buttons[nombre] = btn

            col += 1
            if col == 3:
                col = 0
                row += 1

        products_layout.addLayout(grid)
        products_layout.addStretch()

        # =========================
        # TICKET
        # =========================
        ticket_frame = QFrame()
        ticket_frame.setFixedWidth(340)
        ticket_frame.setStyleSheet("""
            QFrame {
                border: 2px solid black;
                border-radius: 14px;
                background: white;
            }
        """)

        ticket_layout = QVBoxLayout(ticket_frame)
        ticket_layout.setContentsMargins(0, 0, 0, 0)

        self.ticket = TicketWidget()
        self.ticket.edit_requested.connect(self.edit_product)
        ticket_layout.addWidget(self.ticket)

        # =========================
        # BOTONES INFERIORES
        # =========================
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(40)

        btn_bottom_style = """
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border-radius: 12px;
                padding: 18px 35px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1558b0;
            }
        """

        self.btn_cancel = QPushButton("Cancelación")
        self.btn_admin = QPushButton("Corte (Admin)")
        self.btn_pay = QPushButton("Pagar / Cobrar")

        for btn in (self.btn_cancel, self.btn_admin, self.btn_pay):
            btn.setStyleSheet(btn_bottom_style)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        bottom_layout.addWidget(self.btn_cancel)
        bottom_layout.addWidget(self.btn_admin)
        bottom_layout.addWidget(self.btn_pay)

        # =========================
        # LAYOUT GENERAL
        # =========================
        left_layout = QVBoxLayout()
        left_layout.addLayout(top_bar)
        left_layout.addWidget(products_frame)
        left_layout.addLayout(bottom_layout)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        main_layout.addLayout(left_layout, 3)
        main_layout.addWidget(ticket_frame, 1)

        self.setLayout(main_layout)

        # =========================
        # CONEXIONES
        # =========================
        self.buttons["Gorditas"].clicked.connect(self.open_gorditas)
        self.buttons["Bocoles"].clicked.connect(self.open_bocoles)
        self.buttons["Migadas"].clicked.connect(self.open_migadas)
        self.buttons["Taco de maiz"].clicked.connect(self.open_tacos_de_maiz)
        self.buttons["Bebidas"].clicked.connect(self.open_bebidas)
        self.buttons["Taco de Harina"].clicked.connect(self.open_tacos)
        self.buttons["Quesadillas"].clicked.connect(self.open_quesadillas)
        self.buttons["Café"].clicked.connect(self.add_cafe)
        self.buttons["Big Quesadilla"].clicked.connect(self.open_bigquesadillas)
        self.buttons["Postres"].clicked.connect(self.open_postres)
        self.btn_pay.clicked.connect(self.open_payment)
        self.btn_admin.clicked.connect(self.open_corte)
        self.btn_registros.clicked.connect(self.open_registros)
        self.btn_cancel.clicked.connect(self.cancel_ticket)

        # =========================
        # CLAVE ADMIN 🔒
        # =========================
        self._admin_buffer = ""
        self._admin_password = "goku"

    # =========================
    # TECLADO SECRETO 🔒
    # =========================
    def keyPressEvent(self, event):
        if event.text().isprintable():
            self._admin_buffer += event.text()
            self._admin_buffer = self._admin_buffer[-10:]

            if self._admin_password in self._admin_buffer:
                self.btn_editar_menu.show()
                self._admin_buffer = ""

        super().keyPressEvent(event)

    # =========================
    # ABRIR EDITAR MENÚ
    # =========================
    def open_editar_menu(self):
        from editar_menu import EditarMenuDialog
        EditarMenuDialog(self).exec_()
        self.btn_editar_menu.hide()

    # =========================
    # MÉTODOS DE TICKET
    # =========================
    def add_product(self, data):
        self.ticket.add_item(data)

    def cancel_ticket(self):
        if not self.ticket.items_data:
            QMessageBox.information(self, "Info", "El ticket ya está vacío")
            return

        reply = QMessageBox.question(
            self,
            "Cancelar Ticket",
            "¿Estás seguro de cancelar todo el ticket?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.ticket.clear()

    def edit_product(self, data, row):
        categoria = data["categoria"]

        if categoria == "Gorditas":
            from categorias.gorditas import GorditasDialog
            GorditasDialog(self, edit_data=data, edit_row=row).exec_()

        elif categoria == "Bocoles":
            from categorias.bocoles import BocolesDialog
            BocolesDialog(self, edit_data=data, edit_row=row).exec_()

        elif categoria == "Migadas":
            from categorias.migadas import MigadasDialog
            MigadasDialog(self, edit_data=data, edit_row=row).exec_()

        elif categoria == "Tacos de Maiz":
            from categorias.tacosmaiz import TacosDialog
            TacosDialog(self, edit_data=data, edit_row=row).exec_()

        elif categoria == "Tacos de Harina":
            from categorias.Tacosharina import TacosharinaDialog
            TacosharinaDialog(self, edit_data=data, edit_row=row).exec_()

        elif categoria == "Bebidas":
            from categorias.bebidas import BebidasDialog
            BebidasDialog(self, edit_data=data, edit_row=row).exec_()

        elif categoria == "Quesadillas":
            from categorias.quesadillas import QuesadillasDialog
            QuesadillasDialog(self, edit_data=data, edit_row=row).exec_()

        elif categoria == "Big Quesadilla":
            from categorias.Bigquesadilla import BigQuesadillasDialog
            BigQuesadillasDialog(self, edit_data=data, edit_row=row).exec_()

        elif categoria == "Postres":
            from categorias.postres import PostresDialog
            PostresDialog(self, edit_data=data, edit_row=row).exec_()

    # =========================
    # ABRIR CATEGORÍAS
    # =========================
    def open_gorditas(self):
        from categorias.gorditas import GorditasDialog
        GorditasDialog(self).exec_()

    def open_bocoles(self):
        from categorias.bocoles import BocolesDialog
        BocolesDialog(self).exec_()

    def open_migadas(self):
        from categorias.migadas import MigadasDialog
        MigadasDialog(self).exec_()

    def open_tacos_de_maiz(self):
        from categorias.tacosmaiz import TacosDialog
        TacosDialog(self).exec_()

    def open_bebidas(self):
        from categorias.bebidas import BebidasDialog
        BebidasDialog(self).exec_()

    def open_tacos(self):
        from categorias.Tacosharina import TacosharinaDialog
        TacosharinaDialog(self).exec_()

    def open_quesadillas(self):
        from categorias.quesadillas import QuesadillasDialog
        QuesadillasDialog(self).exec_()

    def open_bigquesadillas(self):
        from categorias.Bigquesadilla import BigQuesadillasDialog
        BigQuesadillasDialog(self).exec_()

    def open_postres(self):
        from categorias.postres import PostresDialog
        PostresDialog(self).exec_()

    def add_cafe(self):
        self.add_product({
            "categoria": "Café",
            "tipo": "Café",
            "qty": 1,
            "price": 25
        })

    # =========================
    # CONFIGURAR IMPRESORA
    # =========================
    def open_printer_config(self):
        try:
            from config_impresora import PrinterConfigDialog
            PrinterConfigDialog(self).exec_()
        except ImportError:
            QMessageBox.information(
                self,
                "Impresora",
                "Para usar la impresora, instala:\n\n"
                "pip install python-escpos pyserial\n\n"
                "Y para Windows:\n"
                "pip install pywin32"
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al abrir configuración:\n{e}")

    def open_payment(self):
        if not self.ticket.items_data:
            QMessageBox.warning(self, "Atención", "El ticket está vacío")
            return

        from pago import PaymentDialog
        PaymentDialog(self, self.ticket).exec_()

    def open_corte(self):
        from corte import CorteDialog
        CorteDialog(self, self.ticket).exec_()

    def open_registros(self):
        RegistrosSemanalesDialog(self).exec_()