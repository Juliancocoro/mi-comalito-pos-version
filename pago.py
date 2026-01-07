from PyQt5.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QVBoxLayout, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt


class PaymentDialog(QDialog):
    def __init__(self, parent, ticket):
        super().__init__(parent)

        self.ticket = ticket
        self.parent = parent

        self.setWindowTitle("Pago")
        self.setFixedSize(380, 380)

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

        # Checkbox para imprimir ticket
        self.check_print = QCheckBox("Imprimir ticket")
        self.check_print.setChecked(True)
        self.check_print.setStyleSheet("""
            QCheckBox {
                font-size: 16px;
                padding: 10px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
            }
        """)

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
        layout.addWidget(self.check_print)
        layout.addWidget(btn_pay)
        layout.addWidget(btn_cancel)

    def confirm_payment(self):
        # Imprimir ticket si está marcado
        if self.check_print.isChecked():
            self.print_ticket()

        # Actualizar totales
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
                return

            # Intentar conectar e imprimir
            if pm.connect_from_config():
                pm.print_ticket(
                    self.ticket.items_data,
                    self.ticket.total,
                    self.ticket.tickets_pagados + 1
                )

        except ImportError:
            # Si no está el módulo, simplemente no imprime
            pass
        except Exception:
            # Cualquier error, simplemente no imprime
            pass