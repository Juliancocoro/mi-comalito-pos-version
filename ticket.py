# ticket.py (corregido)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QListWidget, QListWidgetItem,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal


class TicketWidget(QWidget):

    edit_requested = pyqtSignal(dict, int)

    def __init__(self):
        super().__init__()

        self.total = 0.0
        self.items_data = []

          # === CORTE DEL DÍA ===
        self.total_vendido = 0.0
        self.tickets_pagados = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("TICKET")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self._request_edit)

        self.list.setStyleSheet("""
            QListWidget {
                font-size: 15px;
            }
            QListWidget::item:selected {
                background: #1a73e8;
                color: white;
            }
        """)

        self.btn_remove = QPushButton("❌ Quitar producto")
        self.btn_remove.setStyleSheet("""
            QPushButton {
                background-color: #d93025;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
            }
        """)
        self.btn_remove.clicked.connect(self.remove_selected)

        self.total_label = QLabel("Total: $0.00")
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        layout.addWidget(title)
        layout.addWidget(self.list)
        layout.addWidget(self.btn_remove)
        layout.addWidget(self.total_label)

    # =========================
    # AGREGAR PRODUCTO
    # =========================
    def add_item(self, data):
        """
        data = {
            "categoria": "Migadas",
            "tipo": "Con huevo",
            "qty": 2,
            "price": 35
        }
        """
        qty = data["qty"]
        categoria = data["categoria"]
        tipo = data.get("tipo", "")  # opcional
        subtotal = qty * data["price"]

        self.items_data.append({
            "categoria": categoria,
            "tipo": tipo,
            "qty": qty,
            "price": data["price"],
            "subtotal": subtotal
        })

        item_text = f"{qty} x {categoria}"
        if tipo:
            item_text += f" - {tipo}"
        item_text += f"     ${subtotal:.2f}"

        self.list.addItem(item_text)
        self.total += subtotal
        self._update_total()

    # =========================
    # SOLICITAR EDICIÓN
    # =========================
    def _request_edit(self):
        row = self.list.currentRow()
        if row >= 0:
            self.edit_requested.emit(self.items_data[row], row)

    # =========================
    # QUITAR PRODUCTO
    # =========================
    def remove_selected(self):
        row = self.list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atención", "Selecciona un producto")
            return

        removed = self.items_data.pop(row)
        self.total -= removed["subtotal"]
        self.list.takeItem(row)
        self._update_total()

    # =========================
    # REEMPLAZAR PRODUCTO (EDICIÓN)
    # =========================
    def replace_item(self, row, data):
        old = self.items_data[row]
        self.total -= old["subtotal"]

        subtotal = data["qty"] * data["price"]
        data["subtotal"] = subtotal

        self.items_data[row] = data

        item_text = f"{data['qty']} x {data['categoria']}"
        if data.get("tipo"):
            item_text += f" - {data['tipo']}"
        item_text += f"     ${subtotal:.2f}"

        self.list.item(row).setText(item_text)

        self.total += subtotal
        self._update_total()

    # =========================
    def clear(self):
        self.list.clear()
        self.items_data.clear()
        self.total = 0
        self._update_total()

    def _update_total(self):
        if self.total < 0:
            self.total = 0
        self.total_label.setText(f"Total: ${self.total:.2f}")
