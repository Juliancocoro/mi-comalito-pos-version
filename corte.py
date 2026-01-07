from PyQt5.QtWidgets import (
    QDialog, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox,
    QCheckBox
)
from datetime import datetime
from guardar_corte import guardar_corte


class CorteDialog(QDialog):
    def __init__(self, parent, ticket):
        super().__init__(parent)

        self.ticket = ticket

        self.setWindowTitle("Corte del Día")
        self.setFixedSize(420, 480)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, Monaco, monospace;
                font-size: 14px;
                background: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #ddd;
            }
        """)

        self.text.setText(self.generate_ticket())

        # Checkbox para imprimir
        self.check_print = QCheckBox("Imprimir corte")
        self.check_print.setChecked(True)
        self.check_print.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_close = QPushButton("GUARDAR Y CERRAR")
        btn_close.setFixedHeight(50)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1558b0;
            }
        """)
        btn_close.clicked.connect(self.save_and_close)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(50)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 12px;
                font-size: 14px;
            }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_close)

        layout.addWidget(self.text)
        layout.addWidget(self.check_print)
        layout.addLayout(btn_layout)

    def save_and_close(self):
        try:
            # Imprimir si está marcado
            if self.check_print.isChecked():
                self.print_corte()

            # Guardar corte
            guardar_corte(
                self.ticket.total_vendido,
                self.ticket.tickets_pagados
            )

            # Reiniciar contadores del día
            self.ticket.total_vendido = 0.0
            self.ticket.tickets_pagados = 0

            QMessageBox.information(
                self,
                "Corte",
                "Corte guardado correctamente"
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar el corte:\n{e}"
            )

    def print_corte(self):
        """Imprime el corte del día - NO falla si no hay impresora"""
        try:
            from impresora import PrinterManager

            pm = PrinterManager()

            # Si no hay configuración, simplemente no imprime
            if not pm.config:
                return

            if pm.connect_from_config():
                pm.print_corte(
                    self.ticket.total_vendido,
                    self.ticket.tickets_pagados
                )

        except ImportError:
            pass
        except Exception:
            pass

    def generate_ticket(self):
        now = datetime.now()

        return f"""
╔══════════════════════════════╗
║     MICHEL - CORTE DEL DÍA   ║
╚══════════════════════════════╝

  Fecha: {now.strftime('%d/%m/%Y')}
  Hora:  {now.strftime('%H:%M:%S')}

──────────────────────────────

  Tickets cobrados: {self.ticket.tickets_pagados}
  
  Total vendido:    ${self.ticket.total_vendido:.2f}

──────────────────────────────

         FIN DEL CORTE
""".strip()