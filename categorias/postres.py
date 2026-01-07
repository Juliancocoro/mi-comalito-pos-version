from PyQt5.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QVBoxLayout, QFrame, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
import json
from pathlib import Path

ARCH_POSTRES = Path("postres.json")


class PostresDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.setWindowTitle("Postres")
        self.resize(420, 400)  # 👈 ya NO es fijo

        # =========================
        # CONTENEDOR PRINCIPAL
        # =========================
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 20px;
            }
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title = QLabel("Postres")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")

        # =========================
        # SCROLL AREA
        # =========================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(15)

        scroll.setWidget(scroll_content)

        main_layout.addWidget(title)
        main_layout.addWidget(scroll)

        wrapper = QVBoxLayout(self)
        wrapper.addWidget(container)

        self.btn_style = """
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border-radius: 14px;
                padding: 18px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1558b0;
            }
        """

        self.cargar_postres()

    # =========================
    # CARGAR POSTRES DESDE JSON
    # =========================
    def cargar_postres(self):
        if not ARCH_POSTRES.exists():
            return

        with open(ARCH_POSTRES, "r", encoding="utf-8") as f:
            postres = json.load(f)

        for nombre, precio in postres.items():
            btn = QPushButton(f"{nombre}  ${precio}")
            btn.setStyleSheet(self.btn_style)
            btn.setFixedHeight(60)

            btn.clicked.connect(
                lambda _, n=nombre, p=precio: self.add_postre(n, p)
            )

            self.scroll_layout.addWidget(btn)

        self.scroll_layout.addStretch()  # 👈 empuja hacia arriba

    # =========================
    # AGREGAR AL TICKET
    # =========================
    def add_postre(self, tipo, price):
        data = {
            "categoria": "Postres",
            "tipo": tipo,
            "qty": 1,
            "price": price
        }

        self.parent.add_product(data)
        self.accept()
