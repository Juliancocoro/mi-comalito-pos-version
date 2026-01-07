from PyQt5.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout,
    QComboBox, QFrame
)
from PyQt5.QtCore import Qt
from guisos import GUISOS


class MigadasDialog(QDialog):
    def __init__(self, parent, edit_data=None, edit_row=None):
        super().__init__(parent)

        self.parent = parent
        self.edit_data = edit_data
        self.edit_row = edit_row

        self.setWindowTitle("Migadas")
        self.setFixedSize(460, 520)

        # ===== PRECIOS =====
        self.base_price = 85
        self.extra_price = 0

        self.qty = edit_data["qty"] if edit_data else 1
        self.guisos = edit_data.get("guisos", 1) if edit_data else 1

        self.menu = list(GUISOS.keys())

        # ===== CONTENEDOR =====
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 20px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Migadas")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")

        # ===== TIPO =====
        self.type_box = QComboBox()
        self.type_box.addItems(self.menu)
        self.type_box.setStyleSheet("""
            QComboBox {
                font-size: 18px;
                padding: 12px;
                border-radius: 14px;
                border: 2px solid #ccc;
            }
        """)

        if edit_data:
            self.type_box.setCurrentText(edit_data["tipo"])

        self.type_box.currentTextChanged.connect(self.update_price)

        # ===== CANTIDAD MIGADAS =====
        layout.addWidget(title)
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.type_box)
        layout.addWidget(QLabel("Cantidad:"))
        layout.addLayout(self.counter(
            self.decrease_qty, self.increase_qty,
            lambda: self.qty
        ))

        # ===== GUISOS =====
        layout.addWidget(QLabel("Cantidad de guisos:"))
        layout.addLayout(self.counter(
            self.decrease_guisos, self.increase_guisos,
            lambda: self.guisos
        ))

        # ===== PRECIO =====
        self.price_label = QLabel()
        self.price_label.setAlignment(Qt.AlignCenter)
        self.price_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #1a73e8;
        """)

        btn_add = QPushButton("AGREGAR AL TICKET")
        btn_add.setFixedHeight(60)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border-radius: 16px;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        btn_add.clicked.connect(self.confirm)

        layout.addWidget(self.price_label)
        layout.addStretch()
        layout.addWidget(btn_add)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)

        self.update_price()

    # =========================
    # CONTADOR GENERICO
    # =========================
    def counter(self, minus, plus, value_func):
        layout = QHBoxLayout()

        btn_minus = QPushButton("−")
        btn_plus = QPushButton("+")

        for btn in (btn_minus, btn_plus):
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 26px;
                    border-radius: 25px;
                    background-color: #e0e0e0;
                }
            """)

        label = QLabel(str(value_func()))
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(60)
        label.setStyleSheet("font-size: 22px; font-weight: bold;")

        def refresh():
            label.setText(str(value_func()))
            self.update_price()

        btn_minus.clicked.connect(lambda: (minus(), refresh()))
        btn_plus.clicked.connect(lambda: (plus(), refresh()))

        layout.addStretch()
        layout.addWidget(btn_minus)
        layout.addWidget(label)
        layout.addWidget(btn_plus)
        layout.addStretch()

        return layout

    # =========================
    # QTY
    # =========================
    def increase_qty(self):
        self.qty += 1

    def decrease_qty(self):
        if self.qty > 1:
            self.qty -= 1

    # =========================
    # GUISOS
    # =========================
    def increase_guisos(self):
        self.guisos += 1

    def decrease_guisos(self):
        if self.guisos > 1:
            self.guisos -= 1

    # =========================
    # PRECIO
    # =========================
    def update_price(self):
        extras = max(0, self.guisos - 1)
        unit_price = self.base_price + extras * self.extra_price
        total = unit_price * self.qty
        self.price_label.setText(f"Precio: ${total}")

    # =========================
    # CONFIRMAR
    # =========================
    def confirm(self):
        extras = max(0, self.guisos - 1)
        price = self.base_price + extras * self.extra_price

        data = {
            "categoria": "Migadas",
            "tipo": f"{self.type_box.currentText()} ({self.guisos} guisos)",
            "qty": self.qty,
            "price": price,
            "guisos": self.guisos
        }

        if self.edit_data:
            self.parent.ticket.replace_item(self.edit_row, data)
        else:
            self.parent.add_product(data)

        self.accept()
