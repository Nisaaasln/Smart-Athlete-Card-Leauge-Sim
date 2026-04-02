from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class ZorlukSecimEkrani(QDialog):
    """
    DÜZELTİLDİ: Proje gereksinimi — Oyun başında zorluk seçimi yapılmalı (Kolay / Orta)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zorluk Seçimi")
        self.setFixedSize(400, 250)
        self.setStyleSheet("background-color: #1a1a2e; color: white;")
        self.secim = "orta"

        layout = QVBoxLayout()

        baslik = QLabel(" Yapay Zekâ Zorluk Seviyesi")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff88;")
        baslik.setAlignment(Qt.AlignCenter)
        layout.addWidget(baslik)

        aciklama = QLabel("Bilgisayarın nasıl oynayacağını seçin:")
        aciklama.setStyleSheet("font-size: 13px; color: lightgray;")
        aciklama.setAlignment(Qt.AlignCenter)
        layout.addWidget(aciklama)

        self.kolay_btn = QPushButton("  Kolay  —  Rastgele kart seçer")
        self.kolay_btn.setStyleSheet("""
            QPushButton { background-color: #2b2b3d; color: white; border-radius: 10px;
                          padding: 12px; font-size: 14px; }
            QPushButton:hover { background-color: #3a3a55; }
        """)
        self.kolay_btn.clicked.connect(lambda: self._sec("kolay"))
        layout.addWidget(self.kolay_btn)

        self.orta_btn = QPushButton("  Orta  —  En yüksek performanslı kartı seçer")
        self.orta_btn.setStyleSheet("""
            QPushButton { background-color: #2b2b3d; color: white; border-radius: 10px;
                          padding: 12px; font-size: 14px; }
            QPushButton:hover { background-color: #3a3a55; }
        """)
        self.orta_btn.clicked.connect(lambda: self._sec("orta"))
        layout.addWidget(self.orta_btn)

        self.setLayout(layout)

    def _sec(self, zorluk):
        self.secim = zorluk
        self.accept()


class KartWidget(QFrame):
    def __init__(self, kart, secim_fonksiyonu=None):
        super().__init__()
        self.kart = kart
        self.secim_fonksiyonu = secim_fonksiyonu
        self.setFixedWidth(300)
        self._aktif = True

        self._stil_guncelle()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        self.setGraphicsEffect(shadow)

        self._layout_olustur()

    def _stil_guncelle(self):
        if self._aktif:
            self.setStyleSheet("""
            QFrame {
                background-color: #1e1e2f;
                border-radius: 15px;
                color: white;
            }
            """)
        else:
            self.setStyleSheet("""
            QFrame {
                background-color: #111120;
                border-radius: 15px;
                color: gray;
                border: 2px solid #ff4444;
            }
            """)

    def _layout_olustur(self):
        old_layout = self.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old_layout)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        ust_container = QFrame()
        ust_container.setFixedHeight(180)

        resim = QLabel(ust_container)
        pixmap = QPixmap(self.kart.resim)
        if pixmap.isNull():
            print("Resim bulunamadı:", self.kart.resim)
        resim.setPixmap(pixmap.scaled(300, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        resim.setAlignment(Qt.AlignCenter)
        resim.setGeometry(0, 0, 300, 180)

        isim = QLabel(self.kart.ad, ust_container)
        isim.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        isim.move(10, 140)

        brans = QLabel(self.kart.brans.capitalize(), ust_container)
        brans.setStyleSheet("font-size: 12px; color: lightgray;")
        brans.move(10, 160)

        main_layout.addWidget(ust_container)

        enerji = QProgressBar()
        enerji.setMaximum(self.kart.max_enerji)
        enerji.setValue(max(0, self.kart.enerji))

        renk = "#00ff88"
        if self.kart.enerji < 20:
            renk = "#ff4444"  # Kritik: kırmızı
        elif self.kart.enerji < 40:
            renk = "#ffaa00"  # Düşük: turuncu

        enerji.setStyleSheet(f"""
        QProgressBar {{
            border: none;
            background: #2a2a40;
            height: 8px;
            border-radius: 4px;
        }}
        QProgressBar::chunk {{
            background-color: {renk};
            border-radius: 4px;
        }}
        """)
        main_layout.addWidget(enerji)

        if self.kart.enerji < 20:
            kritik_label = QLabel(" KRİTİK ENERJİ")
            kritik_label.setStyleSheet("color: #ff4444; font-size: 11px; font-weight: bold;")
            kritik_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(kritik_label)

        grid = QGridLayout()

        def stat_kutu(isim_str, deger):
            kutu = QFrame()
            kutu.setStyleSheet("""
                background-color: #2b2b3d;
                border-radius: 10px;
                padding: 8px;
            """)
            v = QVBoxLayout()
            label1 = QLabel(isim_str)
            label1.setStyleSheet("font-size: 10px; color: lightgray;")
            label2 = QLabel(str(deger))
            label2.setStyleSheet("font-size: 16px; font-weight: bold;")
            v.addWidget(label1)
            v.addWidget(label2)
            kutu.setLayout(v)
            return kutu

        if self.kart.brans == "futbol":
            grid.addWidget(stat_kutu("Penaltı", self.kart.penalti), 0, 0)
            grid.addWidget(stat_kutu("Serbest", self.kart.serbestVurus), 0, 1)
            grid.addWidget(stat_kutu("Kaleci", self.kart.kaleciKarsiKarsiya), 1, 0)
            grid.addWidget(stat_kutu("Dayanıklılık", self.kart.dayaniklilik), 1, 1)
        elif self.kart.brans == "basketbol":
            grid.addWidget(stat_kutu("Üçlük", self.kart.ucluk), 0, 0)
            grid.addWidget(stat_kutu("Serbest Atış", self.kart.serbestAtis), 0, 1)
            grid.addWidget(stat_kutu("İkilik", self.kart.ikilik), 1, 0)
            grid.addWidget(stat_kutu("Dayanıklılık", self.kart.dayaniklilik), 1, 1)
        elif self.kart.brans == "voleybol":
            grid.addWidget(stat_kutu("Servis", self.kart.servis), 0, 0)
            grid.addWidget(stat_kutu("Blok", self.kart.blok), 0, 1)
            grid.addWidget(stat_kutu("Smaç", self.kart.smac), 1, 0)
            grid.addWidget(stat_kutu("Dayanıklılık", self.kart.dayaniklilik), 1, 1)

        main_layout.addLayout(grid)

        alt_bilgi = QHBoxLayout()
        seviye_label = QLabel(f" Seviye {self.kart.seviye}")
        seviye_label.setStyleSheet("font-size: 11px; color: #ffdd00;")
        moral_label = QLabel(f" Moral: {self.kart.moral}")
        moral_renk = "#00ff88" if self.kart.moral > 60 else ("#ffaa00" if self.kart.moral > 40 else "#ff4444")
        moral_label.setStyleSheet(f"font-size: 11px; color: {moral_renk};")
        alt_bilgi.addWidget(seviye_label)
        alt_bilgi.addWidget(moral_label)
        main_layout.addLayout(alt_bilgi)

        if self.kart.ozel_yetenek:
            yetenek_label = QLabel(f" {type(self.kart.ozel_yetenek).__name__}")
            yetenek_label.setStyleSheet("font-size: 10px; color: #aaaaff;")
            yetenek_label.setToolTip(self.kart.ozel_yetenek.aciklama)
            main_layout.addWidget(yetenek_label)

        if self.kart.enerji <= 0:
            tukenMis = QLabel(" TÜKENMIŞ — Oynanamaz")
            tukenMis.setStyleSheet("color: #ff4444; font-weight: bold; font-size: 11px;")
            tukenMis.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(tukenMis)
            self._aktif = False
            self._stil_guncelle()

        self.setLayout(main_layout)

    def mousePressEvent(self, event):
        if self.secim_fonksiyonu and self.kart.enerji > 0:
            self.secim_fonksiyonu(self.kart)
        elif self.kart.enerji <= 0:
            QMessageBox.warning(self, "Tükenmiş Kart", f"{self.kart.ad} enerjisi bitti, oynanamaz!")

    def guncelle(self):
        """Kart görünümünü güncel verilerle yenile"""
        self._layout_olustur()


class BilgisayarKartiWidget(QFrame):
    """Bilgisayarın kartları için — varsayılan gizli, göster/gizle butonu ile açılır"""
    def __init__(self, kart):
        super().__init__()
        self.kart = kart
        self.setFixedWidth(220)
        self.setStyleSheet("""
        QFrame {
            background-color: #1e1e2f;
            border-radius: 12px;
            color: white;
        }
        """)
        layout = QVBoxLayout()

        isim = QLabel(self.kart.ad)
        isim.setStyleSheet("font-size: 13px; font-weight: bold; color: white;")
        isim.setAlignment(Qt.AlignCenter)
        layout.addWidget(isim)

        brans = QLabel(self.kart.brans.capitalize())
        brans.setStyleSheet("font-size: 11px; color: lightgray;")
        brans.setAlignment(Qt.AlignCenter)
        layout.addWidget(brans)

        enerji = QProgressBar()
        enerji.setMaximum(self.kart.max_enerji)
        enerji.setValue(max(0, self.kart.enerji))
        renk = "#ff4444" if self.kart.enerji < 20 else ("#ffaa00" if self.kart.enerji < 40 else "#00ff88")
        enerji.setStyleSheet(f"""
            QProgressBar {{ border: none; background: #2a2a40; height: 6px; border-radius: 3px; }}
            QProgressBar::chunk {{ background-color: {renk}; border-radius: 3px; }}
        """)
        layout.addWidget(enerji)

        seviye = QLabel(f" Seviye {self.kart.seviye}  |   Enerji: {self.kart.enerji}")
        seviye.setStyleSheet("font-size: 10px; color: #aaaaaa;")
        seviye.setAlignment(Qt.AlignCenter)
        layout.addWidget(seviye)

        self.setLayout(layout)


class TurSonucuWidget(QDialog):
    """Tur sonucunu gösteren popup"""
    def __init__(self, sonuc, tur_no, oyuncu_ad, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Tur {tur_no} Sonucu")
        self.setFixedSize(420, 320)
        self.setStyleSheet("background-color: #1a1a2e; color: white;")

        layout = QVBoxLayout()

        kazanan = sonuc.get("kazanan", "")
        if kazanan and kazanan.startswith("oyuncu"):
            renk = "#00ff88"
            mesaj = " KAZANDIN!"
        elif kazanan and kazanan.startswith("bilgisayar"):
            renk = "#ff4444"
            mesaj = " KAYBETTİN!"
        else:
            renk = "#ffdd00"
            mesaj = " BERABERE!"

        baslik = QLabel(mesaj)
        baslik.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {renk};")
        baslik.setAlignment(Qt.AlignCenter)
        layout.addWidget(baslik)

        brans_label = QLabel(f"Branş: {sonuc.get('brans', '').upper()}  |  Özellik: {sonuc.get('ozellik', '')}")
        brans_label.setStyleSheet("font-size: 12px; color: lightgray;")
        brans_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(brans_label)

        puan_frame = QFrame()
        puan_frame.setStyleSheet("background-color: #2b2b3d; border-radius: 10px; padding: 10px;")
        puan_layout = QHBoxLayout()

        o_kart = sonuc.get("o_kart")
        b_kart = sonuc.get("b_kart")

        oyuncu_col = QVBoxLayout()
        oyuncu_col.addWidget(self._label(oyuncu_ad, "14px", "white"))
        oyuncu_col.addWidget(self._label(o_kart.ad if o_kart else "-", "12px", "lightgray"))
        oyuncu_col.addWidget(self._label(str(sonuc.get("o_puan", 0)), "28px", "#00ff88"))
        puan_layout.addLayout(oyuncu_col)

        vs = QLabel("VS")
        vs.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        vs.setAlignment(Qt.AlignCenter)
        puan_layout.addWidget(vs)

        bilg_col = QVBoxLayout()
        bilg_col.addWidget(self._label("Bilgisayar", "14px", "white"))
        bilg_col.addWidget(self._label(b_kart.ad if b_kart else "-", "12px", "lightgray"))
        bilg_col.addWidget(self._label(str(sonuc.get("b_puan", 0)), "28px", "#ff4444"))
        puan_layout.addLayout(bilg_col)

        puan_frame.setLayout(puan_layout)
        layout.addWidget(puan_frame)

        tamam_btn = QPushButton("Devam Et ")
        tamam_btn.setStyleSheet("""
            QPushButton { background-color: #3a3a60; color: white; border-radius: 8px;
                          padding: 10px; font-size: 14px; }
            QPushButton:hover { background-color: #5a5a80; }
        """)
        tamam_btn.clicked.connect(self.accept)
        layout.addWidget(tamam_btn)

        self.setLayout(layout)

    def _label(self, metin, boyut, renk):
        l = QLabel(metin)
        l.setStyleSheet(f"font-size: {boyut}; color: {renk};")
        l.setAlignment(Qt.AlignCenter)
        return l


class OyunSonuEkrani(QDialog):
    """DÜZELTİLDİ: Oyun sonu ekranı — istatistikler ve kazanan gösterilir"""
    def __init__(self, kullanici, bilgisayar, kazanan, istatistikler, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Oyun Bitti!")
        self.setFixedSize(700, 600)
        self.setStyleSheet("background-color: #1a1a2e; color: white;")

        layout = QVBoxLayout()

        if kazanan:
            kazanan_mesaj = f" KAZANAN: {kazanan.ad.upper()}"
            renk = "#00ff88" if kazanan.ad == kullanici.ad else "#ff4444"
        else:
            kazanan_mesaj = " BERABERE!"
            renk = "#ffdd00"

        baslik = QLabel(kazanan_mesaj)
        baslik.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {renk};")
        baslik.setAlignment(Qt.AlignCenter)
        layout.addWidget(baslik)

        skor_frame = QFrame()
        skor_frame.setStyleSheet("background-color: #2b2b3d; border-radius: 12px; padding: 12px;")
        skor_layout = QHBoxLayout()

        def skor_kutu(ad, skor, galip, bera):
            col = QVBoxLayout()
            col.addWidget(self._label(ad, "15px", "white"))
            col.addWidget(self._label(f"{skor} puan", "28px", "#00ff88"))
            col.addWidget(self._label(f"Galibiyet: {galip}  Beraberlik: {bera}", "11px", "lightgray"))
            return col

        skor_layout.addLayout(skor_kutu(kullanici.ad, kullanici.skor,
                                        kullanici.toplam_galibiyet, kullanici.toplam_beraberlik))
        skor_layout.addWidget(self._label("—", "22px", "white"))
        skor_layout.addLayout(skor_kutu(bilgisayar.ad, bilgisayar.skor,
                                        bilgisayar.toplam_galibiyet, bilgisayar.toplam_beraberlik))
        skor_frame.setLayout(skor_layout)
        layout.addWidget(skor_frame)

        tablo_baslik = QLabel(" Maç İstatistikleri")
        tablo_baslik.setStyleSheet("font-size: 15px; font-weight: bold; color: #aaaaff;")
        layout.addWidget(tablo_baslik)

        tablo = QTableWidget()
        tablo.setColumnCount(6)
        tablo.setHorizontalHeaderLabels(["Tur", "Oyuncu Kartı", "Bilgisayar Kartı", "Özellik", "Skor", "Kazanan"])
        tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tablo.setStyleSheet("""
            QTableWidget { background-color: #2b2b3d; color: white; gridline-color: #3a3a55; }
            QHeaderView::section { background-color: #3a3a55; color: white; padding: 4px; }
        """)
        tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tablo.setRowCount(len(istatistikler))

        for row, kayit in enumerate(istatistikler):
            tablo.setItem(row, 0, QTableWidgetItem(str(kayit.get("tur", ""))))
            tablo.setItem(row, 1, QTableWidgetItem(kayit.get("oyuncu_kart", "")))
            tablo.setItem(row, 2, QTableWidgetItem(kayit.get("bilgisayar_kart", "")))
            tablo.setItem(row, 3, QTableWidgetItem(kayit.get("ozellik", "")))
            skor_str = f"{kayit.get('oyuncu_puan',0)} - {kayit.get('bilgisayar_puan',0)}"
            tablo.setItem(row, 4, QTableWidgetItem(skor_str))
            tablo.setItem(row, 5, QTableWidgetItem(kayit.get("kazanan", "")))

        layout.addWidget(tablo)

        kapat_btn = QPushButton("Oyunu Kapat")
        kapat_btn.setStyleSheet("""
            QPushButton { background-color: #cc3333; color: white; border-radius: 8px;
                          padding: 10px; font-size: 14px; }
            QPushButton:hover { background-color: #ee4444; }
        """)
        kapat_btn.clicked.connect(self.accept)
        layout.addWidget(kapat_btn)

        self.setLayout(layout)

    def _label(self, metin, boyut, renk):
        l = QLabel(metin)
        l.setStyleSheet(f"font-size: {boyut}; color: {renk};")
        l.setAlignment(Qt.AlignCenter)
        return l


class TestApp(QMainWindow):
    def __init__(self, oyun_yonetici, secim_callback):
        super().__init__()
        self.oyun_yonetici = oyun_yonetici
        self.secim_callback = secim_callback
        self.kart_widgetleri = []
        self.bilgisayar_gizli = True
        self.secilen_ozellik = None

        self.setWindowTitle("Akıllı Sporcu Kart Ligi")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #12121f;")

        self._arayuz_olustur()

    def _arayuz_olustur(self):
        merkez = QWidget()
        self.setCentralWidget(merkez)
        ana_layout = QVBoxLayout(merkez)
        ana_layout.setSpacing(10)

        ust_bar = QFrame()
        ust_bar.setStyleSheet("background-color: #1e1e2f; border-radius: 10px; padding: 8px;")
        ust_bar_layout = QHBoxLayout(ust_bar)

        baslik = QLabel("  Akıllı Sporcu Kart Ligi")
        baslik.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff88;")
        ust_bar_layout.addWidget(baslik)

        ust_bar_layout.addStretch()

        self.skor_label = QLabel("Skor:  Sen 0  —  Bilgisayar 0")
        self.skor_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        ust_bar_layout.addWidget(self.skor_label)

        ust_bar_layout.addStretch()

        self.tur_label = QLabel("Tur: 1/9  |  Sıradaki: FUTBOL")
        self.tur_label.setStyleSheet("font-size: 13px; color: #aaaaff;")
        ust_bar_layout.addWidget(self.tur_label)

        ana_layout.addWidget(ust_bar)

        orta = QHBoxLayout()

        sol_frame = QFrame()
        sol_frame.setStyleSheet("background-color: #1a1a30; border-radius: 10px; padding: 6px;")
        sol_layout = QVBoxLayout(sol_frame)

        oyuncu_baslik = QLabel("🧑 Senin Kartların")
        oyuncu_baslik.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        sol_layout.addWidget(oyuncu_baslik)

        ozellik_frame = QFrame()
        ozellik_frame.setStyleSheet("background-color: #2b2b3d; border-radius: 8px; padding: 4px;")
        ozellik_layout = QHBoxLayout(ozellik_frame)
        ozellik_lbl = QLabel("Özellik Seç (opsiyonel):")
        ozellik_lbl.setStyleSheet("color: lightgray; font-size: 11px;")
        ozellik_layout.addWidget(ozellik_lbl)
        self.ozellik_combo = QComboBox()
        self.ozellik_combo.addItem("Rastgele (Otomatik)")
        self.ozellik_combo.setStyleSheet("""
            QComboBox { background-color: #3a3a55; color: white; border-radius: 6px; padding: 4px; }
            QComboBox QAbstractItemView { background-color: #3a3a55; color: white; }
        """)
        self.ozellik_combo.currentIndexChanged.connect(self._ozellik_secildi)
        ozellik_layout.addWidget(self.ozellik_combo)
        sol_layout.addWidget(ozellik_frame)

        oyuncu_scroll = QScrollArea()
        oyuncu_scroll.setWidgetResizable(True)
        oyuncu_scroll.setStyleSheet("border: none;")
        oyuncu_icerik = QWidget()
        self.oyuncu_grid = QGridLayout(oyuncu_icerik)
        self.oyuncu_grid.setSpacing(15)
        oyuncu_scroll.setWidget(oyuncu_icerik)
        sol_layout.addWidget(oyuncu_scroll)

        orta.addWidget(sol_frame, stretch=2)

        sag_frame = QFrame()
        sag_frame.setStyleSheet("background-color: #1a1a30; border-radius: 10px; padding: 6px;")
        sag_layout = QVBoxLayout(sag_frame)

        bilg_baslik_row = QHBoxLayout()
        bilg_baslik = QLabel(" Bilgisayarın Kartları")
        bilg_baslik.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        bilg_baslik_row.addWidget(bilg_baslik)

        self.goster_btn = QPushButton(" Göster")
        self.goster_btn.setStyleSheet("""
            QPushButton { background-color: #3a3a60; color: white; border-radius: 8px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #5a5a80; }
        """)
        self.goster_btn.clicked.connect(self._bilgisayar_goster_gizle)
        bilg_baslik_row.addWidget(self.goster_btn)
        sag_layout.addLayout(bilg_baslik_row)

        bilg_scroll = QScrollArea()
        bilg_scroll.setWidgetResizable(True)
        bilg_scroll.setStyleSheet("border: none;")
        self.bilg_icerik = QWidget()
        self.bilg_grid = QGridLayout(self.bilg_icerik)
        self.bilg_grid.setSpacing(10)
        bilg_scroll.setWidget(self.bilg_icerik)
        sag_layout.addWidget(bilg_scroll)

        orta.addWidget(sag_frame, stretch=1)
        ana_layout.addLayout(orta)

        self.durum_label = QLabel("Sıradaki branş için bir kart seçin.")
        self.durum_label.setStyleSheet(
            "background-color: #2b2b3d; color: #aaffaa; font-size: 13px; "
            "border-radius: 8px; padding: 8px;"
        )
        self.durum_label.setAlignment(Qt.AlignCenter)
        ana_layout.addWidget(self.durum_label)

        self._oyuncu_kartlarini_goster()
        self._bilgisayar_kartlarini_gizle()
        self._tur_etiketini_guncelle(0)

    def _ozellik_secildi(self, index):
        if index == 0:
            self.secilen_ozellik = None
        else:
            self.secilen_ozellik = self.ozellik_combo.currentText()

    def _ozellik_combo_guncelle(self, brans):
        """Sıradaki branşa göre özellik seçeneklerini günceller"""
        self.ozellik_combo.blockSignals(True)
        self.ozellik_combo.clear()
        self.ozellik_combo.addItem("Rastgele (Otomatik)")
        ozellikler = self.oyun_yonetici.ozellik_listesi_gui(brans)
        for oz in ozellikler:
            self.ozellik_combo.addItem(oz)
        self.ozellik_combo.blockSignals(False)
        self.secilen_ozellik = None

    def _bilgisayar_goster_gizle(self):
        """DÜZELTİLDİ: Bilgisayar kartlarını göster/gizle"""
        self.bilgisayar_gizli = not self.bilgisayar_gizli
        if self.bilgisayar_gizli:
            self.goster_btn.setText(" Göster")
            self._bilgisayar_kartlarini_gizle()
        else:
            self.goster_btn.setText(" Gizle")
            self._bilgisayar_kartlarini_goster()

    def _bilgisayar_kartlarini_gizle(self):
        while self.bilg_grid.count():
            item = self.bilg_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        gizli = QLabel(" Bilgisayarın kartları gizli.\n'Göster' butonuna tıkla.")
        gizli.setStyleSheet("color: gray; font-size: 13px;")
        gizli.setAlignment(Qt.AlignCenter)
        self.bilg_grid.addWidget(gizli, 0, 0)

    def _bilgisayar_kartlarini_goster(self):
        while self.bilg_grid.count():
            item = self.bilg_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        satir, sutun = 0, 0
        for k in self.oyun_yonetici.bilgisayar.kartlar:
            widget = BilgisayarKartiWidget(k)
            self.bilg_grid.addWidget(widget, satir, sutun)
            sutun += 1
            if sutun == 2:
                sutun = 0
                satir += 1

    def _oyuncu_kartlarini_goster(self):
        while self.oyuncu_grid.count():
            item = self.oyuncu_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.kart_widgetleri.clear()

        satir, sutun = 0, 0
        for k in self.oyun_yonetici.oyuncu.kartlar:
            w = KartWidget(k, self.kart_secildi)
            self.oyuncu_grid.addWidget(w, satir, sutun)
            self.kart_widgetleri.append(w)
            sutun += 1
            if sutun == 3:
                sutun = 0
                satir += 1

    def _tur_etiketini_guncelle(self, tur_index):
        if tur_index >= 9:
            self.tur_label.setText("Oyun Bitti!")
            return
        brans = ["FUTBOL", "BASKETBOL", "VOLEYBOL"][tur_index % 3]
        self.tur_label.setText(f"Tur: {tur_index + 1}/9  |  Sıradaki: {brans}")
        self.durum_label.setText(f"Sıradaki branş: {brans} — Kartını seç!")
        self._ozellik_combo_guncelle(brans.lower())

    def kart_secildi(self, kart):
        print("Seçilen kart:", kart.ad)
        self.secim_callback(kart, self.secilen_ozellik)

    def tur_sonucu_goster(self, sonuc, tur_index):
        """Tur bittikten sonra sonucu göster ve arayüzü güncelle"""
        oyuncu = self.oyun_yonetici.oyuncu
        bilgisayar = self.oyun_yonetici.bilgisayar

        self.skor_label.setText(
            f"Skor:  Sen {oyuncu.skor}  —  Bilgisayar {bilgisayar.skor}")

        dialog = TurSonucuWidget(sonuc, tur_index, oyuncu.ad, self)
        dialog.exec_()

        self._oyuncu_kartlarini_goster()
        if not self.bilgisayar_gizli:
            self._bilgisayar_kartlarini_goster()

        self._tur_etiketini_guncelle(tur_index)

    def oyun_bitis_goster(self, kullanici, bilgisayar, kazanan, istatistikler):
        """DÜZELTİLDİ: Oyun sonu ekranını göster"""
        self.tur_label.setText(" OYUN BİTTİ")
        self.durum_label.setText("Oyun tamamlandı!")
        ekran = OyunSonuEkrani(kullanici, bilgisayar, kazanan, istatistikler, self)
        ekran.exec_()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    print("kart.py direkt çalıştırılamaz. oyun.py üzerinden başlatın.")
    sys.exit(0)  
