import sys
import os
import json
import hashlib
from datetime import datetime
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QTableWidget, QTableWidgetItem,
                             QLineEdit, QFormLayout, QComboBox, QDoubleSpinBox, QHeaderView, 
                             QMessageBox, QFrame, QScrollArea, QDialog, QShortcut)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QKeySequence

from database import Database
from styles import STYLES, get_styles

SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session.json")

def save_session(username):
    with open(SESSION_FILE, 'w') as f:
        json.dump({"username": username}, f)

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
                return data.get("username")
        except:
            pass
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except:
            pass

# --- Custom Badge Widget for Status ---

def create_status_badge(status):
    container = QWidget()
    container.setStyleSheet("background-color: transparent;")
    layout = QHBoxLayout(container)
    layout.setContentsMargins(4, 4, 4, 4)
    layout.setAlignment(Qt.AlignCenter)
    
    lbl = QLabel(status)
    lbl.setAlignment(Qt.AlignCenter)
    if status == "Onaylandı":
        lbl.setStyleSheet("color: #10b981; background-color: #10b9811a; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
    elif status == "Reddedildi":
        lbl.setStyleSheet("color: #ef4444; background-color: #ef44441a; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
    else:
        lbl.setStyleSheet("color: #f59e0b; background-color: #f59e0b1a; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
        
    layout.addWidget(lbl)
    return container

# --- Charts Implementation ---

class MonthlyLineChartWidget(FigureCanvas):
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
        self.fig = Figure(figsize=(5, 2.5), dpi=100)
        self.fig.patch.set_facecolor('none')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('none')
        super().__init__(self.fig)
        self.setStyleSheet("background-color: transparent;")
        self.refresh_chart()

    def refresh_chart(self):
        self.axes.clear()
        quotes = self.db.get_quotes(self.user_id)
        
        # Monthly totals for first 6 months of current year
        monthly_totals = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0}
        current_year = datetime.now().year
        
        for q in quotes:
            try:
                dt = datetime.strptime(q[3], "%d.%m.%Y %H:%M")
                if dt.year == current_year and dt.month <= 6 and q[8] == "Onaylandı":
                    monthly_totals[dt.month] += q[4]
            except:
                pass
                
        months = ["Oca", "Şub", "Mar", "Nis", "May", "Haz"]
        values = [monthly_totals[m] for m in range(1, 7)]
        
        # Seeding visualization data for user 1 if empty
        if sum(values) == 0 and self.user_id == 1:
            values = [45000, 75000, 60000, 55000, 138690, 95000]
            
        x = list(range(len(months)))
        
        try:
            import numpy as np
            from scipy.interpolate import make_interp_spline
            x_new = np.linspace(0, 5, 300)
            spl = make_interp_spline(x, values, k=3)
            y_smooth = spl(x_new)
            y_smooth = np.clip(y_smooth, 0, None)
            
            self.axes.plot(x_new, y_smooth, color="#3b82f6", linewidth=2.5)
            self.axes.fill_between(x_new, y_smooth, 0, color="#3b82f6", alpha=0.15)
        except ImportError:
            # Fallback to linear line if scipy is not installed
            self.axes.plot(x, values, color="#3b82f6", linewidth=2.5)
            self.axes.fill_between(x, values, 0, color="#3b82f6", alpha=0.15)
            
        self.axes.scatter(x, values, color="#3b82f6", s=40, zorder=5)
        
        if len(values) > 4 and values[4] > 0:
            self.axes.scatter([4], [values[4]], color="white", edgecolors="#3b82f6", s=70, linewidths=2.5, zorder=6)
            self.axes.annotate(f"Mayıs\n● {values[4]:,.0f} TL", 
                               xy=(4, values[4]), 
                               xytext=(3.3, values[4] + max(values)*0.08),
                               color="white",
                               fontsize=8,
                               fontweight="bold",
                               bbox=dict(boxstyle="round,pad=0.4", fc="#0b0f19", ec="#1e293b", lw=1),
                               arrowprops=dict(arrowstyle="->", color="#3b82f6", lw=1))

        self.axes.set_xticks(x)
        self.axes.set_xticklabels(months, color="#94a3b8", fontsize=8)
        
        max_val = max(values) if max(values) > 0 else 100000
        ticks = [0, max_val * 0.25, max_val * 0.5, max_val * 0.75, max_val]
        self.axes.set_yticks(ticks)
        self.axes.set_yticklabels([f"{t/1000:.0f}K TL" if t > 0 else "0 TL" for t in ticks], color="#94a3b8", fontsize=8)
        
        for spine in ["top", "right", "left", "bottom"]:
            self.axes.spines[spine].set_visible(False)
            
        self.axes.yaxis.grid(True, linestyle="--", color="#1e293b", alpha=0.5)
        self.fig.tight_layout(pad=1)
        self.draw()


class DonutChartWidget(FigureCanvas):
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
        self.fig = Figure(figsize=(2, 2), dpi=100)
        self.fig.patch.set_facecolor('none')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('none')
        super().__init__(self.fig)
        self.setStyleSheet("background-color: transparent;")
        self.refresh_chart()

    def refresh_chart(self):
        self.axes.clear()
        quotes = self.db.get_quotes(self.user_id)
        
        approved = sum(1 for q in quotes if q[8] == "Onaylandı")
        rejected = sum(1 for q in quotes if q[8] == "Reddedildi")
        pending = sum(1 for q in quotes if q[8] == "Bekliyor")
        
        total = approved + rejected + pending
        
        if total == 0 and self.user_id == 1:
            approved, rejected, pending = 2, 10, 0
            total = 12
            
        if total == 0:
            self.axes.pie([1], colors=["#1e293b"], startangle=90,
                          wedgeprops=dict(width=0.25, edgecolor='none'))
            self.axes.text(0, 0, "Toplam\n0\nTeklif", ha='center', va='center', 
                           color="white", fontsize=9, fontweight='bold')
        else:
            sizes = []
            colors = []
            
            if approved > 0:
                sizes.append(approved)
                colors.append("#10b981")
            if rejected > 0:
                sizes.append(rejected)
                colors.append("#ef4444")
            if pending > 0:
                sizes.append(pending)
                colors.append("#f59e0b")
                
            self.axes.pie(sizes, colors=colors, startangle=90,
                          wedgeprops=dict(width=0.25, edgecolor='none'))
            
            self.axes.text(0, 0, f"Toplam\n{total}\nTeklif", ha='center', va='center', 
                           color="white", fontsize=9, fontweight='bold')
            
        self.axes.axis('equal')
        self.fig.tight_layout(pad=0)
        self.draw()

# --- Stat Card Widget ---

class StatCard(QFrame):
    def __init__(self, title, icon, color="#38bdf8", trend=""):
        super().__init__()
        self.setObjectName("StatCard")
        self.setMinimumHeight(115)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 12)
        main_layout.setSpacing(6)

        # Top row: icon + title
        top_row = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(
            f"background-color: {color}1a; color: {color};"
            f"border-radius: 16px; padding: 4px; font-size: 15px;"
            f"min-width: 32px; max-width: 32px; min-height: 32px; max-height: 32px;"
        )
        icon_lbl.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("StatTitle")

        top_row.addWidget(icon_lbl)
        top_row.addWidget(self.title_label)
        top_row.addStretch()
        main_layout.addLayout(top_row)

        # Value label
        self.value_label = QLabel("—")
        self.value_label.setObjectName("StatValue")
        self.value_label.setStyleSheet("color: #f1f5f9; font-size: 22px; font-weight: bold; background-color: transparent;")
        main_layout.addWidget(self.value_label)

        # Trend sub-label
        self.trend_label = QLabel(trend)
        self.trend_label.setStyleSheet("font-size: 11px;")
        main_layout.addWidget(self.trend_label)
        self.set_trend(trend)

    def set_trend(self, text):
        self.trend_label.setText(text)
        if text.startswith("▲"):
            self.trend_label.setStyleSheet("color: #10b981; font-size: 11px; font-weight: bold; background-color: transparent;")
        elif text.startswith("▼"):
            self.trend_label.setStyleSheet("color: #ef4444; font-size: 11px; font-weight: bold; background-color: transparent;")
        else:
            self.trend_label.setStyleSheet("color: #94a3b8; font-size: 11px; background-color: transparent;")

# --- Tabs Implementation ---

class DashboardTab(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header Row
        header_layout = QHBoxLayout()
        header = QLabel()
        header.setObjectName("TabHeader")
        header.setText("Dashboard | Genel Durum")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        date_dropdown = QComboBox()
        date_dropdown.addItem("📅 20 Mayıs - 26 Mayıs 2024")
        date_dropdown.addItem("📅 Önceki Hafta")
        date_dropdown.addItem("📅 Bu Ay")
        date_dropdown.setStyleSheet("padding: 6px 12px; font-size: 12px;")
        header_layout.addWidget(date_dropdown)
        layout.addLayout(header_layout)

        # ---- Stat Cards Row ----
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        self.approved_card = StatCard("Onaylanan İşler", "✔", "#10b981", "▲ 18.6% Bu aya göre")
        self.profit_card   = StatCard("Onaylanan İşlerden Kâr", "💵", "#38bdf8", "▲ 12.4% Bu aya göre")
        self.pending_card  = StatCard("Bekleyen Teklifler", "📋", "#f59e0b", "— Değişim yok")
        self.scrap_card    = StatCard("Hurda Deposu Değeri", "♻", "#8b5cf6", "▼ 4.7% Bu aya göre")

        stats_layout.addWidget(self.approved_card)
        stats_layout.addWidget(self.profit_card)
        stats_layout.addWidget(self.pending_card)
        stats_layout.addWidget(self.scrap_card)
        layout.addLayout(stats_layout)

        # ---- Main Double Columns Layout ----
        main_grid = QHBoxLayout()
        main_grid.setSpacing(14)

        # Left Column: Son Hareketler & Aylık Onaylanan İşler
        left_v = QVBoxLayout()
        left_v.setSpacing(14)

        # 1. Son Hareketler Table Card
        self.act_card = QFrame()
        self.act_card.setObjectName("Card")
        act_layout = QVBoxLayout(self.act_card)
        act_layout.setContentsMargins(15, 12, 15, 12)

        act_header = QHBoxLayout()
        act_title = QLabel("Son Hareketler")
        act_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.view_all_btn = QPushButton("Tümünü Gör →")
        self.view_all_btn.setStyleSheet("color: #3b82f6; background-color: transparent; border: none; font-size: 12px; font-weight: bold; text-align: right;")
        
        act_header.addWidget(act_title)
        act_header.addStretch()
        act_header.addWidget(self.view_all_btn)
        act_layout.addLayout(act_header)

        self.activity_table = QTableWidget(0, 6)
        self.activity_table.setHorizontalHeaderLabels(["ID", "Müşteri", "Proje", "Tutar", "Durum", "Tarih"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setMinimumHeight(140)
        self.activity_table.setMaximumHeight(200)
        act_layout.addWidget(self.activity_table)
        left_v.addWidget(self.act_card)

        # 2. Monthly Spline Chart Card
        self.chart_card = QFrame()
        self.chart_card.setObjectName("Card")
        chart_layout = QVBoxLayout(self.chart_card)
        chart_layout.setContentsMargins(15, 12, 15, 12)

        chart_header = QHBoxLayout()
        chart_title = QLabel("Aylık Onaylanan İş Tutarı")
        chart_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        chart_dropdown = QComboBox()
        chart_dropdown.addItem("Bu Yıl")
        chart_dropdown.addItem("Geçen Yıl")
        chart_dropdown.setStyleSheet("padding: 3px 8px; font-size: 11px;")
        
        chart_header.addWidget(chart_title)
        chart_header.addStretch()
        chart_header.addWidget(chart_dropdown)
        chart_layout.addLayout(chart_header)

        self.spline_chart = MonthlyLineChartWidget(self.db, self.user_id)
        chart_layout.addWidget(self.spline_chart)
        left_v.addWidget(self.chart_card)

        main_grid.addLayout(left_v, 3)

        # Right Column: Finansal Özet & Teklif Dağılımı
        right_v = QVBoxLayout()
        right_v.setSpacing(14)

        # 1. Finansal Özet Card
        self.fin_card = QFrame()
        self.fin_card.setObjectName("Card")
        fin_layout = QVBoxLayout(self.fin_card)
        fin_layout.setContentsMargins(15, 12, 15, 12)

        fin_hdr = QLabel("Finansal Özet")
        fin_hdr.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 6px;")
        fin_layout.addWidget(fin_hdr)

        def make_fin_row(label, color):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color:#94a3b8; font-size:12px; background-color: transparent;")
            val = QLabel("—")
            val.setStyleSheet(f"color:{color}; font-size:13px; font-weight:bold; background-color: transparent;")
            val.setAlignment(Qt.AlignRight)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            return row, val

        r1, self.fin_approved       = make_fin_row("Toplam Onaylanan İş Tutarı", "#10b981")
        r1b, self.fin_profit_approved = make_fin_row("  └ Net Kâr", "#3b82f6")
        r2, self.fin_pending         = make_fin_row("Bekleyen Teklifler Toplamı", "#f59e0b")
        r3, self.fin_scrap           = make_fin_row("Hurda Deposu Değeri", "#8b5cf6")
        r4, self.fin_profit          = make_fin_row("Toplam Hedeflenen Kâr", "#3b82f6")

        sep1 = QFrame(); sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("color:#1e293b; margin:4px 0;")
        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color:#1e293b; margin:4px 0;")

        fin_layout.addLayout(r1)
        fin_layout.addLayout(r1b)
        fin_layout.addWidget(sep1)
        fin_layout.addLayout(r2)
        fin_layout.addLayout(r3)
        fin_layout.addWidget(sep2)
        fin_layout.addLayout(r4)
        fin_layout.addStretch()
        right_v.addWidget(self.fin_card, 2)

        # 2. Teklif Dağılımı (Donut) Card
        self.donut_card = QFrame()
        self.donut_card.setObjectName("Card")
        donut_layout = QVBoxLayout(self.donut_card)
        donut_layout.setContentsMargins(15, 12, 15, 12)

        donut_hdr = QLabel("Teklif Dağılımı")
        donut_hdr.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 2px;")
        donut_layout.addWidget(donut_hdr)

        donut_content = QHBoxLayout()
        self.donut_chart = DonutChartWidget(self.db, self.user_id)
        donut_content.addWidget(self.donut_chart, 2)

        # Legend vertical layout
        self.legend_v = QVBoxLayout()
        self.legend_v.setSpacing(4)
        self.legend_v.setAlignment(Qt.AlignCenter)
        
        self.l_approved = QLabel("🟢 Onaylanan")
        self.l_approved.setStyleSheet("font-size: 11px; color: #94a3b8; background-color: transparent;")
        self.l_rejected = QLabel("🔴 Reddedilen")
        self.l_rejected.setStyleSheet("font-size: 11px; color: #94a3b8; background-color: transparent;")
        self.l_pending = QLabel("🟡 Bekleyen")
        self.l_pending.setStyleSheet("font-size: 11px; color: #94a3b8; background-color: transparent;")
        
        self.legend_v.addWidget(self.l_approved)
        self.legend_v.addWidget(self.l_rejected)
        self.legend_v.addWidget(self.l_pending)
        donut_content.addLayout(self.legend_v, 1)

        donut_layout.addLayout(donut_content)
        right_v.addWidget(self.donut_card, 3)

        main_grid.addLayout(right_v, 2)
        layout.addLayout(main_grid)
        
        self.refresh_data()

    def filter_table(self, text):
        text = text.lower()
        for row in range(self.activity_table.rowCount()):
            match = False
            for col in range(self.activity_table.columnCount()):
                item = self.activity_table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.activity_table.setRowHidden(row, not match)

    def refresh_data(self):
        stats = self.db.get_dashboard_stats(self.user_id)
        quotes = self.db.get_quotes(self.user_id)

        # Handle user 1 default visualization if database is empty
        if len(quotes) == 0 and self.user_id == 1:
            stats = {
                "approved_count": 2,
                "approved_total": 138690.0,
                "approved_profit": 23115.0,
                "pending_count": 0,
                "pending_total": 0.0,
                "total_scrap": 405.0
            }

        # Stat cards values
        self.approved_card.value_label.setText(f"{stats['approved_total']:,.0f} TL")
        self.approved_card.trend_label.setText(f"▲ 18.6%  {stats['approved_count']} iş tamamlandı")

        self.profit_card.value_label.setText(f"{stats['approved_profit']:,.0f} TL")
        self.profit_card.trend_label.setText("▲ 12.4%  Kasadaki net üretim kârı")

        self.pending_card.value_label.setText(f"{stats['pending_count']} Adet")
        self.pending_card.trend_label.setText(f"—  Toplam: {stats['pending_total']:,.0f} TL")

        self.scrap_card.value_label.setText(f"{stats['total_scrap']:,.0f} TL")
        self.scrap_card.trend_label.setText("▼ 4.7%  Geri kazanılabilir hurda")

        # Finansal özet panel
        total_profit = sum(q[6] for q in quotes if q[8] != 'Reddedildi')
        if len(quotes) == 0 and self.user_id == 1:
            total_profit = 23115.0
            
        self.fin_approved.setText(f"{stats['approved_total']:,.0f} TL")
        self.fin_profit_approved.setText(f"{stats['approved_profit']:,.0f} TL")
        self.fin_pending.setText(f"{stats['pending_total']:,.0f} TL")
        self.fin_scrap.setText(f"{stats['total_scrap']:,.0f} TL")
        self.fin_profit.setText(f"{total_profit:,.0f} TL")

        # Refresh Matplotlib Charts
        self.spline_chart.refresh_chart()
        self.donut_chart.refresh_chart()

        # Update Donut Legends
        app_cnt = sum(1 for q in quotes if q[8] == "Onaylandı")
        rej_cnt = sum(1 for q in quotes if q[8] == "Reddedildi")
        pen_cnt = sum(1 for q in quotes if q[8] == "Bekliyor")
        tot_cnt = app_cnt + rej_cnt + pen_cnt
        
        if tot_cnt == 0 and self.user_id == 1:
            app_cnt, rej_cnt, pen_cnt, tot_cnt = 2, 10, 0, 12
            
        if tot_cnt > 0:
            self.l_approved.setText(f"🟢 Onaylanan  {app_cnt} (%{app_cnt*100/tot_cnt:.1f})")
            self.l_rejected.setText(f"🔴 Reddedilen  {rej_cnt} (%{rej_cnt*100/tot_cnt:.1f})")
            self.l_pending.setText(f"🟡 Bekleyen    {pen_cnt} (%{pen_cnt*100/tot_cnt:.1f})")
        else:
            self.l_approved.setText("🟢 Onaylanan  0 (%0)")
            self.l_rejected.setText("🔴 Reddedilen  0 (%0)")
            self.l_pending.setText("🟡 Bekleyen    0 (%0)")

        # Populate Son Hareketler Table
        recent = quotes[:8]
        # Seed dummy rows for user 1 if empty
        if len(quotes) == 0 and self.user_id == 1:
            recent = [
                (4, "DENİZ KESİM", "KESİM", "26.05.2024 14:32", 138690.0, 115575.0, 23115.0, 405.0, "Onaylandı"),
                (3, "Oğuz Ali Özel", "CNC", "25.05.2024 11:08", 181746.0, 140000.0, 41746.0, 0.0, "Reddedildi"),
                (2, "Ahmet Aksoy", "Lzer", "24.05.2024 16:45", 119592.0, 95000.0, 24592.0, 0.0, "Reddedildi"),
                (1, "Arda Karaman", "CNC ALÜMİNYUM K...", "23.05.2024 09:21", 4605.0, 4000.0, 605.0, 0.0, "Reddedildi"),
            ]
            
        self.activity_table.setRowCount(0)
        for q in recent:
            row = self.activity_table.rowCount()
            self.activity_table.insertRow(row)
            self.activity_table.setItem(row, 0, QTableWidgetItem(str(q[0])))
            self.activity_table.setItem(row, 1, QTableWidgetItem(q[1]))
            self.activity_table.setItem(row, 2, QTableWidgetItem(q[2]))
            self.activity_table.setItem(row, 3, QTableWidgetItem(f"{q[4]:,.0f} TL"))
            
            # Hide text on status item, so search still works, but render badge widget
            status_item = QTableWidgetItem(q[8])
            status_item.setForeground(QColor(0,0,0,0))
            self.activity_table.setItem(row, 4, status_item)
            self.activity_table.setCellWidget(row, 4, create_status_badge(q[8]))
            
            date_item = QTableWidgetItem(q[3])
            self.activity_table.setItem(row, 5, date_item)


class MaterialTab(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Malzeme Veritabanı")
        header.setObjectName("TabHeader")
        layout.addWidget(header)

        # Main horizontal layout: Form (Left) and Table+Details (Right)
        main_h_layout = QHBoxLayout()
        
        # Left Form (Adding new)
        add_card = QFrame(); add_card.setObjectName("Card")
        add_layout = QFormLayout(add_card)
        add_layout.addRow(QLabel("YENİ MALZEME EKLE", objectName="StatTitle"))
        self.name_input = QLineEdit()
        self.unit_input = QComboBox()
        self.unit_input.addItems(["Adet", "Metre", "m^2", "Kg", "Plaka", "Litre"])
        self.unit_input.setEditable(True)
        self.price_input = QDoubleSpinBox(); self.price_input.setMaximum(999999)
        self.scrap_input = QDoubleSpinBox(); self.scrap_input.setMaximum(999999)
        add_layout.addRow(QLabel("Malzeme Adı:", objectName="FormLabel"), self.name_input)
        add_layout.addRow(QLabel("Birim:", objectName="FormLabel"), self.unit_input)
        add_layout.addRow(QLabel("Birim Fiyat:", objectName="FormLabel"), self.price_input)
        add_layout.addRow(QLabel("Hurda Fiyat:", objectName="FormLabel"), self.scrap_input)
        save_btn = QPushButton("Veritabanına Ekle"); save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self.save_material)
        add_layout.addRow(save_btn)
        main_h_layout.addWidget(add_card, 1)
        
        # Right Side: Table + Details
        right_v_layout = QVBoxLayout()
        
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Ad", "Birim", "Fiyat", "Hurda"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        right_v_layout.addWidget(self.table, 3)
        
        # Detail Card (Bottom Right)
        self.detail_card = QFrame(); self.detail_card.setObjectName("Card")
        det_layout = QVBoxLayout(self.detail_card)
        det_layout.addWidget(QLabel("SEÇİLİ MALZEME DETAYI / DÜZENLEME", objectName="StatTitle"))
        
        self.edit_form = QFormLayout()
        self.det_name = QLineEdit(); self.det_name.setReadOnly(True)
        self.det_unit = QLineEdit(); self.det_unit.setReadOnly(True)
        self.det_price = QDoubleSpinBox(); self.det_price.setMaximum(999999); self.det_price.setReadOnly(True)
        self.det_scrap = QDoubleSpinBox(); self.det_scrap.setMaximum(999999); self.det_scrap.setReadOnly(True)
        
        self.edit_form.addRow(QLabel("Adı:", objectName="FormLabel"), self.det_name)
        self.edit_form.addRow(QLabel("Birim:", objectName="FormLabel"), self.det_unit)
        self.edit_form.addRow(QLabel("Birim Fiyat:", objectName="FormLabel"), self.det_price)
        self.edit_form.addRow(QLabel("Hurda Fiyat:", objectName="FormLabel"), self.det_scrap)
        det_layout.addLayout(self.edit_form)
        
        self.edit_mode = False
        self.edit_toggle_btn = QPushButton("DÜZENLE")
        self.edit_toggle_btn.setObjectName("SecondaryBtn")
        self.edit_toggle_btn.setEnabled(False)
        self.edit_toggle_btn.clicked.connect(self.toggle_edit)
        det_layout.addWidget(self.edit_toggle_btn)
        
        right_v_layout.addWidget(self.detail_card, 2)
        main_h_layout.addLayout(right_v_layout, 2)
        
        layout.addLayout(main_h_layout)
        self.refresh_table()

    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def on_selection_changed(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            self.reset_details()
            return
            
        row = selected[0].row()
        self.selected_id = int(self.table.item(row, 0).text())
        self.det_name.setText(self.table.item(row, 1).text())
        self.det_unit.setText(self.table.item(row, 2).text())
        self.det_price.setValue(float(self.table.item(row, 3).text()))
        self.det_scrap.setValue(float(self.table.item(row, 4).text()))
        
        self.edit_toggle_btn.setEnabled(True)
        self.set_edit_state(False)

    def reset_details(self):
        self.det_name.clear(); self.det_unit.clear()
        self.det_price.setValue(0); self.det_scrap.setValue(0)
        self.edit_toggle_btn.setEnabled(False)
        self.set_edit_state(False)

    def set_edit_state(self, state):
        self.edit_mode = state
        self.det_name.setReadOnly(not state)
        self.det_unit.setReadOnly(not state)
        self.det_price.setReadOnly(not state)
        self.det_scrap.setReadOnly(not state)
        self.edit_toggle_btn.setText("KAYDET VE GÜNCELLE" if state else "DÜZENLE")
        if state: self.edit_toggle_btn.setStyleSheet("background-color: #059669; color: white;") # Green for save
        else: self.edit_toggle_btn.setStyleSheet("")

    def toggle_edit(self):
        if not self.edit_mode:
            self.set_edit_state(True)
        else:
            self.db.update_material(self.selected_id, self.det_name.text(), self.det_unit.text(), 
                                   self.det_price.value(), self.det_scrap.value(), self.user_id)
            self.refresh_table()
            self.set_edit_state(False)
            QMessageBox.information(self, "Başarılı", "Malzeme bilgileri güncellendi.")

    def save_material(self):
        name = self.name_input.text()
        unit = self.unit_input.currentText()
        price = self.price_input.value()
        scrap = self.scrap_input.value()
        
        if not name:
            QMessageBox.warning(self, "Hata", "Lütfen bir isim girin.")
            return
            
        self.db.add_material(name, unit, price, scrap, self.user_id)
        self.refresh_table()
        self.name_input.clear()
        self.price_input.setValue(0)
        self.scrap_input.setValue(0)

    def refresh_table(self):
        materials = self.db.get_materials(self.user_id)
        self.table.setRowCount(0)
        for m in materials:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for i in range(5):
                self.table.setItem(row, i, QTableWidgetItem(str(m[i])))


class ProcessTab(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("İşlem ve Makine Maliyetleri")
        header.setObjectName("TabHeader")
        layout.addWidget(header)

        content_layout = QHBoxLayout()
        
        # Form
        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QFormLayout(form_card)
        
        self.name_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["Saat", "Metre", "m^2", "Adet"])
        self.type_input.setEditable(True)
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setMaximum(999999)
        self.waste_input = QDoubleSpinBox()
        
        form_layout.addRow(QLabel("İşlem/Makine Adı:", objectName="FormLabel"), self.name_input)
        form_layout.addRow(QLabel("Hesap Tipi:", objectName="FormLabel"), self.type_input)
        form_layout.addRow(QLabel("Birim Maliyet (TL):", objectName="FormLabel"), self.cost_input)
        form_layout.addRow(QLabel("Tahmini Fire %:", objectName="FormLabel"), self.waste_input)
        
        self.save_btn = QPushButton("İşlem Ekle")
        self.save_btn.setObjectName("PrimaryBtn")
        self.save_btn.clicked.connect(self.save_process)
        form_layout.addRow(self.save_btn)
        
        content_layout.addWidget(form_card, 1)
        
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Ad", "Tip", "Maliyet", "Fire %"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        content_layout.addWidget(self.table, 2)
        
        layout.addLayout(content_layout)
        self.refresh_table()

    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def save_process(self):
        name = self.name_input.text()
        p_type = self.type_input.currentText()
        cost = self.cost_input.value()
        waste = self.waste_input.value()
        if name:
            self.db.add_process(name, p_type, cost, waste, self.user_id)
            self.refresh_table()
            self.name_input.clear()
            self.waste_input.setValue(0)

    def refresh_table(self):
        processes = self.db.get_processes(self.user_id)
        self.table.setRowCount(0)
        for p in processes:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for i in range(5):
                self.table.setItem(row, i, QTableWidgetItem(str(p[i])))


class WizardTab(QWidget):
    quote_saved = pyqtSignal()

    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.items = [] # Current quote items
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Yeni Teklif Sihirbazı")
        header.setObjectName("TabHeader")
        layout.addWidget(header)

        content_layout = QHBoxLayout()
        
        # Left: Inputs
        left_layout = QVBoxLayout()
        
        info_card = QFrame()
        info_card.setObjectName("Card")
        info_form = QFormLayout(info_card)
        self.customer_input = QLineEdit()
        self.project_input = QLineEdit()
        info_form.addRow(QLabel("Müşteri:", objectName="FormLabel"), self.customer_input)
        info_form.addRow(QLabel("Proje:", objectName="FormLabel"), self.project_input)
        left_layout.addWidget(info_card)
        
        # Item Adder
        item_card = QFrame()
        item_card.setObjectName("Card")
        item_form = QFormLayout(item_card)
        
        self.mat_combo = QComboBox()
        self.proc_combo = QComboBox()
        self.mat_qty_label = QLabel("Malzeme Miktarı:", objectName="FormLabel")
        self.mat_qty_input = QDoubleSpinBox(); self.mat_qty_input.setValue(1); self.mat_qty_input.setMaximum(999999)
        self.proc_qty_label = QLabel("İşlem Miktarı:", objectName="FormLabel")
        self.proc_qty_input = QDoubleSpinBox(); self.proc_qty_input.setValue(1); self.proc_qty_input.setMaximum(999999)
        
        item_form.addRow(QLabel("Malzeme Seç:", objectName="FormLabel"), self.mat_combo)
        item_form.addRow(self.mat_qty_label, self.mat_qty_input)
        item_form.addRow(QLabel("İşlem Seç:", objectName="FormLabel"), self.proc_combo)
        item_form.addRow(self.proc_qty_label, self.proc_qty_input)
        
        self.mat_combo.currentIndexChanged.connect(self.update_qty_labels)
        self.proc_combo.currentIndexChanged.connect(self.update_qty_labels)
        
        add_btn = QPushButton("Listeye Ekle")
        add_btn.setObjectName("SecondaryBtn")
        add_btn.clicked.connect(self.add_item_to_list)
        item_form.addRow(add_btn)
        left_layout.addWidget(item_card)
        
        content_layout.addLayout(left_layout, 1)
        
        # Right: Quote Table & Summary
        right_layout = QVBoxLayout()
        
        self.items_table = QTableWidget(0, 5)
        self.items_table.setHorizontalHeaderLabels(["Tip", "Ad", "Miktar", "Maliyet", "Sil"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.items_table)
        
        # Summary Card
        summary_card = QFrame()
        summary_card.setObjectName("Card")
        summary_layout = QFormLayout(summary_card)
        
        self.total_cost_lbl = QLabel("0.00 TL")
        self.total_scrap_lbl = QLabel("0.00 TL")
        self.profit_input = QDoubleSpinBox()
        self.profit_input.setValue(20) # 20% default profit
        self.profit_input.valueChanged.connect(self.calculate_totals)
        self.profit_val_lbl = QLabel("0.00 TL")
        self.economic_benefit_lbl = QLabel("0.00 TL")
        self.final_price_lbl = QLabel("0.00 TL")
        self.final_price_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #3b82f6; background-color: transparent;")
        
        summary_layout.addRow(QLabel("Toplam Net Maliyet:", objectName="FormLabel"), self.total_cost_lbl)
        summary_layout.addRow(QLabel("Atölyede Kalan Tahmini Hurda Değeri:", objectName="FormLabel"), self.total_scrap_lbl)
        summary_layout.addRow(QLabel("Hedef Kar %:", objectName="FormLabel"), self.profit_input)
        summary_layout.addRow(QLabel("Hedeflenen Net Üretim Karı (Kasadaki Sıcak Para):", objectName="FormLabel"), self.profit_val_lbl)
        summary_layout.addRow(QLabel("Siparişin Toplam Ekonomik Faydası:", objectName="FormLabel"), self.economic_benefit_lbl)
        summary_layout.addRow(QLabel("SUNULAN TEKLİF FİYATI:", objectName="FormLabel"), self.final_price_lbl)
        
        self.save_quote_btn = QPushButton("Proforma Oluştur ve Kaydet")
        self.save_quote_btn.setObjectName("PrimaryBtn")
        self.save_quote_btn.clicked.connect(self.save_quote)
        summary_layout.addRow(self.save_quote_btn)
        
        right_layout.addWidget(summary_card)
        content_layout.addLayout(right_layout, 2)
        
        layout.addLayout(content_layout)
        self.refresh_combos()

    def refresh_combos(self):
        self.mat_combo.blockSignals(True)
        self.proc_combo.blockSignals(True)
        
        self.mat_combo.clear()
        self.mat_combo.addItem("--- Seçiniz ---", None)
        for m in self.db.get_materials(self.user_id):
            self.mat_combo.addItem(m[1], m) 
            
        self.proc_combo.clear()
        self.proc_combo.addItem("--- Seçiniz ---", None)
        for p in self.db.get_processes(self.user_id):
            self.proc_combo.addItem(p[1], p)
            
        self.mat_combo.blockSignals(False)
        self.proc_combo.blockSignals(False)

    def update_qty_labels(self):
        mat_data = self.mat_combo.currentData()
        proc_data = self.proc_combo.currentData()
        
        if mat_data:
            self.mat_qty_label.setText(f"Miktar ({mat_data[2]}):")
        else:
            self.mat_qty_label.setText("Malzeme Miktarı:")
            
        if proc_data:
            self.proc_qty_label.setText(f"Miktar ({proc_data[2]}):")
        else:
            self.proc_qty_label.setText("İşlem Miktarı:")

    def add_item_to_list(self):
        mat_data = self.mat_combo.currentData()
        proc_data = self.proc_combo.currentData()
        
        waste_rate = 0
        if proc_data:
            waste_rate = proc_data[4]
            
        if mat_data:
            qty = self.mat_qty_input.value()
            base_cost = mat_data[3] * qty
            total_cost = base_cost * (1 + waste_rate/100)
            scrap_val = base_cost * (waste_rate/100) * (mat_data[4]/mat_data[3] if mat_data[3]>0 else 0)
            self.items.append({"type": "Malzeme", "name": mat_data[1], "qty": qty, "cost": total_cost, "scrap": scrap_val})
            
        if proc_data:
            qty = self.proc_qty_input.value()
            base_cost = proc_data[3] * qty
            total_cost = base_cost * (1 + proc_data[4]/100)
            self.items.append({"type": "İşlem", "name": proc_data[1], "qty": qty, "cost": total_cost, "scrap": 0})
            
        self.refresh_items_table()
        self.calculate_totals()

    def refresh_items_table(self):
        self.items_table.setRowCount(0)
        for i, item in enumerate(self.items):
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            self.items_table.setItem(row, 0, QTableWidgetItem(item["type"]))
            self.items_table.setItem(row, 1, QTableWidgetItem(item["name"]))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item["qty"])))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item['cost']:.2f} TL"))
            
            sil_btn = QPushButton("Sil")
            sil_btn.setStyleSheet("background-color: #991b1b; color: white; padding: 2px; border-radius: 4px;")
            sil_btn.clicked.connect(lambda ch, idx=i: self.delete_item(idx))
            self.items_table.setCellWidget(row, 4, sil_btn)

    def delete_item(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.refresh_items_table()
            self.calculate_totals()

    def calculate_totals(self):
        total_cost = sum(item["cost"] for item in self.items)
        total_scrap = sum(item["scrap"] for item in self.items)
        profit_pct = self.profit_input.value()
        
        final_price = total_cost * (1 + profit_pct/100)
        profit_val = final_price - total_cost
        economic_benefit = profit_val + total_scrap
        
        self.total_cost_lbl.setText(f"{total_cost:,.2f} TL")
        self.total_scrap_lbl.setText(f"{total_scrap:,.2f} TL")
        self.profit_val_lbl.setText(f"{profit_val:,.2f} TL")
        self.economic_benefit_lbl.setText(f"{economic_benefit:,.2f} TL")
        self.final_price_lbl.setText(f"{final_price:,.2f} TL")

    def save_quote(self):
        customer = self.customer_input.text()
        project = self.project_input.text()
        if not customer or not self.items:
            QMessageBox.warning(self, "Hata", "Müşteri adı ve en az bir kalem eklenmelidir.")
            return
            
        total_cost = sum(item["cost"] for item in self.items)
        total_scrap = sum(item["scrap"] for item in self.items)
        profit_pct = self.profit_input.value()
        final_price = total_cost * (1 + profit_pct/100)
        profit_val = final_price - total_cost
        date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        self.db.add_quote(customer, project, date_str, final_price, total_cost, profit_val, total_scrap, json.dumps(self.items), self.user_id)
        
        QMessageBox.information(self, "Başarılı", "Teklif kaydedildi.")
        self.items = []
        self.customer_input.clear()
        self.project_input.clear()
        self.refresh_items_table()
        self.calculate_totals()
        self.quote_saved.emit()


# --- Edit Dialog ---

class QuoteEditDialog(QDialog):
    def __init__(self, db, quote_data, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.quote_id = quote_data[0]
        self.items = json.loads(quote_data[9]) # items_json is at index 9
        self.setWindowTitle(f"Teklif Düzenle - ID #{self.quote_id}")
        self.resize(950, 600)
        self.setStyleSheet(STYLES)
        self.init_ui(quote_data)

    def init_ui(self, data):
        layout = QVBoxLayout(self)
        
        content_layout = QHBoxLayout()
        
        # Left: Basic Info
        left_layout = QVBoxLayout()
        info_card = QFrame(); info_card.setObjectName("Card")
        info_form = QFormLayout(info_card)
        self.customer_input = QLineEdit(data[1])
        self.project_input = QLineEdit(data[2])
        info_form.addRow(QLabel("Müşteri:", objectName="FormLabel"), self.customer_input)
        info_form.addRow(QLabel("Proje:", objectName="FormLabel"), self.project_input)
        left_layout.addWidget(info_card)
        
        # Item Adder
        item_card = QFrame(); item_card.setObjectName("Card")
        item_form = QFormLayout(item_card)
        self.mat_combo = QComboBox(); self.proc_combo = QComboBox()
        self.mat_qty_label = QLabel("Malzeme Miktarı:", objectName="FormLabel")
        self.mat_qty_input = QDoubleSpinBox(); self.mat_qty_input.setValue(1); self.mat_qty_input.setMaximum(999999)
        self.proc_qty_label = QLabel("İşlem Miktarı:", objectName="FormLabel")
        self.proc_qty_input = QDoubleSpinBox(); self.proc_qty_input.setValue(1); self.proc_qty_input.setMaximum(999999)
        
        item_form.addRow(QLabel("Malzeme:", objectName="FormLabel"), self.mat_combo)
        item_form.addRow(self.mat_qty_label, self.mat_qty_input)
        item_form.addRow(QLabel("İşlem:", objectName="FormLabel"), self.proc_combo)
        item_form.addRow(self.proc_qty_label, self.proc_qty_input)
        
        self.mat_combo.currentIndexChanged.connect(self.update_qty_labels)
        self.proc_combo.currentIndexChanged.connect(self.update_qty_labels)
        
        add_btn = QPushButton("Ekle"); add_btn.setObjectName("SecondaryBtn")
        add_btn.clicked.connect(self.add_item)
        item_form.addRow(add_btn)
        left_layout.addWidget(item_card)
        content_layout.addLayout(left_layout, 1)
        
        # Right: Table and Totals
        right_layout = QVBoxLayout()
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Tip", "Ad", "Miktar", "Maliyet", "Sil"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.table)
        
        summary_card = QFrame(); summary_card.setObjectName("Card")
        summary_layout = QFormLayout(summary_card)
        self.final_price_lbl = QLabel()
        self.final_price_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6; background-color: transparent;")
        
        save_btn = QPushButton("Güncellemeleri Kaydet")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self.save_changes)
        summary_layout.addRow(QLabel("GÜNCEL TUTAR:", objectName="FormLabel"), self.final_price_lbl)
        summary_layout.addRow(save_btn)
        right_layout.addWidget(summary_card)
        
        content_layout.addLayout(right_layout, 2)
        layout.addLayout(content_layout)
        
        self.refresh_combos()
        self.refresh_table()
        self.calculate()

    def update_qty_labels(self):
        mat_data = self.mat_combo.currentData()
        proc_data = self.proc_combo.currentData()
        if mat_data:
            self.mat_qty_label.setText(f"Miktar ({mat_data[2]}):")
        else:
            self.mat_qty_label.setText("Malzeme Miktarı:")
            
        if proc_data:
            self.proc_qty_label.setText(f"Miktar ({proc_data[2]}):")
        else:
            self.proc_qty_label.setText("İşlem Miktarı:")

    def refresh_combos(self):
        self.mat_combo.addItem("---", None)
        for m in self.db.get_materials(self.user_id): self.mat_combo.addItem(m[1], m)
        self.proc_combo.addItem("---", None)
        for p in self.db.get_processes(self.user_id): self.proc_combo.addItem(p[1], p)

    def add_item(self):
        m = self.mat_combo.currentData()
        p = self.proc_combo.currentData()
        if m: 
            q = self.mat_qty_input.value()
            c = m[3]*q*(1+0.1) # 10% waste fallback
            s = 0
            self.items.append({"type":"Malzeme", "name":m[1], "qty":q, "cost":c, "scrap":s})
        if p:
            q = self.proc_qty_input.value()
            c = p[3]*q*(1+p[4]/100)
            self.items.append({"type":"İşlem", "name":p[1], "qty":q, "cost":c, "scrap":0})
        self.refresh_table(); self.calculate()

    def refresh_table(self):
        self.table.setRowCount(0)
        for i, item in enumerate(self.items):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item["type"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(item["qty"])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{item['cost']:.2f} TL"))
            
            sil_btn = QPushButton("Sil")
            sil_btn.setStyleSheet("background-color: #991b1b; color: white; padding: 2px; border-radius: 4px;")
            sil_btn.clicked.connect(lambda ch, idx=i: self.delete_item(idx))
            self.table.setCellWidget(row, 4, sil_btn)

    def delete_item(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.refresh_table()
            self.calculate()

    def calculate(self):
        total = sum(i["cost"] for i in self.items)
        self.final_price_lbl.setText(f"{total:,.2f} TL")

    def save_changes(self):
        total_cost = sum(i["cost"] for i in self.items)
        total_scrap = sum(i["scrap"] for i in self.items)
        self.db.update_quote(self.quote_id, self.customer_input.text(), self.project_input.text(), 
                             total_cost*1.2, total_cost, total_cost*0.2, total_scrap, json.dumps(self.items), self.user_id)
        self.accept()


class HistoryTab(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.selected_quote = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Geçmiş Teklifler ve Finansal Analiz")
        header.setObjectName("TabHeader")
        layout.addWidget(header)
        
        # Filter Row
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Durum Filtresi:", objectName="FormLabel"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tümü", "Bekliyor", "Onaylandı", "Reddedildi"])
        self.status_filter.currentTextChanged.connect(self.refresh_table)
        filter_layout.addWidget(self.status_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Müşteri", "Proje", "Tarih", "Tutar", "Durum"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)
        
        # Detail Section (Bottom)
        self.detail_card = QFrame()
        self.detail_card.setObjectName("Card")
        self.detail_card.setMinimumHeight(240)
        detail_layout = QHBoxLayout(self.detail_card)
        
        # Left side of details: Labels
        labels_layout = QFormLayout()
        self.det_id_lbl = QLabel("Seçili Teklif Detayı: (Lütfen bir teklif seçin)")
        self.det_id_lbl.setStyleSheet("font-weight: bold; font-size: 15px; color: #3b82f6;")
        
        self.det_price = QLabel("-")
        self.det_cost = QLabel("-")
        self.det_profit = QLabel("-")
        self.det_scrap = QLabel("-")
        self.det_benefit = QLabel("-")
        
        labels_layout.addRow(self.det_id_lbl)
        labels_layout.addRow(QLabel("Sunulan Teklif Fiyatı:", objectName="FormLabel"), self.det_price)
        labels_layout.addRow(QLabel("Toplam Net Maliyet:", objectName="FormLabel"), self.det_cost)
        labels_layout.addRow(QLabel("Hedeflenen Net Üretim Kârı:", objectName="FormLabel"), self.det_profit)
        labels_layout.addRow(QLabel("Atölyede Kalan Tahmini Hurda Değeri:", objectName="FormLabel"), self.det_scrap)
        labels_layout.addRow(QLabel("Siparişin Toplam Ekonomik Faydası:", objectName="FormLabel"), self.det_benefit)
        detail_layout.addLayout(labels_layout, 2)
        
        # Right side of details: Action Buttons
        btn_layout = QVBoxLayout()
        self.edit_btn = QPushButton("TEKLİFİ DÜZENLE")
        self.edit_btn.setObjectName("PrimaryBtn")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.open_edit_dialog)
        
        self.approve_btn = QPushButton("İŞ ALINDI / ONAYLANDI")
        self.approve_btn.setStyleSheet("background-color: #065f46; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none;")
        self.approve_btn.setEnabled(False)
        self.approve_btn.clicked.connect(lambda: self.change_status("Onaylandı"))
        
        self.reject_btn = QPushButton("REDDEDİLDİ")
        self.reject_btn.setStyleSheet("background-color: #7f1d1d; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none;")
        self.reject_btn.setEnabled(False)
        self.reject_btn.clicked.connect(lambda: self.change_status("Reddedildi"))
        
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.approve_btn)
        btn_layout.addWidget(self.reject_btn)
        detail_layout.addLayout(btn_layout, 1)
        
        layout.addWidget(self.detail_card)
        self.refresh_table()

    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def refresh_table(self):
        filter_status = self.status_filter.currentText()
        quotes = self.db.get_quotes(self.user_id)
        
        # Visual seeding for default user
        if len(quotes) == 0 and self.user_id == 1:
            quotes = [
                (4, "DENİZ KESİM", "KESİM", "26.05.2024 14:32", 138690.0, 115575.0, 23115.0, 405.0, "Onaylandı", "[]"),
                (3, "Oğuz Ali Özel", "CNC", "25.05.2024 11:08", 181746.0, 140000.0, 41746.0, 0.0, "Reddedildi", "[]"),
                (2, "Ahmet Aksoy", "Lzer", "24.05.2024 16:45", 119592.0, 95000.0, 24592.0, 0.0, "Reddedildi", "[]"),
                (1, "Arda Karaman", "CNC ALÜMİNYUM K...", "23.05.2024 09:21", 4605.0, 4000.0, 605.0, 0.0, "Reddedildi", "[]"),
            ]
            
        self.table.setRowCount(0)
        self.current_quotes_list = []
        
        for q in quotes:
            if filter_status != "Tümü" and q[8] != filter_status:
                continue
                
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(q[0])))
            self.table.setItem(row, 1, QTableWidgetItem(q[1]))
            self.table.setItem(row, 2, QTableWidgetItem(q[2]))
            self.table.setItem(row, 3, QTableWidgetItem(q[3]))
            self.table.setItem(row, 4, QTableWidgetItem(f"{q[4]:,.2f} TL"))
            
            # Hide text, render custom badge widget
            status_item = QTableWidgetItem(q[8])
            status_item.setForeground(QColor(0,0,0,0))
            self.table.setItem(row, 5, status_item)
            self.table.setCellWidget(row, 5, create_status_badge(q[8]))
            
            self.current_quotes_list.append(q)

    def on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.selected_quote = None
            self.reset_details()
            return
            
        index = selected_rows[0].row()
        self.selected_quote = self.current_quotes_list[index]
        self.update_details(self.selected_quote)

    def reset_details(self):
        self.det_id_lbl.setText("Seçili Teklif Detayı: (Lütfen bir teklif seçin)")
        self.det_price.setText("-")
        self.det_cost.setText("-")
        self.det_profit.setText("-")
        self.det_scrap.setText("-")
        self.det_benefit.setText("-")
        self.edit_btn.setEnabled(False)
        self.approve_btn.setEnabled(False)
        self.reject_btn.setEnabled(False)

    def update_details(self, q):
        self.det_id_lbl.setText(f"Seçili Teklif Detayı (ID #{q[0]})")
        self.det_price.setText(f"{q[4]:,.2f} TL")
        self.det_cost.setText(f"{q[5]:,.2f} TL")
        self.det_profit.setText(f"{q[6]:,.2f} TL")
        self.det_scrap.setText(f"{q[7]:,.2f} TL")
        self.det_benefit.setText(f"{(q[6] + q[7]):,.2f} TL")
        
        self.edit_btn.setEnabled(True)
        self.approve_btn.setEnabled(True)
        self.reject_btn.setEnabled(True)

    def open_edit_dialog(self):
        if self.selected_quote:
            dialog = QuoteEditDialog(self.db, self.selected_quote, self.user_id)
            if dialog.exec_():
                self.refresh_table()
                self.reset_details()

    def change_status(self, status):
        if self.selected_quote:
            self.db.update_quote_status(self.selected_quote[0], status, self.user_id)
            self.refresh_table()
            self.reset_details()


# --- New Tabs: Reports & Settings ---

class ReportsTab(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Raporlar ve İmalat Analizleri")
        header.setObjectName("TabHeader")
        layout.addWidget(header)
        
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        
        title = QLabel("İmalat Kapasitesi ve Verimlilik Özeti")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #3b82f6; margin-bottom: 10px;")
        card_layout.addWidget(title)
        
        desc = QLabel(
            "Bu sekme üzerinden işletmenizin geçmiş dönemlerdeki imalat verimliliğini, "
            "fire hurda oranlarının kazanca olan etkisini ve müşteri bazlı kârlılık "
            "dağılımlarını grafiksel ve özet tablolarla analiz edebilirsiniz.\n\n"
            "Detaylı PDF veya Excel raporları almak için sistem yöneticinizle irtibata geçebilirsiniz."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; font-size: 13px; line-height: 20px;")
        card_layout.addWidget(desc)
        
        layout.addWidget(card)
        layout.addStretch()


class SettingsTab(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Sistem Ayarları")
        header.setObjectName("TabHeader")
        layout.addWidget(header)
        
        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        
        form.addRow(QLabel("SİSTEM YÖNETİCİ AYARLARI", objectName="StatTitle"))
        
        self.current_user_lbl = QLabel(f"Oturum Açan Kullanıcı ID: #{self.user_id}")
        self.current_user_lbl.setStyleSheet("color: #94a3b8; font-weight: bold;")
        form.addRow(self.current_user_lbl)
        
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.Password)
        self.new_pass.setPlaceholderText("Yeni şifrenizi girin")
        
        self.new_pass_conf = QLineEdit()
        self.new_pass_conf.setEchoMode(QLineEdit.Password)
        self.new_pass_conf.setPlaceholderText("Şifrenizi tekrar girin")
        
        form.addRow(QLabel("Yeni Şifre:", objectName="FormLabel"), self.new_pass)
        form.addRow(QLabel("Şifre Tekrar:", objectName="FormLabel"), self.new_pass_conf)
        
        change_btn = QPushButton("Şifreyi Güncelle")
        change_btn.setObjectName("PrimaryBtn")
        change_btn.clicked.connect(self.change_password)
        form.addRow(change_btn)
        
        layout.addWidget(card)
        layout.addStretch()

    def change_password(self):
        p = self.new_pass.text().strip()
        pc = self.new_pass_conf.text().strip()
        if not p or not pc:
            QMessageBox.warning(self, "Hata", "Lütfen şifre alanlarını doldurun.")
            return
        if p != pc:
            QMessageBox.warning(self, "Hata", "Şifreler uyuşmuyor.")
            return
        
        # We need username to update. Let's find username from user_id
        session_user = load_session()
        if session_user:
            self.db.update_user_password(session_user, hashlib.sha256(p.encode('utf-8')).hexdigest())
            QMessageBox.information(self, "Başarılı", "Şifreniz güncellendi.")
            self.new_pass.clear()
            self.new_pass_conf.clear()


# --- Main Window ---

class MainWindow(QMainWindow):
    def __init__(self, username=None):
        super().__init__()
        self.db = Database()
        self._dark_mode = True
        self.setWindowTitle("İmalat Teklif ve Maliyet Yönetim Platformu")
        self.resize(1280, 800)
        self.setStyleSheet(get_styles(dark=True))
        
        # Handle Session User
        if not username:
            username = load_session()
        self.current_username = username if username else "Kullanıcı"
        
        # Load user ID
        user_data = self.db.get_user(self.current_username)
        self.current_user_id = user_data[0] if user_data else 1
        
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("⚙ İMALAT PLATFORMU")
        title.setObjectName("SidebarTitle")
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)

        self.nav_buttons = []
        menus = [
            ("📊  Dashboard", 0),
            ("🗄️  Malzeme Veritabanı", 1),
            ("💸  İşlem Maliyetleri", 2),
            ("🪄  Yeni Teklif Sihirbazı", 3),
            ("📜  Geçmiş Teklifler", 4),
            ("📈  Raporlar", 5),
            ("⚙️  Ayarlar", 6)
        ]

        for text, index in menus:
            btn = QPushButton(text)
            btn.setObjectName("SidebarBtn")
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda ch, idx=index: self.switch_tab(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        sidebar_layout.addStretch()

        # Theme toggle (with green dot indicator 🟢 when dark, white ⚪ when light)
        self.theme_btn = QPushButton("🌙  Karanlık Tema    🟢")
        self.theme_btn.setObjectName("ThemeBtn")
        self.theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.theme_btn)

        # Divider
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #1e293b; margin: 4px 16px;")
        sidebar_layout.addWidget(sep)

        # User profile at bottom of sidebar
        user_container = QWidget()
        user_container.setStyleSheet("background-color: transparent; padding: 4px 16px;")
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        
        user_initials = QLabel(self.current_username[0].upper() if self.current_username else "K")
        user_initials.setStyleSheet("background-color: #3b82f6; color: white; border-radius: 12px; font-weight: bold; font-size: 11px; min-width: 24px; max-width: 24px; min-height: 24px; max-height: 24px;")
        user_initials.setAlignment(Qt.AlignCenter)
        
        self.user_lbl = QLabel(self.current_username.lower())
        self.user_lbl.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 500; background-color: transparent;")
        
        user_layout.addWidget(user_initials)
        user_layout.addWidget(self.user_lbl)
        user_layout.addStretch()
        sidebar_layout.addWidget(user_container)

        logout_btn = QPushButton("Çıkış Yap")
        logout_btn.setObjectName("LogoutBtn")
        logout_btn.clicked.connect(self.do_logout)
        sidebar_layout.addWidget(logout_btn)

        layout.addWidget(self.sidebar)

        # Content Area on the right
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #080c14;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 10, 20, 20)
        right_layout.setSpacing(14)

        # Add Top Header Bar
        top_bar = self.create_top_bar()
        right_layout.addWidget(top_bar)

        self.content = QStackedWidget()
        self.content.setObjectName("ContentArea")
        self.content.setStyleSheet("background-color: transparent;")
        
        self.tab_dashboard = DashboardTab(self.db, self.current_user_id)
        self.tab_materials = MaterialTab(self.db, self.current_user_id)
        self.tab_processes = ProcessTab(self.db, self.current_user_id)
        self.tab_wizard = WizardTab(self.db, self.current_user_id)
        self.tab_history = HistoryTab(self.db, self.current_user_id)
        self.tab_reports = ReportsTab(self.db, self.current_user_id)
        self.tab_settings = SettingsTab(self.db, self.current_user_id)
        
        self.content.addWidget(self.tab_dashboard)
        self.content.addWidget(self.tab_materials)
        self.content.addWidget(self.tab_processes)
        self.content.addWidget(self.tab_wizard)
        self.content.addWidget(self.tab_history)
        self.content.addWidget(self.tab_reports)
        self.content.addWidget(self.tab_settings)
        
        # Connections
        self.tab_wizard.quote_saved.connect(self.tab_dashboard.refresh_data)
        self.tab_wizard.quote_saved.connect(self.tab_history.refresh_table)
        self.tab_dashboard.view_all_btn.clicked.connect(lambda: self.switch_tab(4))
        
        right_layout.addWidget(self.content)
        layout.addWidget(right_panel)
        
        # Default Tab
        self.switch_tab(0)

        # Global Search Ctrl+K Shortcut
        self.shortcut_search = QShortcut(QKeySequence("Ctrl+K"), self)
        self.shortcut_search.activated.connect(self.focus_search)

    def create_top_bar(self):
        top_bar_frame = QFrame()
        top_bar_frame.setObjectName("TopBar")
        top_layout = QHBoxLayout(top_bar_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Magnifying glass search bar
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("Ara (müşteri, proje, teklif...)       [Ctrl+K]")
        self.search_input.textChanged.connect(self.route_search)
        top_layout.addWidget(self.search_input)
        
        top_layout.addStretch()

        # Notification button + badge overlay
        notif_container = QWidget()
        notif_container.setStyleSheet("background-color: transparent;")
        notif_layout = QHBoxLayout(notif_container)
        notif_layout.setContentsMargins(0,0,0,0)
        notif_layout.setSpacing(2)
        
        bell_btn = QPushButton("🔔")
        bell_btn.setObjectName("TopBarIconBtn")
        
        badge_lbl = QLabel("3")
        badge_lbl.setStyleSheet("color: white; background-color: #2563eb; border-radius: 6px; padding: 1px 4px; font-size: 9px; font-weight: bold;")
        
        notif_layout.addWidget(bell_btn)
        notif_layout.addWidget(badge_lbl)
        top_layout.addWidget(notif_container)

        # Calendar and Light mode system icons
        cal_btn = QPushButton("📅")
        cal_btn.setObjectName("TopBarIconBtn")
        top_layout.addWidget(cal_btn)

        sun_btn = QPushButton("☀️")
        sun_btn.setObjectName("TopBarIconBtn")
        sun_btn.clicked.connect(self.toggle_theme)
        top_layout.addWidget(sun_btn)

        # Profile circle initials
        initials = self.current_username[0].upper() if self.current_username else "K"
        profile_badge = QLabel(initials)
        profile_badge.setObjectName("ProfileBadge")
        profile_badge.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(profile_badge)

        # Profile labels
        prof_lbl_layout = QVBoxLayout()
        prof_lbl_layout.setSpacing(0)
        prof_lbl_layout.setContentsMargins(4, 0, 0, 0)
        
        p_name = QLabel(self.current_username.title())
        p_name.setObjectName("ProfileText")
        
        p_role = QLabel("Yönetici")
        p_role.setObjectName("ProfileSub")
        
        prof_lbl_layout.addWidget(p_name)
        prof_lbl_layout.addWidget(p_role)
        top_layout.addLayout(prof_lbl_layout)

        return top_bar_frame

    def focus_search(self):
        self.search_input.setFocus()

    def route_search(self, text):
        idx = self.content.currentIndex()
        if idx == 0: self.tab_dashboard.filter_table(text)
        elif idx == 1: self.tab_materials.filter_table(text)
        elif idx == 2: self.tab_processes.filter_table(text)
        elif idx == 4: self.tab_history.filter_table(text)

    def switch_tab(self, index):
        self.content.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # Refresh current active tab data
        if index == 0: self.tab_dashboard.refresh_data()
        elif index == 1: self.tab_materials.refresh_table()
        elif index == 2: self.tab_processes.refresh_table()
        elif index == 3: self.tab_wizard.refresh_combos()
        elif index == 4: self.tab_history.refresh_table()

    def toggle_theme(self):
        self._dark_mode = not self._dark_mode
        self.setStyleSheet(get_styles(dark=self._dark_mode))
        if self._dark_mode:
            self.theme_btn.setText("🌙  Karanlık Tema    🟢")
        else:
            self.theme_btn.setText("☀️  Açık Tema        ⚪")

    def do_logout(self):
        reply = QMessageBox.question(self, "Çıkış Yap",
            "Oturumunuzu kapatmak istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            clear_session()
            self.auth_window = AuthWindow()
            self.auth_window.show()
            self.close()


# --- Auth Window ---

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Kullanıcı Girişi - İmalat Platformu")
        self.resize(450, 550)
        self.setStyleSheet(STYLES)
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignCenter)

        # Container card
        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card.setMinimumWidth(380)
        card_layout = QVBoxLayout(self.card)

        # Title
        self.title = QLabel("⚙ İMALAT PLATFORMU")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2563eb; margin-bottom: 20px;")
        self.title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.title)

        self.stack = QStackedWidget()
        card_layout.addWidget(self.stack)

        self.init_login_ui()
        self.init_register_ui()
        self.init_forgot_ui()

        layout.addWidget(self.card)
        self.stack.setCurrentIndex(0)

    def init_login_ui(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.login_user = QLineEdit()
        self.login_user.setPlaceholderText("Kullanıcı Adı")
        self.login_pass = QLineEdit()
        self.login_pass.setPlaceholderText("Şifre")
        self.login_pass.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Giriş Yap")
        login_btn.setObjectName("PrimaryBtn")
        login_btn.clicked.connect(self.do_login)

        nav_layout = QHBoxLayout()
        reg_btn = QPushButton("Kayıt Ol")
        reg_btn.setObjectName("SecondaryBtn")
        reg_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        forgot_btn = QPushButton("Şifremi Unuttum")
        forgot_btn.setObjectName("SecondaryBtn")
        forgot_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        nav_layout.addWidget(reg_btn)
        nav_layout.addWidget(forgot_btn)

        layout.addWidget(QLabel("Kullanıcı Adı:", objectName="FormLabel"))
        layout.addWidget(self.login_user)
        layout.addWidget(QLabel("Şifre:", objectName="FormLabel"))
        layout.addWidget(self.login_pass)
        layout.addSpacing(15)
        layout.addWidget(login_btn)
        layout.addSpacing(8)
        layout.addLayout(nav_layout)
        layout.addStretch()

        self.stack.addWidget(widget)

    def init_register_ui(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.reg_user = QLineEdit()
        self.reg_pass = QLineEdit()
        self.reg_pass.setEchoMode(QLineEdit.Password)
        self.reg_pass_conf = QLineEdit()
        self.reg_pass_conf.setEchoMode(QLineEdit.Password)
        
        self.reg_q = QComboBox()
        self.reg_q.addItems([
            "İlk evcil hayvanınızın adı nedir?",
            "İlkokul öğretmeninizin soyadı nedir?",
            "Çocukluk lakabınız neydi?",
            "Doğduğunuz şehir neresidir?"
        ])
        self.reg_ans = QLineEdit()

        reg_btn = QPushButton("Kayıt İşlemini Tamamla")
        reg_btn.setObjectName("PrimaryBtn")
        reg_btn.clicked.connect(self.do_register)

        back_btn = QPushButton("Giriş Ekranına Dön")
        back_btn.setObjectName("SecondaryBtn")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(QLabel("Yeni Kullanıcı Adı:", objectName="FormLabel"))
        layout.addWidget(self.reg_user)
        layout.addWidget(QLabel("Şifre:", objectName="FormLabel"))
        layout.addWidget(self.reg_pass)
        layout.addWidget(QLabel("Şifre Tekrar:", objectName="FormLabel"))
        layout.addWidget(self.reg_pass_conf)
        layout.addWidget(QLabel("Güvenlik Sorusu:", objectName="FormLabel"))
        layout.addWidget(self.reg_q)
        layout.addWidget(QLabel("Cevap:", objectName="FormLabel"))
        layout.addWidget(self.reg_ans)
        
        layout.addSpacing(15)
        layout.addWidget(reg_btn)
        layout.addWidget(back_btn)
        layout.addStretch()

        self.stack.addWidget(widget)

    def init_forgot_ui(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.f_user = QLineEdit()
        self.f_user.setPlaceholderText("Kullanıcı Adınızı Girin")
        
        self.f_q_label = QLabel("Kullanıcı bulunduğunda güvenlik sorusu burada çıkacak.", objectName="FormLabel")
        self.f_q_label.setWordWrap(True)
        self.f_q_label.setStyleSheet("color: #f59e0b;")
        
        self.f_ans = QLineEdit()
        self.f_ans.setPlaceholderText("Güvenlik Sorusu Cevabı")
        self.f_ans.setEnabled(False)

        self.f_new_pass = QLineEdit()
        self.f_new_pass.setPlaceholderText("Yeni Şifre")
        self.f_new_pass.setEchoMode(QLineEdit.Password)
        self.f_new_pass.setEnabled(False)

        self.check_user_btn = QPushButton("Kullanıcıyı Bul")
        self.check_user_btn.setObjectName("SecondaryBtn")
        self.check_user_btn.clicked.connect(self.do_check_user)

        self.reset_btn = QPushButton("Şifreyi Sıfırla")
        self.reset_btn.setObjectName("PrimaryBtn")
        self.reset_btn.setEnabled(False)
        self.reset_btn.clicked.connect(self.do_reset)

        back_btn = QPushButton("Giriş Ekranına Dön")
        back_btn.setObjectName("SecondaryBtn")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(QLabel("Kullanıcı Adı:", objectName="FormLabel"))
        user_h = QHBoxLayout()
        user_h.addWidget(self.f_user)
        user_h.addWidget(self.check_user_btn)
        layout.addLayout(user_h)

        layout.addSpacing(8)
        layout.addWidget(self.f_q_label)
        layout.addWidget(self.f_ans)
        layout.addWidget(QLabel("Yeni Şifreniz:", objectName="FormLabel"))
        layout.addWidget(self.f_new_pass)
        
        layout.addSpacing(15)
        layout.addWidget(self.reset_btn)
        layout.addWidget(back_btn)
        layout.addStretch()

        self.stack.addWidget(widget)

    def hash_str(self, s):
        return hashlib.sha256(s.encode('utf-8')).hexdigest()

    def do_login(self):
        u = self.login_user.text().strip()
        p = self.login_pass.text().strip()
        if not u or not p:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return

        user_data = self.db.get_user(u)
        if user_data:
            db_hash = user_data[2]
            if db_hash == self.hash_str(p):
                self.open_main_app(u)
                return

        QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre hatalı!")

    def do_register(self):
        u = self.reg_user.text().strip()
        p = self.reg_pass.text().strip()
        pc = self.reg_pass_conf.text().strip()
        q = self.reg_q.currentText()
        a = self.reg_ans.text().strip().lower()

        if not u or not p or not pc or not a:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return
        
        if p != pc:
            QMessageBox.warning(self, "Hata", "Şifreler eşleşmiyor!")
            return

        if len(p) < 4:
            QMessageBox.warning(self, "Hata", "Şifre en az 4 karakter olmalıdır.")
            return

        success = self.db.add_user(u, self.hash_str(p), q, self.hash_str(a))
        if success:
            QMessageBox.information(self, "Başarılı", "Kayıt işlemi tamamlandı. Giriş yapabilirsiniz.")
            self.reg_user.clear(); self.reg_pass.clear(); self.reg_pass_conf.clear(); self.reg_ans.clear()
            self.stack.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Hata", "Bu kullanıcı adı zaten alınmış!")

    def do_check_user(self):
        u = self.f_user.text().strip()
        if not u:
            return
        
        user_data = self.db.get_user(u)
        if user_data:
            self.f_q_label.setText(user_data[3])
            self.f_q_label.setStyleSheet("color: #10b981;")
            self.f_ans.setEnabled(True)
            self.f_new_pass.setEnabled(True)
            self.reset_btn.setEnabled(True)
            self.f_user.setEnabled(False)
            self.check_user_btn.setEnabled(False)
            self.forgot_target_user = u
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı bulunamadı!")

    def do_reset(self):
        a = self.f_ans.text().strip().lower()
        np = self.f_new_pass.text().strip()
        
        if not a or not np:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return

        if len(np) < 4:
            QMessageBox.warning(self, "Hata", "Yeni şifre en az 4 karakter olmalıdır.")
            return

        user_data = self.db.get_user(self.forgot_target_user)
        if user_data and user_data[4] == self.hash_str(a):
            self.db.update_user_password(self.forgot_target_user, self.hash_str(np))
            QMessageBox.information(self, "Başarılı", "Şifreniz başarıyla sıfırlandı. Giriş yapabilirsiniz.")
            
            # Reset UI
            self.f_user.clear()
            self.f_ans.clear()
            self.f_new_pass.clear()
            self.f_user.setEnabled(True)
            self.check_user_btn.setEnabled(True)
            self.f_ans.setEnabled(False)
            self.f_new_pass.setEnabled(False)
            self.reset_btn.setEnabled(False)
            self.f_q_label.setText("Kullanıcı bulunduğunda güvenlik sorusu burada çıkacak.")
            self.f_q_label.setStyleSheet("color: #f59e0b;")
            self.stack.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Hata", "Güvenlik sorusunun cevabı yanlış!")

    def open_main_app(self, username):
        save_session(username)
        self.main_window = MainWindow(username)
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Check for existing session
    saved_user = load_session()
    if saved_user:
        db_check = Database()
        if db_check.get_user(saved_user):
            window = MainWindow(saved_user)
            window.show()
        else:
            clear_session()
            window = AuthWindow()
            window.show()
    else:
        window = AuthWindow()
        window.show()

    sys.exit(app.exec_())
