from PyQt5.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, QLabel, QFrame
)
from PyQt5.QtCore import Qt


class BebidasDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.setWindowTitle("Bebidas")
        self.setFixedSize(420, 300)

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 20px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        title = QLabel("Bebidas")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")

        btn_aguas = QPushButton("🥤 Aguas de Sabor")
        btn_refrescos = QPushButton("🥤 Refrescos")

        for btn in (btn_aguas, btn_refrescos):
            btn.setFixedHeight(70)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a73e8;
                    color: white;
                    border-radius: 18px;
                    font-size: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1558b0;
                }
            """)

        btn_aguas.clicked.connect(self.open_aguas)
        btn_refrescos.clicked.connect(self.open_refrescos)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(btn_aguas)
        layout.addWidget(btn_refrescos)
        layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)

    def open_aguas(self):
        from categorias.aguas import AguasDialog
        AguasDialog(self.parent).exec_()

    def open_refrescos(self):
        from categorias.refrescos import RefrescosDialog
        RefrescosDialog(self.parent).exec_()
