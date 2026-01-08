from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from guisos import GUISOS


class BocolesDialog(QDialog):
    def __init__(self, parent, edit_data=None, edit_row=None):
        super().__init__(parent)

        self.parent = parent
        self.edit_data = edit_data
        self.edit_row = edit_row

        self.setWindowTitle("Bocoles")
        self.setFixedSize(460, 420)

        self.base_price = 16  

        self.menu = {
            guiso: self.base_price + extra
            for guiso, extra in GUISOS.items()
        }

        self.qty = edit_data["qty"] if edit_data else 1

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

        title = QLabel("Bocoles")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")

        self.type_box = QComboBox()
        self.type_box.addItems(self.menu.keys())
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

        # -------- Cantidad --------
        qty_layout = QHBoxLayout()
        qty_layout.setSpacing(25)

        btn_minus = QPushButton("−")
        btn_plus = QPushButton("+")

        for btn in (btn_minus, btn_plus):
            btn.setFixedSize(60, 60)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 28px;
                    font-weight: bold;
                    border-radius: 30px;
                    background-color: #e0e0e0;
                }
            """)

        btn_minus.clicked.connect(self.decrease_qty)
        btn_plus.clicked.connect(self.increase_qty)

        self.qty_label = QLabel(str(self.qty))
        self.qty_label.setAlignment(Qt.AlignCenter)
        self.qty_label.setFixedWidth(80)
        self.qty_label.setStyleSheet("font-size: 26px; font-weight: bold;")

        qty_layout.addStretch()
        qty_layout.addWidget(btn_minus)
        qty_layout.addWidget(self.qty_label)
        qty_layout.addWidget(btn_plus)
        qty_layout.addStretch()

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

        layout.addWidget(title)
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.type_box)
        layout.addWidget(QLabel("Cantidad:"))
        layout.addLayout(qty_layout)
        layout.addWidget(self.price_label)
        layout.addStretch()
        layout.addWidget(btn_add)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)

        self.update_price()

    def increase_qty(self):
        self.qty += 1
        self.qty_label.setText(str(self.qty))

    def decrease_qty(self):
        if self.qty > 1:
            self.qty -= 1
            self.qty_label.setText(str(self.qty))

    def update_price(self):
        tipo = self.type_box.currentText()
        self.price_label.setText(f"Precio unitario: ${self.menu[tipo]}")

    def confirm(self):
        tipo = self.type_box.currentText()
        price = self.menu[tipo]

        data = {
            "categoria": "Bocoles",
            "tipo": tipo,
            "qty": self.qty,
            "price": price
        }

        if self.edit_data:
            self.parent.ticket.replace_item(self.edit_row, data)
        else:
            self.parent.add_product(data)  

        self.accept()
