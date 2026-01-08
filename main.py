# main.py
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


def resource_path(relative_path):
    """Obtiene la ruta correcta para recursos empaquetados"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        # -------- Ventana --------
        self.setWindowTitle("POS Mi Comalito - Login")
        self.setFixedSize(700, 500)

        # -------- Fondo ---------
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, 700, 500)

        pixmap = QPixmap(resource_path("background.jpg"))
        if not pixmap.isNull():
            self.background.setPixmap(
                pixmap.scaled(700, 500, Qt.IgnoreAspectRatio)
            )
        self.background.lower()

        # -------- Título --------
        self.title = QLabel("Mi Comalito POS")
        self.title.setFont(QFont("Arial", 24, QFont.Bold))
        self.title.setStyleSheet("color: black;")

        # -------- Usuario --------
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setFixedHeight(45)
        self.user_input.setStyleSheet("""
            QLineEdit {
                border-radius: 22px;
                padding-left: 15px;
                font-size: 16px;
                background: white;
            }
        """)

        # -------- Contraseña --------
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFixedHeight(45)
        self.pass_input.setStyleSheet("""
            QLineEdit {
                border-radius: 22px;
                padding-left: 15px;
                font-size: 16px;
                background: white;
            }
        """)

        # -------- Botón Entrar --------
        self.login_btn = QPushButton("Entrar")
        self.login_btn.setFixedHeight(50)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1558b0;
            }
        """)
        self.login_btn.clicked.connect(self.verify_login)

        # -------- Layout --------
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.addStretch()
        layout.addWidget(self.title, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)
        layout.addSpacing(10)
        layout.addWidget(self.login_btn)
        layout.addStretch()

        layout.setContentsMargins(120, 40, 120, 40)
        self.setLayout(layout)

    # -------- Login --------
    def verify_login(self):
        user = self.user_input.text().strip()
        pw = self.pass_input.text().strip()

        if user == "admin" and pw == "1234":
            from pos import POSWindow

            self.pos = POSWindow()
            self.pos.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())