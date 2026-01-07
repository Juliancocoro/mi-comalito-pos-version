import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QLineEdit, QLabel
)
from PyQt5.QtCore import Qt

ARCH_GUISOS = Path("guisos.json")
ARCH_AGUAS = Path("aguas.json")
ARCH_REFRESCOS = Path("refrescos.json")
ARCH_POSTRES = Path("postres.json")


def cargar_json(path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


class EditarMenuDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("🛠️ Editar Menú")
        self.setFixedSize(520, 460)

        self.seccion_actual = "guisos"

        self.guisos = cargar_json(ARCH_GUISOS)
        self.aguas = cargar_json(ARCH_AGUAS)
        self.refrescos = cargar_json(ARCH_REFRESCOS)
        self.postres = cargar_json(ARCH_POSTRES)

        layout = QVBoxLayout(self)

        # =========================
        # BOTONES SUPERIORES
        # =========================
        top = QHBoxLayout()

        btn_guisos = QPushButton("🍲 Guisos")
        btn_aguas = QPushButton("🥤 Aguas")
        btn_refrescos = QPushButton("🥤 Refrescos")
        btn_postres = QPushButton("🍰 Postres")

        for b in (btn_guisos, btn_aguas, btn_refrescos, btn_postres):
            b.setFixedHeight(40)
            b.setStyleSheet("font-size:16px; font-weight:bold;")

        btn_guisos.clicked.connect(lambda: self.cambiar_seccion("guisos"))
        btn_aguas.clicked.connect(lambda: self.cambiar_seccion("aguas"))
        btn_refrescos.clicked.connect(lambda: self.cambiar_seccion("refrescos"))
        btn_postres.clicked.connect(lambda: self.cambiar_seccion("postres"))

        top.addWidget(btn_guisos)
        top.addWidget(btn_aguas)
        top.addWidget(btn_refrescos)
        top.addWidget(btn_postres)

        # =========================
        # TITULO
        # =========================
        self.title = QLabel()
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:18px; font-weight:bold;")

        # =========================
        # TABLA
        # =========================
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nombre", "Precio"])
        self.table.horizontalHeader().setStretchLastSection(True)

        # =========================
        # INPUTS
        # =========================
        add_layout = QHBoxLayout()

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre")

        self.input_precio = QLineEdit()
        self.input_precio.setPlaceholderText("Precio")

        btn_add = QPushButton("➕ Agregar")
        btn_add.clicked.connect(self.agregar)

        add_layout.addWidget(self.input_nombre)
        add_layout.addWidget(self.input_precio)
        add_layout.addWidget(btn_add)

        # =========================
        # BOTONES INFERIORES
        # =========================
        bottom = QHBoxLayout()

        btn_delete = QPushButton("❌ Eliminar")
        btn_save = QPushButton("💾 Guardar")

        btn_delete.clicked.connect(self.eliminar)
        btn_save.clicked.connect(self.guardar)

        bottom.addWidget(btn_delete)
        bottom.addWidget(btn_save)

        # =========================
        # LAYOUT FINAL
        # =========================
        layout.addLayout(top)
        layout.addWidget(self.title)
        layout.addWidget(self.table)
        layout.addLayout(add_layout)
        layout.addLayout(bottom)

        self.cambiar_seccion("guisos")

    # =========================
    # CAMBIAR SECCION
    # =========================
    def cambiar_seccion(self, seccion):
        self.seccion_actual = seccion
        self.table.setRowCount(0)

        if seccion == "guisos":
            self.title.setText("🍲 Editar Guisos")
            data = self.guisos
        elif seccion == "aguas":
            self.title.setText("🥤 Editar Aguas")
            data = self.aguas
        elif seccion == "refrescos":
            self.title.setText("🥤 Editar Refrescos")
            data = self.refrescos
        else:
            self.title.setText("🍰 Editar Postres")
            data = self.postres

        for nombre, precio in data.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(nombre))
            self.table.setItem(row, 1, QTableWidgetItem(str(precio)))

    # =========================
    # AGREGAR
    # =========================
    def agregar(self):
        nombre = self.input_nombre.text().strip()
        precio = self.input_precio.text().strip()

        if not nombre or not precio:
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return

        try:
            precio = float(precio)
        except ValueError:
            QMessageBox.warning(self, "Error", "Precio inválido")
            return

        if self.seccion_actual == "guisos":
            self.guisos[nombre] = precio
        elif self.seccion_actual == "aguas":
            self.aguas[nombre] = precio
        elif self.seccion_actual == "refrescos":
            self.refrescos[nombre] = precio
        else:
            self.postres[nombre] = precio

        self.input_nombre.clear()
        self.input_precio.clear()
        self.cambiar_seccion(self.seccion_actual)

    # =========================
    # ELIMINAR
    # =========================
    def eliminar(self):
        row = self.table.currentRow()
        if row < 0:
            return

        nombre = self.table.item(row, 0).text()

        if self.seccion_actual == "guisos":
            del self.guisos[nombre]
        elif self.seccion_actual == "aguas":
            del self.aguas[nombre]
        elif self.seccion_actual == "refrescos":
            del self.refrescos[nombre]
        else:
            del self.postres[nombre]

        self.table.removeRow(row)

    # =========================
    # GUARDAR
    # =========================
    def guardar(self):
        data = {}
        for row in range(self.table.rowCount()):
            nombre = self.table.item(row, 0).text()
            precio = float(self.table.item(row, 1).text())
            data[nombre] = precio

        if self.seccion_actual == "guisos":
            self.guisos = data
            guardar_json(ARCH_GUISOS, data)
        elif self.seccion_actual == "aguas":
            self.aguas = data
            guardar_json(ARCH_AGUAS, data)
        elif self.seccion_actual == "refrescos":
            self.refrescos = data
            guardar_json(ARCH_REFRESCOS, data)
        else:
            self.postres = data
            guardar_json(ARCH_POSTRES, data)

        QMessageBox.information(self, "Listo", "Cambios guardados correctamente")
