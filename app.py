import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# --- 1. VERİTABANI KURULUMU ---
def init_db():
    db_exists = os.path.exists('imalat_motoru.db')
    conn = sqlite3.connect('imalat_motoru.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Stok_Hammadde (
        id INTEGER PRIMARY KEY AUTOINCREMENT, malzeme_adi TEXT, kategori TEXT, 
        birim TEXT, birim_fiyat REAL, fire_yuzdesi REAL, hurda_kilo_fiyati REAL)''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS Islem_Maliyetleri (
        id INTEGER PRIMARY KEY AUTOINCREMENT, islem_adi TEXT, hesap_tipi TEXT, birim_maliyet REAL)''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS Teklifler (
        id INTEGER PRIMARY KEY AUTOINCREMENT, musteri_adi TEXT, proje_adi TEXT, 
        toplam_malzeme_maliyeti REAL, toplam_islem_maliyeti REAL, kar_marji REAL, 
        net_uretim_kari REAL, tahmini_hurda_degeri REAL, sunulan_fiyat REAL, durum TEXT, tarih TEXT)''')
    
    if not db_exists:
        # İlk kurulumda test verileri
        cursor.execute("INSERT INTO Stok_Hammadde (malzeme_adi, kategori, birim, birim_fiyat, fire_yuzdesi, hurda_kilo_fiyati) VALUES ('Alüminyum 7075 Kütük', 'Metal', 'KG', 250, 15, 45)")
        cursor.execute("INSERT INTO Stok_Hammadde (malzeme_adi, kategori, birim, birim_fiyat, fire_yuzdesi, hurda_kilo_fiyati) VALUES ('Çelik Sac 3mm', 'Metal', 'KG', 40, 20, 12)")
        cursor.execute("INSERT INTO Islem_Maliyetleri (islem_adi, hesap_tipi, birim_maliyet) VALUES ('3 Eksen CNC İşleme', 'Saat', 600)")
        cursor.execute("INSERT INTO Islem_Maliyetleri (islem_adi, hesap_tipi, birim_maliyet) VALUES ('Lazer Kesim', 'Saat', 800)")
    
    conn.commit()
    conn.close()

# --- 2. ANA UYGULAMA SINIFI ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ImalatUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Akıllı Teklif ve Maliyet Motoru")
        self.geometry("1100x750")
        
        # Grid Yapısı (Sol menü ve sağ içerik)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SOL MENÜ (Sidebar) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MALİYET MOTORU", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_malzeme = ctk.CTkButton(self.sidebar_frame, text="Malzeme Veritabanı", command=self.show_malzeme)
        self.btn_malzeme.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_islem = ctk.CTkButton(self.sidebar_frame, text="İşlem Maliyetleri", command=self.show_islem)
        self.btn_islem.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_teklif = ctk.CTkButton(self.sidebar_frame, text="Yeni Teklif Sihirbazı", command=self.show_teklif)
        self.btn_teklif.grid(row=4, column=0, padx=20, pady=10)
        
        self.btn_gecmis = ctk.CTkButton(self.sidebar_frame, text="Geçmiş Teklifler", command=self.show_gecmis)
        self.btn_gecmis.grid(row=5, column=0, padx=20, pady=10)

        # --- SAĞ İÇERİK ALANI (Frames) ---
        self.frames = {}
        
        self.frames["Dashboard"] = ctk.CTkFrame(self, corner_radius=10)
        self.frames["Malzeme"] = ctk.CTkFrame(self, corner_radius=10)
        self.frames["Islem"] = ctk.CTkFrame(self, corner_radius=10)
        self.frames["Teklif"] = ctk.CTkFrame(self, corner_radius=10)
        self.frames["Gecmis"] = ctk.CTkFrame(self, corner_radius=10)

        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.setup_dashboard()
        self.setup_malzeme_ekrani()
        self.setup_islem_ekrani()
        self.setup_teklif_sihirbazi()
        self.setup_gecmis()
        
        self.show_dashboard()

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

    def show_dashboard(self): 
        self.load_dashboard_data()
        self.show_frame("Dashboard")
    def show_malzeme(self): 
        self.load_malzeme_data()
        self.show_frame("Malzeme")
    def show_islem(self): 
        self.load_islem_data()
        self.show_frame("Islem")
    def show_teklif(self):
        self.load_combobox_data()
        self.show_frame("Teklif")
    def show_gecmis(self):
        self.load_gecmis_data()
        self.show_frame("Gecmis")

    # --- DASHBOARD TASARIMI ---
    def setup_dashboard(self):
        f = self.frames["Dashboard"]
        
        # Üst Başlık
        header_frame = ctk.CTkFrame(f, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(header_frame, text="İşletme Özeti ve Genel Durum", font=("Arial", 24, "bold")).pack(side="left")

        # 1. KPI Kartları Bölümü (Üst Kısım)
        self.kpi_frame = ctk.CTkFrame(f, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=20, pady=10)
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Kart değişkenleri
        self.lbl_bekleyen_sayi = ctk.CTkLabel(self.create_kpi_card(self.kpi_frame, 0, "Bekleyen Teklifler", "#f39c12"), text="0", font=("Arial", 24, "bold"))
        self.lbl_bekleyen_sayi.pack(pady=10)
        
        self.lbl_onaylanan_hacim = ctk.CTkLabel(self.create_kpi_card(self.kpi_frame, 1, "Toplam Ciro (Onaylanan)", "#2980b9"), text="0 TL", font=("Arial", 20, "bold"))
        self.lbl_onaylanan_hacim.pack(pady=10)

        self.lbl_net_kar = ctk.CTkLabel(self.create_kpi_card(self.kpi_frame, 2, "Net Üretim Karı", "#27ae60"), text="0 TL", font=("Arial", 20, "bold"))
        self.lbl_net_kar.pack(pady=10)

        self.lbl_hurda_degeri = ctk.CTkLabel(self.create_kpi_card(self.kpi_frame, 3, "Toplam Hurda Değeri", "#8e44ad"), text="0 TL", font=("Arial", 20, "bold"))
        self.lbl_hurda_degeri.pack(pady=10)

        # 2. Grafikler Bölümü (Alt Kısım)
        self.charts_frame = ctk.CTkFrame(f, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.charts_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.pie_chart_frame = ctk.CTkFrame(self.charts_frame)
        self.pie_chart_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.bar_chart_frame = ctk.CTkFrame(self.charts_frame)
        self.bar_chart_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.canvas_pie = None
        self.canvas_bar = None

    def create_kpi_card(self, parent, col, title, color):
        card = ctk.CTkFrame(parent, corner_radius=10, border_width=2, border_color=color)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=("Arial", 14), text_color=color).pack(pady=(10, 0))
        return card

    def load_dashboard_data(self):
        conn = sqlite3.connect('imalat_motoru.db')
        cursor = conn.cursor()
        
        # KPI Verilerini Çek
        cursor.execute("SELECT COUNT(*) FROM Teklifler WHERE durum='Bekliyor'")
        bekleyen = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(sunulan_fiyat), SUM(net_uretim_kari), SUM(tahmini_hurda_degeri) FROM Teklifler WHERE durum='Onaylandı'")
        onayli_veriler = cursor.fetchone()
        
        ciro = onayli_veriler[0] if onayli_veriler[0] else 0
        net_kar = onayli_veriler[1] if onayli_veriler[1] else 0
        hurda = onayli_veriler[2] if onayli_veriler[2] else 0
        
        # UI Güncelle
        self.lbl_bekleyen_sayi.configure(text="0")
        self.lbl_onaylanan_hacim.configure(text="0.00 TL")
        self.lbl_net_kar.configure(text="0.00 TL")
        self.lbl_hurda_degeri.configure(text="0.00 TL")
        
        self.animate_numbers(0, bekleyen, self.lbl_bekleyen_sayi, is_integer=True)
        self.animate_numbers(0, ciro, self.lbl_onaylanan_hacim)
        self.animate_numbers(0, net_kar, self.lbl_net_kar)
        self.animate_numbers(0, hurda, self.lbl_hurda_degeri)
        
        # Grafik Verilerini Çek
        cursor.execute("SELECT durum, COUNT(*) FROM Teklifler GROUP BY durum")
        durumlar = cursor.fetchall()
        
        cursor.execute("SELECT proje_adi, net_uretim_kari FROM Teklifler WHERE durum='Onaylandı' ORDER BY id DESC LIMIT 5")
        son_karlar = cursor.fetchall()
        
        conn.close()
        
        self.draw_pie_chart(durumlar)
        self.draw_bar_chart(son_karlar)

    def draw_pie_chart(self, veriler):
        if self.canvas_pie:
            self.canvas_pie.get_tk_widget().destroy()
            
        fig = Figure(figsize=(4, 3), dpi=100)
        fig.patch.set_facecolor('#2b2b2b') # Dark mode arkaplan
        ax = fig.add_subplot(111)
        
        if not veriler:
            ax.text(0.5, 0.5, "Henüz Veri Yok", ha='center', va='center', color='white')
        else:
            labels = [v[0] for v in veriler]
            sizes = [v[1] for v in veriler]
            colors = ['#f39c12' if l=='Bekliyor' else '#27ae60' if l=='Onaylandı' else '#e74c3c' for l in labels]
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            for text in texts + autotexts:
                text.set_color('white')
            
            ax.axis('equal')
            ax.set_title("Teklif Durumları", color='white', pad=10)

        self.canvas_pie = FigureCanvasTkAgg(fig, master=self.pie_chart_frame)
        self.canvas_pie.draw()
        self.canvas_pie.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def draw_bar_chart(self, veriler):
        if self.canvas_bar:
            self.canvas_bar.get_tk_widget().destroy()
            
        fig = Figure(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')
        
        if not veriler:
            ax.text(0.5, 0.5, "Henüz Onaylanan İş Yok", ha='center', va='center', color='white')
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            projeler = [v[0][:10] + '..' if len(v[0]) > 10 else v[0] for v in veriler] # İsimleri kısalt
            karlar = [v[1] for v in veriler]
            
            bars = ax.bar(projeler, karlar, color='#3498db')
            ax.set_title("Son 5 İş - Net Kar", color='white', pad=10)
            ax.tick_params(axis='x', colors='white', rotation=45)
            ax.tick_params(axis='y', colors='white')
            
            # Değerleri bar üstüne yaz
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval, f'{int(yval)}', ha='center', va='bottom', color='white', fontsize=8)

        fig.tight_layout()
        self.canvas_bar = FigureCanvasTkAgg(fig, master=self.bar_chart_frame)
        self.canvas_bar.draw()
        self.canvas_bar.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    # --- MALZEME VERİTABANI TASARIMI ---
    def setup_malzeme_ekrani(self):
        f = self.frames["Malzeme"]
        ctk.CTkLabel(f, text="Hammadde Veritabanı", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Form Alanı
        form_frame = ctk.CTkFrame(f, fg_color="transparent")
        form_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(form_frame, text="Malzeme Adı:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.ent_malz_adi = ctk.CTkEntry(form_frame, width=150)
        self.ent_malz_adi.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Kategori:").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.ent_malz_kat = ctk.CTkEntry(form_frame, width=150)
        self.ent_malz_kat.grid(row=0, column=3, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Birim (KG, Adet vb):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.ent_malz_birim = ctk.CTkEntry(form_frame, width=150)
        self.ent_malz_birim.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Birim Fiyatı (TL):").grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.ent_malz_fiyat = ctk.CTkEntry(form_frame, width=150)
        self.ent_malz_fiyat.grid(row=1, column=3, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Fire Yüzdesi (%):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.ent_malz_fire = ctk.CTkEntry(form_frame, width=150)
        self.ent_malz_fire.grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Hurda Değeri (TL/Birim):").grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.ent_malz_hurda = ctk.CTkEntry(form_frame, width=150)
        self.ent_malz_hurda.grid(row=2, column=3, padx=10, pady=5)

        ctk.CTkButton(form_frame, text="Malzemeyi Ekle", fg_color="green", command=self.malzeme_ekle).grid(row=3, column=0, columnspan=4, pady=15)

        # Tablo Alanı
        columns = ("ID", "Malzeme", "Kategori", "Birim", "Fiyat", "Fire %", "Hurda Değeri")
        self.tree_malzeme = ttk.Treeview(f, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree_malzeme.heading(col, text=col)
            self.tree_malzeme.column(col, width=100, anchor="center")
        self.tree_malzeme.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

    def malzeme_ekle(self):
        try:
            adi = self.ent_malz_adi.get()
            kat = self.ent_malz_kat.get()
            birim = self.ent_malz_birim.get()
            fiyat = float(self.ent_malz_fiyat.get())
            fire = float(self.ent_malz_fire.get())
            hurda = float(self.ent_malz_hurda.get())

            if not adi or not birim:
                messagebox.showwarning("Uyarı", "Malzeme Adı ve Birim boş bırakılamaz.")
                return

            conn = sqlite3.connect('imalat_motoru.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Stok_Hammadde (malzeme_adi, kategori, birim, birim_fiyat, fire_yuzdesi, hurda_kilo_fiyati) VALUES (?, ?, ?, ?, ?, ?)", 
                           (adi, kat, birim, fiyat, fire, hurda))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarılı", "Malzeme veritabanına eklendi.")
            self.load_malzeme_data()
            
            # Girdileri Temizle
            for ent in (self.ent_malz_adi, self.ent_malz_kat, self.ent_malz_birim, self.ent_malz_fiyat, self.ent_malz_fire, self.ent_malz_hurda):
                ent.delete(0, 'end')

        except ValueError:
            messagebox.showerror("Hata", "Fiyat ve Fire değerleri sayısal olmalıdır.")

    def load_malzeme_data(self):
        for item in self.tree_malzeme.get_children():
            self.tree_malzeme.delete(item)
        conn = sqlite3.connect('imalat_motoru.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Stok_Hammadde")
        for row in cursor.fetchall():
            formatted_row = (row[0], row[1], row[2], row[3], f"{row[4]:.2f} TL", f"%{row[5]:.1f}", f"{row[6]:.2f} TL")
            self.tree_malzeme.insert("", "end", values=formatted_row)
        conn.close()

    # --- İŞLEM MALİYETLERİ EKRANI TASARIMI ---
    def setup_islem_ekrani(self):
        f = self.frames["Islem"]
        ctk.CTkLabel(f, text="Üretim/İşlem Maliyetleri", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Form Alanı
        form_frame = ctk.CTkFrame(f, fg_color="transparent")
        form_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(form_frame, text="İşlem Adı:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.ent_islem_adi = ctk.CTkEntry(form_frame, width=150)
        self.ent_islem_adi.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Hesap Tipi (Saat, Adet vb):").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.ent_islem_tipi = ctk.CTkEntry(form_frame, width=150)
        self.ent_islem_tipi.grid(row=0, column=3, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Birim Maliyeti (TL):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.ent_islem_maliyet = ctk.CTkEntry(form_frame, width=150)
        self.ent_islem_maliyet.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkButton(form_frame, text="İşlemi Ekle", fg_color="green", command=self.islem_ekle).grid(row=1, column=2, columnspan=2, pady=15, padx=20)

        # Tablo Alanı
        columns = ("ID", "İşlem Adı", "Hesap Tipi", "Birim Maliyeti (TL)")
        self.tree_islem = ttk.Treeview(f, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree_islem.heading(col, text=col)
            self.tree_islem.column(col, width=150, anchor="center")
        self.tree_islem.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

    def islem_ekle(self):
        try:
            adi = self.ent_islem_adi.get()
            tip = self.ent_islem_tipi.get()
            maliyet = float(self.ent_islem_maliyet.get())

            if not adi or not tip:
                messagebox.showwarning("Uyarı", "İşlem Adı ve Tipi boş bırakılamaz.")
                return

            conn = sqlite3.connect('imalat_motoru.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Islem_Maliyetleri (islem_adi, hesap_tipi, birim_maliyet) VALUES (?, ?, ?)", 
                           (adi, tip, maliyet))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarılı", "İşlem veritabanına eklendi.")
            self.load_islem_data()
            
            self.ent_islem_adi.delete(0, 'end')
            self.ent_islem_tipi.delete(0, 'end')
            self.ent_islem_maliyet.delete(0, 'end')

        except ValueError:
            messagebox.showerror("Hata", "Maliyet sayısal bir değer olmalıdır.")

    def load_islem_data(self):
        for item in self.tree_islem.get_children():
            self.tree_islem.delete(item)
        conn = sqlite3.connect('imalat_motoru.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Islem_Maliyetleri")
        for row in cursor.fetchall():
            formatted_row = (row[0], row[1], row[2], f"{row[3]:.2f} TL")
            self.tree_islem.insert("", "end", values=formatted_row)
        conn.close()


    # --- YENİ TEKLİF SİHİRBAZI (HESAPLAMA MOTORU) ---
    def setup_teklif_sihirbazi(self):
        f = self.frames["Teklif"]
        ctk.CTkLabel(f, text="Akıllı Teklif ve Maliyet Hesaplama", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=10, padx=20)

        # Müşteri Bilgileri
        ctk.CTkLabel(f, text="Müşteri Adı:").grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.entry_musteri = ctk.CTkEntry(f, width=200)
        self.entry_musteri.grid(row=1, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(f, text="Proje Adı:").grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.entry_proje = ctk.CTkEntry(f, width=200)
        self.entry_proje.grid(row=2, column=1, padx=20, pady=5, sticky="w")

        # Malzeme Seçimi
        ctk.CTkLabel(f, text="Kullanılacak Malzeme:").grid(row=3, column=0, padx=20, pady=20, sticky="w")
        self.combo_malzeme = ctk.CTkComboBox(f, width=200, values=[])
        self.combo_malzeme.grid(row=3, column=1, padx=20, pady=20, sticky="w")
        
        ctk.CTkLabel(f, text="Brüt Miktar (Birim):").grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.entry_malzeme_miktar = ctk.CTkEntry(f, width=100)
        self.entry_malzeme_miktar.grid(row=4, column=1, padx=20, pady=5, sticky="w")

        # İşlem Seçimi
        ctk.CTkLabel(f, text="Uygulanacak İşlem:").grid(row=5, column=0, padx=20, pady=20, sticky="w")
        self.combo_islem = ctk.CTkComboBox(f, width=200, values=[])
        self.combo_islem.grid(row=5, column=1, padx=20, pady=20, sticky="w")

        ctk.CTkLabel(f, text="İşlem Süresi/Miktarı:").grid(row=6, column=0, padx=20, pady=5, sticky="w")
        self.entry_islem_miktar = ctk.CTkEntry(f, width=100)
        self.entry_islem_miktar.grid(row=6, column=1, padx=20, pady=5, sticky="w")

        # Kar Marjı
        ctk.CTkLabel(f, text="Hedeflenen Kar Marjı (%):").grid(row=7, column=0, padx=20, pady=20, sticky="w")
        self.entry_kar = ctk.CTkEntry(f, width=100)
        self.entry_kar.insert(0, "30") # Varsayılan %30
        self.entry_kar.grid(row=7, column=1, padx=20, pady=20, sticky="w")

        # Butonlar
        self.btn_hesapla = ctk.CTkButton(f, text="Maliyeti Hesapla", command=self.hesapla_ve_goster)
        self.btn_hesapla.grid(row=8, column=0, padx=20, pady=20)
        
        self.btn_kaydet = ctk.CTkButton(f, text="Teklifi Kaydet", command=self.teklif_kaydet, fg_color="green")
        self.btn_kaydet.grid(row=8, column=1, padx=20, pady=20, sticky="w")

        # Sonuç Ekranı (Animasyonlu Kartlar)
        self.result_frame = ctk.CTkFrame(f, fg_color="transparent")
        self.result_frame.grid(row=9, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.result_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.card_maliyet = ctk.CTkFrame(self.result_frame, corner_radius=10, border_width=2, border_color="#e74c3c")
        self.card_maliyet.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(self.card_maliyet, text="Toplam Maliyet", text_color="#e74c3c", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        self.lbl_anim_maliyet = ctk.CTkLabel(self.card_maliyet, text="0.00 TL", font=("Arial", 22, "bold"))
        self.lbl_anim_maliyet.pack(pady=10)

        self.card_kar = ctk.CTkFrame(self.result_frame, corner_radius=10, border_width=2, border_color="#2ecc71")
        self.card_kar.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(self.card_kar, text="Net Üretim Karı", text_color="#2ecc71", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        self.lbl_anim_kar = ctk.CTkLabel(self.card_kar, text="0.00 TL", font=("Arial", 22, "bold"))
        self.lbl_anim_kar.pack(pady=10)

        self.card_fiyat = ctk.CTkFrame(self.result_frame, corner_radius=10, border_width=2, border_color="#f1c40f")
        self.card_fiyat.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(self.card_fiyat, text="MÜŞTERİYE SUNULACAK FİYAT", text_color="#f1c40f", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        self.lbl_anim_fiyat = ctk.CTkLabel(self.card_fiyat, text="0.00 TL", font=("Arial", 26, "bold"), text_color="#f1c40f")
        self.lbl_anim_fiyat.pack(pady=10)

        # İlerleme Çubuğu (Progress Bar)
        self.progress_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.progress_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.progress_frame, text="Maliyet", text_color="#e74c3c").pack(side="left", padx=10)
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400, progress_color="#e74c3c", fg_color="#2ecc71")
        self.progress_bar.set(0.5)
        self.progress_bar.pack(side="left", padx=10)
        ctk.CTkLabel(self.progress_frame, text="Kar", text_color="#2ecc71").pack(side="left", padx=10)
        
        self.result_frame.grid_remove() # Başlangıçta gizle

    def load_combobox_data(self):
        conn = sqlite3.connect('imalat_motoru.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT malzeme_adi FROM Stok_Hammadde")
        malzemeler = [row[0] for row in cursor.fetchall()]
        self.combo_malzeme.configure(values=malzemeler)
        if malzemeler: self.combo_malzeme.set(malzemeler[0])
        
        cursor.execute("SELECT islem_adi FROM Islem_Maliyetleri")
        islemler = [row[0] for row in cursor.fetchall()]
        self.combo_islem.configure(values=islemler)
        if islemler: self.combo_islem.set(islemler[0])
        
        conn.close()

    def hesapla_ve_goster(self):
        try:
            secili_malzeme = self.combo_malzeme.get()
            malzeme_miktar = float(self.entry_malzeme_miktar.get())
            secili_islem = self.combo_islem.get()
            islem_miktar = float(self.entry_islem_miktar.get())
            kar_marji = float(self.entry_kar.get())

            conn = sqlite3.connect('imalat_motoru.db')
            cursor = conn.cursor()
            
            # Malzeme Verilerini Çek
            cursor.execute("SELECT birim_fiyat, fire_yuzdesi, hurda_kilo_fiyati FROM Stok_Hammadde WHERE malzeme_adi=?", (secili_malzeme,))
            m_fiyat, m_fire_yuzde, m_hurda_fiyat = cursor.fetchone()
            
            # İşlem Verilerini Çek
            cursor.execute("SELECT birim_maliyet FROM Islem_Maliyetleri WHERE islem_adi=?", (secili_islem,))
            i_maliyet = cursor.fetchone()[0]
            conn.close()

            # --- MATEMATİKSEL MOTOR ---
            toplam_malzeme_maliyeti = malzeme_miktar * m_fiyat
            fire_miktari = malzeme_miktar * (m_fire_yuzde / 100)
            self.tahmini_hurda_degeri = fire_miktari * m_hurda_fiyat
            
            toplam_islem_maliyeti = islem_miktar * i_maliyet
            ana_maliyet = toplam_malzeme_maliyeti + toplam_islem_maliyeti
            
            self.sunulan_fiyat = ana_maliyet * (1 + (kar_marji / 100))
            self.net_uretim_kari = self.sunulan_fiyat - ana_maliyet
            
            # Değerleri sınıf içinde tut (Kaydetmek için)
            self.hesaplanan_veri = {
                "toplam_malzeme": toplam_malzeme_maliyeti,
                "toplam_islem": toplam_islem_maliyeti,
                "kar_marji": kar_marji
            }

            self.result_frame.grid() # Sonuç ekranını göster
            
            # Progress bar oranını ayarla (maliyet / sunulan_fiyat)
            oran = ana_maliyet / self.sunulan_fiyat if self.sunulan_fiyat > 0 else 0
            self.progress_bar.set(oran)
            
            # Animasyon yok, doğrudan değerleri yazdır
            self.lbl_anim_maliyet.configure(text=f"{ana_maliyet:,.2f} TL")
            self.lbl_anim_kar.configure(text=f"{self.net_uretim_kari:,.2f} TL")
            self.lbl_anim_fiyat.configure(text=f"{self.sunulan_fiyat:,.2f} TL")

        except Exception as e:
            messagebox.showerror("Hata", "Lütfen tüm değerleri doğru formatta girin.")

    def animate_numbers(self, current_val, target_val, label_widget, is_integer=False):
        diff = target_val - current_val
        if diff <= (0.5 if is_integer else 0.01):
            if is_integer:
                label_widget.configure(text=f"{int(target_val)}")
            else:
                label_widget.configure(text=f"{target_val:,.2f} TL")
            return
            
        increment = target_val / 20.0
        new_val = current_val + increment
        
        if new_val >= target_val:
            if is_integer:
                label_widget.configure(text=f"{int(target_val)}")
            else:
                label_widget.configure(text=f"{target_val:,.2f} TL")
        else:
            if is_integer:
                label_widget.configure(text=f"{int(new_val)}")
            else:
                label_widget.configure(text=f"{new_val:,.2f} TL")
            self.after(25, self.animate_numbers, new_val, target_val, label_widget, is_integer)

    def teklif_kaydet(self):
        try:
            musteri = self.entry_musteri.get()
            proje = self.entry_proje.get()
            tarih = datetime.datetime.now().strftime("%Y-%m-%d")
            
            if not musteri or not proje:
                messagebox.showwarning("Uyarı", "Müşteri ve Proje adı boş bırakılamaz.")
                return

            conn = sqlite3.connect('imalat_motoru.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Teklifler 
                (musteri_adi, proje_adi, toplam_malzeme_maliyeti, toplam_islem_maliyeti, 
                kar_marji, net_uretim_kari, tahmini_hurda_degeri, sunulan_fiyat, durum, tarih) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                (musteri, proje, self.hesaplanan_veri["toplam_malzeme"], self.hesaplanan_veri["toplam_islem"],
                 self.hesaplanan_veri["kar_marji"], self.net_uretim_kari, self.tahmini_hurda_degeri, 
                 self.sunulan_fiyat, "Bekliyor", tarih))
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Teklif başarıyla veritabanına kaydedildi.")
            
            # Alanları temizle
            self.entry_musteri.delete(0, 'end')
            self.entry_proje.delete(0, 'end')
            self.result_frame.grid_remove() # Animasyonlu ekranı gizle
            
        except AttributeError:
            messagebox.showwarning("Uyarı", "Önce maliyeti hesaplamalısınız.")

    # --- GEÇMİŞ TEKLİFLER (FİNANSAL ANALİZ) ---
    def setup_gecmis(self):
        f = self.frames["Gecmis"]
        ctk.CTkLabel(f, text="Geçmiş Teklifler ve Hurda Analizi", font=("Arial", 20, "bold")).pack(pady=10)

        # Tkinter Treeview ile tablo oluşturma (CTk henüz tam tablo desteklemiyor)
        columns = ("ID", "Müşteri", "Proje", "Sunulan Fiyat", "Durum", "Üretim Karı", "Hurda Değeri")
        self.tree = ttk.Treeview(f, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        
        self.tree.pack(pady=20, fill="x", padx=20)

        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Seçili İşi 'Onaylandı' Yap", fg_color="green", command=lambda: self.durum_guncelle("Onaylandı")).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="Seçili İşi 'Reddedildi' Yap", fg_color="red", command=lambda: self.durum_guncelle("Reddedildi")).grid(row=0, column=1, padx=10)
        ctk.CTkButton(btn_frame, text="Seçili Teklifi Sil", fg_color="#555555", hover_color="#333333", command=self.teklif_sil).grid(row=0, column=2, padx=10)

    def load_gecmis_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.tree.tag_configure('onaylandi', background='#d4edda', foreground='black')
        self.tree.tag_configure('reddedildi', background='#f8d7da', foreground='black')
            
        conn = sqlite3.connect('imalat_motoru.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, musteri_adi, proje_adi, sunulan_fiyat, durum, net_uretim_kari, tahmini_hurda_degeri FROM Teklifler ORDER BY id DESC")
        rows = cursor.fetchall()
        
        for row in rows:
            formatted_row = (row[0], row[1], row[2], f"{row[3]:.2f} TL", row[4], f"{row[5]:.2f} TL", f"{row[6]:.2f} TL")
            if row[4] == "Onaylandı":
                self.tree.insert("", "end", values=formatted_row, tags=('onaylandi',))
            elif row[4] == "Reddedildi":
                self.tree.insert("", "end", values=formatted_row, tags=('reddedildi',))
            else:
                self.tree.insert("", "end", values=formatted_row)
            
        conn.close()

    def durum_guncelle(self, yeni_durum):
        secili_item = self.tree.selection()
        if not secili_item:
            messagebox.showwarning("Uyarı", "Lütfen tablodan bir teklif seçin.")
            return
            
        teklif_id = self.tree.item(secili_item[0])['values'][0]
        
        conn = sqlite3.connect('imalat_motoru.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE Teklifler SET durum=? WHERE id=?", (yeni_durum, teklif_id))
        conn.commit()
        conn.close()
        
        self.load_gecmis_data() # Tabloyu yenile

    def teklif_sil(self):
        secili_item = self.tree.selection()
        if not secili_item:
            messagebox.showwarning("Uyarı", "Lütfen silmek için tablodan bir teklif seçin.")
            return
            
        cevap = messagebox.askyesno("Onay", "Seçili teklifi silmek istediğinize emin misiniz?")
        if cevap:
            teklif_id = self.tree.item(secili_item[0])['values'][0]
            
            conn = sqlite3.connect('imalat_motoru.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Teklifler WHERE id=?", (teklif_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarılı", "Teklif başarıyla silindi.")
            self.load_gecmis_data() # Tabloyu yenile

if __name__ == "__main__":
    init_db() # Önce veritabanını kontrol et/kur
    app = ImalatUygulamasi()
    app.mainloop()
