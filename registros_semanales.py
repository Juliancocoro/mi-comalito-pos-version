from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
    QComboBox, QFileDialog
)
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
import json
from pathlib import Path
import calendar
from fpdf import FPDF

ARCHIVO = Path("ventas.json")


class RegistrosSemanalesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("📊 Registros de Ventas")
        self.setFixedSize(750, 600)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(15)

        # =========================
        # TÍTULO
        # =========================
        titulo = QLabel("📊 Resumen de Ventas")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
        """)
        self.main_layout.addWidget(titulo)

        # =========================
        # SELECTOR DE MES
        # =========================
        self.combo_mes = QComboBox()
        self.combo_mes.setFixedHeight(35)

        for m in range(1, 13):
            self.combo_mes.addItem(calendar.month_name[m], m)

        self.combo_mes.setCurrentIndex(datetime.now().month - 1)
        self.combo_mes.currentIndexChanged.connect(self.actualizar_vista)

        self.main_layout.addWidget(self.combo_mes)

        # =========================
        # TARJETAS
        # =========================
        totales = self.calcular_totales_hoy()

        cards = QHBoxLayout()
        cards.setSpacing(15)

        self.card_dia = self._card("HOY", totales["dia"])
        self.card_semana = self._card("SEMANA", totales["semana"])
        self.card_mes = self._card("MES", totales["mes"])

        cards.addWidget(self.card_dia)
        cards.addWidget(self.card_semana)
        cards.addWidget(self.card_mes)

        self.main_layout.addLayout(cards)

        # =========================
        # GRÁFICA
        # =========================
        self.chart_view = self.crear_grafica_mes(
            self.calcular_por_mes(datetime.now().month)[1]
        )
        self.main_layout.addWidget(self.chart_view)

        # =========================
        # BOTONES
        # =========================
        btns = QHBoxLayout()
        btns.setSpacing(15)

        btn_pdf = QPushButton("📤 Exportar PDF")
        btn_pdf.setFixedHeight(40)
        btn_pdf.clicked.connect(self.exportar_pdf)

        btn_close = QPushButton("CERRAR")
        btn_close.setFixedHeight(40)
        btn_close.clicked.connect(self.accept)

        btns.addWidget(btn_pdf)
        btns.addWidget(btn_close)

        self.main_layout.addLayout(btns)

    # =========================
    # CARD
    # =========================
    def _card(self, titulo, valor):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(frame)

        lbl_t = QLabel(titulo)
        lbl_t.setAlignment(Qt.AlignCenter)
        lbl_t.setStyleSheet("font-size: 14px; color: #555;")

        lbl_v = QLabel(f"${valor:.2f}")
        lbl_v.setAlignment(Qt.AlignCenter)
        lbl_v.setStyleSheet("font-size: 20px; font-weight: bold;")

        layout.addWidget(lbl_t)
        layout.addWidget(lbl_v)

        return frame

    # =========================
    # TOTALES HOY / SEMANA / MES
    # =========================
    def calcular_totales_hoy(self):
        if not ARCHIVO.exists():
            return {"dia": 0, "semana": 0, "mes": 0}

        with open(ARCHIVO, "r", encoding="utf-8") as f:
            ventas = json.load(f)

        hoy = datetime.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        inicio_mes = hoy.replace(day=1)

        total_dia = total_semana = total_mes = 0

        for v in ventas:
            fecha = datetime.strptime(v["fecha"], "%Y-%m-%d").date()
            total = v["total_vendido"]

            if fecha == hoy:
                total_dia += total
            if fecha >= inicio_semana:
                total_semana += total
            if fecha >= inicio_mes:
                total_mes += total

        return {
            "dia": total_dia,
            "semana": total_semana,
            "mes": total_mes
        }

    # =========================
    # CÁLCULO POR MES
    # =========================
    def calcular_por_mes(self, mes):
        if not ARCHIVO.exists():
            return 0, {}, {}

        with open(ARCHIVO, "r", encoding="utf-8") as f:
            ventas = json.load(f)

        total_mes = 0
        por_dia = {}
        por_semana = {}

        for v in ventas:
            fecha = datetime.strptime(v["fecha"], "%Y-%m-%d").date()
            if fecha.month != mes:
                continue

            total_mes += v["total_vendido"]

            por_dia[fecha.day] = por_dia.get(fecha.day, 0) + v["total_vendido"]
            semana = fecha.isocalendar()[1]
            por_semana[semana] = por_semana.get(semana, 0) + v["total_vendido"]

        return total_mes, por_dia, por_semana

    # =========================
    # ACTUALIZAR VISTA
    # =========================
    def actualizar_vista(self):
        mes = self.combo_mes.currentData()
        total_mes, por_dia, _ = self.calcular_por_mes(mes)

        self.card_mes.findChildren(QLabel)[1].setText(f"${total_mes:.2f}")

        self.main_layout.removeWidget(self.chart_view)
        self.chart_view.deleteLater()

        self.chart_view = self.crear_grafica_mes(por_dia)
        self.main_layout.insertWidget(3, self.chart_view)

    # =========================
    # GRÁFICA DEL MES
    # =========================
    def crear_grafica_mes(self, por_dia):
        series = QBarSeries()
        bar = QBarSet("Ventas del Mes")

        for dia in range(1, 32):
            bar.append(por_dia.get(dia, 0))

        series.append(bar)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Ventas por Día del Mes")
        chart.createDefaultAxes()
        chart.legend().setVisible(False)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        return view

    # =========================
    # EXPORTAR PDF
    # =========================
    def exportar_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar PDF", "reporte_ventas.pdf", "PDF (*.pdf)"
        )
        if not path:
            return

        mes_num = self.combo_mes.currentData()
        mes_nombre = self.combo_mes.currentText()
        total_mes, por_dia, por_semana = self.calcular_por_mes(mes_num)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, f"REPORTE DE VENTAS - {mes_nombre}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 8, f"Total del mes: ${total_mes:.2f}", ln=True)
        pdf.ln(5)

        pdf.cell(0, 8, "Ventas por semana:", ln=True)
        for s, t in por_semana.items():
            pdf.cell(0, 8, f"Semana {s}: ${t:.2f}", ln=True)

        pdf.ln(5)
        pdf.cell(0, 8, "Ventas por día:", ln=True)
        for d, t in por_dia.items():
            pdf.cell(0, 8, f"Día {d}: ${t:.2f}", ln=True)

        pdf.output(path)
