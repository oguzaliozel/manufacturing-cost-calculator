# QSS (Qt Style Sheets) — Ultra-Premium Light & Dark Theme

def get_styles(dark=True):
    if dark:
        bg        = "#081120"   # Ana arka plan — derin lacivert
        bg2       = "#0a1628"   # Hafif daha açık bg
        card      = "#111C33"   # Kart yüzeyi
        card2     = "#162040"   # Hover/accent kart
        sidebar   = "#0c1832"   # Sidebar
        border    = "#1e3a5f"   # Çerçeve
        border2   = "#2a5080"   # Parlak çerçeve
        text      = "#EAF4FF"   # Ana metin
        sub_text  = "#7ba7cc"   # İkincil metin
        input_bg  = "#162040"   # Input alanı
        combo_bg  = "#111C33"
        accent    = "#00AFFF"   # Primary elektrik mavi
        accent2   = "#00D1FF"   # Secondary parlak mavi
        act_btn   = "#0088cc"
        act_hov   = "#0099ee"
        sec_btn   = "#1e3a5f"
        sec_text  = "#EAF4FF"
        logout_c  = "#ff4d6d"
        logout_b  = "#3d0020"
        tab_c     = "#7ba7cc"
        success   = "#00e5a0"
        warning   = "#ffb020"
        danger    = "#ff4d6d"
        muted     = "#2a4a6b"
        glow      = "rgba(0,175,255,0.15)"
        row_alt   = "#0f1f38"
    else:
        bg        = "#F5F1EA"   # Ana arka plan — sıcak krem
        bg2       = "#EDE8DF"
        card      = "#FFFDF9"   # Kart — krem beyaz
        card2     = "#F0EBE1"
        sidebar   = "#ECE5DB"   # Sidebar — açık kahve
        border    = "#D8CCBC"   # Çerçeve
        border2   = "#C8A97E"   # Altın vurgu
        text      = "#2B2B2B"   # Ana metin
        sub_text  = "#6B6B6B"   # İkincil metin
        input_bg  = "#FFFDF9"
        combo_bg  = "#FFFDF9"
        accent    = "#8B5E3C"   # Ana kahve
        accent2   = "#C8A97E"   # Altın
        act_btn   = "#8B5E3C"
        act_hov   = "#A47148"
        sec_btn   = "#ECE5DB"
        sec_text  = "#2B2B2B"
        logout_c  = "#C14953"
        logout_b  = "#F9E5E6"
        tab_c     = "#6B6B6B"
        success   = "#4F8A5B"
        warning   = "#B07D2A"
        danger    = "#C14953"
        muted     = "#C8BEAF"
        glow      = "rgba(139,94,60,0.08)"
        row_alt   = "#F7F3EE"

    return f"""
/* ═══════════════════════════════════
   GLOBAL BASE
   ═══════════════════════════════════ */
QMainWindow {{
    background-color: {bg};
}}

QWidget {{
    color: {text};
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
    background-color: {bg};
}}

QDialog {{
    background-color: {card};
    border: 1px solid {border};
    border-radius: 12px;
}}

/* ═══════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════ */
#Sidebar {{
    background-color: {sidebar};
    border-right: 1px solid {border};
    min-width: 240px;
    max-width: 240px;
}}

#SidebarLogo {{
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 1.5px;
    padding: 20px 16px 18px 16px;
    color: {accent};
    border-bottom: 1px solid {border};
    background-color: {sidebar};
    text-transform: uppercase;
}}

#SidebarSection {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: {sub_text};
    padding: 12px 16px 4px 16px;
    background-color: transparent;
    text-transform: uppercase;
}}

QPushButton#SidebarBtn {{
    background-color: transparent;
    border: none;
    padding: 10px 14px;
    text-align: left;
    border-radius: 8px;
    margin: 1px 8px;
    font-weight: 500;
    font-size: 13px;
    color: {sub_text};
}}

QPushButton#SidebarBtn:hover {{
    background-color: {card2};
    color: {text};
}}

QPushButton#SidebarBtn[active="true"] {{
    background-color: {accent};
    color: white;
    font-weight: 600;
}}

#SidebarFooter {{
    border-top: 1px solid {border};
    background-color: {sidebar};
    padding: 8px;
}}

#UserInfoLabel {{
    font-size: 12px;
    font-weight: 600;
    color: {text};
    background-color: transparent;
}}

#UserRoleLabel {{
    font-size: 10px;
    color: {sub_text};
    background-color: transparent;
}}

#AvatarBadge {{
    background-color: {accent};
    color: white;
    border-radius: 16px;
    font-weight: 700;
    font-size: 12px;
    min-width: 32px;
    min-height: 32px;
    max-width: 32px;
    max-height: 32px;
}}

QPushButton#LogoutBtn {{
    background-color: transparent;
    color: {logout_c};
    border: 1px solid {logout_b};
    border-radius: 6px;
    padding: 7px 12px;
    font-weight: 600;
    font-size: 12px;
    text-align: left;
}}

QPushButton#LogoutBtn:hover {{
    background-color: {logout_b};
    color: {logout_c};
}}

QPushButton#ThemeToggleBtn {{
    background-color: transparent;
    border: 1px solid {border};
    border-radius: 6px;
    padding: 7px 12px;
    color: {sub_text};
    font-size: 12px;
    text-align: left;
}}

QPushButton#ThemeToggleBtn:hover {{
    background-color: {card2};
    color: {text};
}}

/* ═══════════════════════════════════
   TOP BAR
   ═══════════════════════════════════ */
#TopBar {{
    background-color: {card};
    border-bottom: 1px solid {border};
    min-height: 56px;
    max-height: 56px;
}}

#SearchInput {{
    background-color: {bg};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 8px 12px 8px 36px;
    color: {text};
    font-size: 13px;
    min-width: 280px;
    max-width: 280px;
}}

#SearchInput:focus {{
    border-color: {accent};
    background-color: {input_bg};
}}

#TopIconBtn {{
    background-color: transparent;
    border: none;
    font-size: 16px;
    padding: 6px;
    border-radius: 8px;
    color: {sub_text};
    min-width: 32px;
    min-height: 32px;
    max-width: 32px;
    max-height: 32px;
}}

#TopIconBtn:hover {{
    background-color: {bg};
    color: {text};
}}

#ClockLabel {{
    font-size: 12px;
    font-weight: 600;
    color: {sub_text};
    background-color: transparent;
    padding: 0 8px;
}}

#SyncBadge {{
    background-color: transparent;
    font-size: 10px;
    color: {success};
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid {success};
}}

#NotifBadge {{
    background-color: {danger};
    color: white;
    border-radius: 8px;
    font-size: 9px;
    font-weight: 700;
    min-width: 16px;
    max-width: 16px;
    min-height: 16px;
    max-height: 16px;
    padding: 0;
}}

/* ═══════════════════════════════════
   CONTENT AREA
   ═══════════════════════════════════ */
#ContentArea {{
    background-color: {bg};
}}

#PageHeader {{
    font-size: 22px;
    font-weight: 700;
    color: {text};
    background-color: transparent;
    letter-spacing: -0.3px;
}}

#PageSub {{
    font-size: 13px;
    color: {sub_text};
    background-color: transparent;
}}

/* ═══════════════════════════════════
   CARDS
   ═══════════════════════════════════ */
#Card {{
    background-color: {card};
    border: 1px solid {border};
    border-radius: 12px;
}}

#CardHeader {{
    font-size: 13px;
    font-weight: 700;
    color: {text};
    background-color: transparent;
    letter-spacing: 0.2px;
}}

#CardSub {{
    font-size: 11px;
    color: {sub_text};
    background-color: transparent;
}}

/* KPI STAT CARDS */
#StatCard {{
    background-color: {card};
    border: 1px solid {border};
    border-radius: 14px;
    padding: 4px;
}}

#StatCard:hover {{
    border-color: {border2};
    background-color: {card2};
}}

#StatTitle {{
    color: {sub_text};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    background-color: transparent;
    text-transform: uppercase;
}}

#StatValue {{
    color: {text};
    font-size: 26px;
    font-weight: 700;
    background-color: transparent;
    letter-spacing: -0.5px;
}}

#StatTrend {{
    font-size: 11px;
    font-weight: 600;
    background-color: transparent;
}}

#LiveDot {{
    background-color: {success};
    border-radius: 4px;
    min-width: 8px;
    max-width: 8px;
    min-height: 8px;
    max-height: 8px;
}}

#LiveLabel {{
    font-size: 10px;
    font-weight: 600;
    color: {success};
    background-color: transparent;
    letter-spacing: 0.5px;
}}

/* ═══════════════════════════════════
   TABLES
   ═══════════════════════════════════ */
QTableWidget {{
    background-color: {card};
    border: 1px solid {border};
    border-radius: 10px;
    color: {text};
    gridline-color: transparent;
    outline: none;
}}

QTableWidget::item {{
    padding: 10px 12px;
    color: {text};
    border-bottom: 1px solid {border};
    background-color: transparent;
}}

QTableWidget::item:alternate {{
    background-color: {row_alt};
}}

QTableWidget::item:selected {{
    background-color: {glow};
    color: {text};
}}

QTableWidget::item:hover {{
    background-color: {card2};
}}

QHeaderView::section {{
    background-color: {card};
    color: {sub_text};
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid {border};
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

QHeaderView {{
    background-color: {card};
}}

/* ═══════════════════════════════════
   FORM INPUTS
   ═══════════════════════════════════ */
QLineEdit, QDoubleSpinBox, QSpinBox {{
    background-color: {input_bg};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 9px 13px;
    color: {text};
    font-size: 13px;
    selection-background-color: {accent};
}}

QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
    border: 1.5px solid {accent};
    background-color: {card};
}}

QLineEdit:hover, QDoubleSpinBox:hover {{
    border-color: {border2};
}}

QComboBox {{
    background-color: {input_bg};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 9px 13px;
    color: {text};
    font-size: 13px;
}}

QComboBox:focus {{
    border: 1.5px solid {accent};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    width: 10px;
    height: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {combo_bg};
    color: {text};
    selection-background-color: {accent};
    border: 1px solid {border};
    outline: none;
    padding: 4px;
}}

QLabel#FormLabel {{
    color: {sub_text};
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    background-color: transparent;
    margin-top: 6px;
}}

QTextEdit {{
    background-color: {input_bg};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 8px 12px;
    color: {text};
}}

QTextEdit:focus {{
    border-color: {accent};
}}

/* ═══════════════════════════════════
   BUTTONS
   ═══════════════════════════════════ */
QPushButton#PrimaryBtn {{
    background-color: {act_btn};
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 13px;
    border: none;
    letter-spacing: 0.3px;
}}

QPushButton#PrimaryBtn:hover {{
    background-color: {act_hov};
}}

QPushButton#PrimaryBtn:pressed {{
    background-color: {act_btn};
}}

QPushButton#SecondaryBtn {{
    background-color: {sec_btn};
    color: {sec_text};
    border-radius: 8px;
    padding: 9px 16px;
    border: 1px solid {border};
    font-size: 13px;
    font-weight: 500;
}}

QPushButton#SecondaryBtn:hover {{
    border-color: {border2};
    background-color: {card2};
}}

QPushButton#DangerBtn {{
    background-color: transparent;
    color: {danger};
    border: 1px solid {danger};
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton#DangerBtn:hover {{
    background-color: {logout_b};
}}

QPushButton#IconBtn {{
    background-color: transparent;
    border: 1px solid {border};
    border-radius: 6px;
    padding: 6px 10px;
    color: {sub_text};
    font-size: 12px;
}}

QPushButton#IconBtn:hover {{
    background-color: {card2};
    color: {text};
    border-color: {border2};
}}

QPushButton#SuccessBtn {{
    background-color: transparent;
    color: {success};
    border: 1px solid {success};
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 600;
}}

QPushButton#SuccessBtn:hover {{
    background-color: {success};
    color: white;
}}

/* ═══════════════════════════════════
   SCROLLBARS
   ═══════════════════════════════════ */
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {muted};
    border-radius: 3px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {sub_text};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 5px;
}}

QScrollBar::handle:horizontal {{
    background: {muted};
    border-radius: 3px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ═══════════════════════════════════
   TABS
   ═══════════════════════════════════ */
QTabWidget::pane {{
    border: none;
    background-color: transparent;
}}

QTabBar::tab {{
    background: transparent;
    padding: 8px 18px;
    color: {tab_c};
    font-weight: 500;
    font-size: 13px;
    border-bottom: 2px solid transparent;
    margin-right: 4px;
}}

QTabBar::tab:selected {{
    color: {accent};
    border-bottom: 2px solid {accent};
    font-weight: 700;
}}

QTabBar::tab:hover {{
    color: {text};
}}

/* ═══════════════════════════════════
   CALENDAR
   ═══════════════════════════════════ */
#CalDayBtn {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 4px;
    color: {text};
    font-size: 12px;
    font-weight: 500;
    min-width: 44px;
    max-width: 44px;
    min-height: 44px;
    max-height: 44px;
    text-align: center;
}}

#CalDayBtn:hover {{
    background-color: {card2};
    border-color: {border};
}}

#CalDayBtn[today="true"] {{
    background-color: {accent};
    color: white;
    font-weight: 700;
    border-color: transparent;
}}

#CalDayBtn[hasEvent="true"] {{
    border-color: {accent2};
    color: {text};
    font-weight: 600;
}}

#CalDayBtn[today="true"][hasEvent="true"] {{
    background-color: {accent};
    color: white;
}}

#CalDayHeader {{
    font-size: 11px;
    font-weight: 700;
    color: {sub_text};
    background-color: transparent;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    text-align: center;
    min-width: 44px;
    max-width: 44px;
    padding: 4px 0;
}}

#CalNavBtn {{
    background-color: transparent;
    border: 1px solid {border};
    border-radius: 6px;
    padding: 5px 10px;
    color: {sub_text};
    font-size: 14px;
    min-width: 30px;
    max-width: 30px;
}}

#CalNavBtn:hover {{
    background-color: {card2};
    color: {text};
}}

#CalMonthLabel {{
    font-size: 16px;
    font-weight: 700;
    color: {text};
    background-color: transparent;
}}

/* ═══════════════════════════════════
   MISC
   ═══════════════════════════════════ */
QFrame#Divider {{
    background-color: {border};
    max-height: 1px;
    min-height: 1px;
}}

#StatusOnline {{
    background-color: {success};
    border-radius: 4px;
    min-width: 8px;
    max-width: 8px;
    min-height: 8px;
    max-height: 8px;
}}

QMessageBox {{
    background-color: {card};
}}

QMessageBox QLabel {{
    color: {text};
    background-color: transparent;
}}

QMessageBox QPushButton {{
    background-color: {act_btn};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 600;
    min-width: 80px;
}}

QMessageBox QPushButton:hover {{
    background-color: {act_hov};
}}
"""

STYLES = get_styles(dark=True)
