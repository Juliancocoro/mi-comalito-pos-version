from PyQt5.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt


class BigQuesadillasDialog(QDialog):
    def __init__(self, parent, edit_data=None, edit_row=None):
        super().__init__(parent)

        self.parent = parent
        self.edit_data = edit_data
        self.edit_row = edit_row

        self.setWindowTitle("Big Quesadilla")
        self.setFixedSize(460, 420)

        # ===== PRECIO FIJO =====
        self.price_unit = 45
        self.qty = edit_data["qty"] if edit_data else 1

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

        main = QVBoxLayout(self)
        main.addWidget(container)

        title = QLabel("Big Quesadilla")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        # ===== CANTIDAD =====
        layout.addWidget(QLabel("Cantidad:"))
        layout.addLayout(self.counter(
            self.decrease_qty, self.increase_qty,
            lambda: self.qty
        ))

        # ===== PRECIO =====
        self.price_label = QLabel()
        self.price_label.setAlignment(Qt.AlignCenter)
        self.price_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8;"
        )

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

        layout.addStretch()
        layout.addWidget(self.price_label)
        layout.addWidget(btn_add)

        self.update_price()

    # =========================
    # CONTADOR + / -
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
    # PRECIO
    # =========================
    def update_price(self):
        total = self.price_unit * self.qty
        self.price_label.setText(f"Precio: ${total}")

    # =========================
    # CONFIRMAR
    # =========================
    def confirm(self):
        data = {
            "categoria": "Big Quesadilla",
            "tipo": "Big Quesadilla",
            "qty": self.qty,
            "price": self.price_unit
        }

        if self.edit_data:
            self.parent.ticket.replace_item(self.edit_row, data)
        else:
            self.parent.add_product(data)

        self.accept()
