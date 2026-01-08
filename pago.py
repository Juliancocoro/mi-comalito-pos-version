import sys
import os
from PyQt5.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, 
    QCheckBox, QTextEdit, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from datetime import datetime


def resource_path(relative_path):
    """Obtiene la ruta correcta para recursos empaquetados"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class TicketPreviewDialog(QDialog):
    """Diálogo que muestra vista previa del ticket"""
    
    def __init__(self, parent, ticket_text):
        super().__init__(parent)
        
        self.setWindowTitle("Vista Previa del Ticket")
        self.setFixedSize(420, 650)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("📄 Vista Previa")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Área del ticket (simula papel térmico)
        ticket_container = QWidget()
        ticket_container.setStyleSheet("""
            QWidget {
                background-color: #fffef5;
                border: 2px solid #ccc;
                border-radius: 8px;
            }
        """)
        
        ticket_layout = QVBoxLayout(ticket_container)
        ticket_layout.setContentsMargins(15, 15, 15, 15)
        ticket_layout.setSpacing(10)
        
        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = resource_path("loguito.jpeg")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Escalar el logo para que quepa en el ticket (ancho máximo 200px)
            scaled_pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            # Si no hay logo, mostrar texto
            logo_label.setText("MI COMALITO")
            logo_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        ticket_layout.addWidget(logo_label)
        
        # Texto del ticket
        self.ticket_display = QTextEdit()
        self.ticket_display.setReadOnly(True)
        self.ticket_display.setText(ticket_text)
        self.ticket_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                background-color: transparent;
                border: none;
                color: #000;
            }
        """)
        self.ticket_display.setMinimumHeight(280)
        
        ticket_layout.addWidget(self.ticket_display)
        layout.addWidget(ticket_container)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_print = QPushButton("🖨️ Imprimir")
        self.btn_print.setFixedHeight(50)
        self.btn_print.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #2d8a47;
            }
        """)
        self.btn_print.clicked.connect(self.accept)
        
        self.btn_skip = QPushButton("Omitir")
        self.btn_skip.setFixedHeight(50)
        self.btn_skip.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                font-size: 14px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #ccc;
            }
        """)
        self.btn_skip.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_skip)
        btn_layout.addWidget(self.btn_print)
        
        layout.addLayout(btn_layout)


class PaymentDialog(QDialog):
    def __init__(self, parent, ticket):
        super().__init__(parent)

        self.ticket = ticket
        self.parent = parent

        self.setWindowTitle("Pago")
        self.setFixedSize(380, 340)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        title = QLabel("TOTAL A PAGAR")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        total = QLabel(f"${self.ticket.total:.2f}")
        total.setAlignment(Qt.AlignCenter)
        total.setStyleSheet(
            "font-size: 32px; font-weight: bold; color: #1a73e8;"
        )

        btn_pay = QPushButton("CONFIRMAR PAGO")
        btn_pay.setFixedHeight(60)
        btn_pay.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #1558b0;
            }
        """)
        btn_pay.clicked.connect(self.confirm_payment)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(45)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                font-size: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #ccc;
            }
        """)
        btn_cancel.clicked.connect(self.reject)

        layout.addWidget(title)
        layout.addWidget(total)
        layout.addStretch()
        layout.addWidget(btn_pay)
        layout.addWidget(btn_cancel)

    def generate_ticket_preview(self, ticket_num):
        """Genera el texto de vista previa del ticket (sin encabezado, el logo va arriba)"""
        now = datetime.now()
        
        lines = []
        lines.append("=" * 34)
        lines.append(f"  Fecha: {now.strftime('%d/%m/%Y')}")
        lines.append(f"  Hora:  {now.strftime('%H:%M:%S')}")
        lines.append(f"  Ticket: #{ticket_num}")
        lines.append("-" * 34)
        
        for item in self.ticket.items_data:
            qty = item.get("qty", 1)
            categoria = item.get("categoria", "")
            tipo = item.get("tipo", "")
            subtotal = item.get("subtotal", 0)
            
            producto = f"{categoria}"
            if tipo:
                producto += f" - {tipo}"
            
            # Truncar si es muy largo
            if len(producto) > 24:
                producto = producto[:21] + "..."
            
            lines.append(f"  {qty} x {producto}")
            lines.append(f"                      ${subtotal:.2f}")
        
        lines.append("-" * 34)
        lines.append(f"  TOTAL:              ${self.ticket.total:.2f}")
        lines.append("=" * 34)
        lines.append("    ¡GRACIAS POR SU COMPRA!")
        lines.append("=" * 34)
        
        return "\n".join(lines)

    def confirm_payment(self):
        # Número de ticket
        ticket_num = self.ticket.tickets_pagados + 1
        
        # Generar vista previa
        ticket_text = self.generate_ticket_preview(ticket_num)
        
        # Mostrar diálogo de vista previa
        preview = TicketPreviewDialog(self, ticket_text)
        
        if preview.exec_() == QDialog.Accepted:
            # Usuario quiere imprimir
            self.print_ticket()
        
        # Actualizar totales (se actualiza siempre, imprima o no)
        self.ticket.total_vendido += self.ticket.total
        self.ticket.tickets_pagados += 1

        QMessageBox.information(self, "Pago", "Pago realizado con éxito")
        self.ticket.clear()
        self.accept()

    def print_ticket(self):
        """Intenta imprimir el ticket - NO falla si no hay impresora"""
        try:
            from impresora import PrinterManager

            pm = PrinterManager()

            # Si no hay configuración, simplemente no imprime
            if not pm.config:
                QMessageBox.warning(
                    self,
                    "Impresora",
                    "No hay impresora configurada.\n\n"
                    "Ve a Impresora para configurarla."
                )
                return

            # Intentar conectar e imprimir
            if pm.connect_from_config():
                if pm.print_ticket(
                    self.ticket.items_data,
                    self.ticket.total,
                    self.ticket.tickets_pagados + 1
                ):
                    pass  # Impresión exitosa
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Error al enviar a la impresora"
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "No se pudo conectar a la impresora"
                )

        except ImportError:
            # Si no está el módulo, simplemente no imprime
            pass
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Error de impresión:\n{e}"
            )