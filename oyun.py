# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import random
import os

RESIMLER = {
    "Karim Mostafa Benzema": "images/futbol1.jpg",
    "Cristiano Ronaldo": "images/futbol2.jpg",
    "Arda Turan": "images/futbol3.jpg",
    "Lionel Messi": "images/futbol4.jpg",
    "Kylian Mbappe": "images/futbol5.jpg",
    "Erling Haaland": "images/futbol6.jpg",
    "Kevin De Bruyne": "images/futbol7.jpg",
    "Luka Modric": "images/futbol8.jpg",
    "Cedi Osman": "images/basketbol1.jpg",
    "Stephen Curry": "images/basketbol2.jpg",
    "Onuralp Bitim": "images/basketbol3.jpg",
    "LeBron James": "images/basketbol4.jpg",
    "Kevin Durant": "images/basketbol5.jpg",
    "Giannis Antetokounmpo": "images/basketbol6.jpg",
    "Nikola Jokic": "images/basketbol7.jpg",
    "Luka Doncic": "images/basketbol8.jpg",
    "Eda Erdem": "images/voleybol1.jpg",
    "Zehra Güneş": "images/voleybol2.jpg",
    "İlkin Aydın": "images/voleybol3.jpg",
    "Paola Egonu": "images/voleybol4.jpg",
    "Gabi Guimaraes": "images/voleybol5.jpg",
    "Tijana Boskovic": "images/voleybol6.jpg",
    "Wilfredo Leon": "images/voleybol7.jpg",
    "Earvin Ngapeth": "images/voleybol8.jpg"
}


def kartlari_oku(dosya_yolu):
    kartlar = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dosya_tam_yol = os.path.join(base_dir, dosya_yolu)

    with open(dosya_tam_yol, "r", encoding="utf-8") as f:
        id_sayac = 1
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue

            parcalar = satir.split(",")
            if len(parcalar) != 9:
                print(f"Hata: eksik veri -> {satir}")
                continue

            brans, ad, takim = parcalar[0], parcalar[1], parcalar[2]
            oz1, oz2, oz3 = map(int, parcalar[3:6])
            dayan = int(parcalar[6])
            ozel = parcalar[7]
            ek_bilgi = parcalar[8] if len(parcalar) > 8 else ""

            if brans == "Futbol":
                kart = Futbolcu(id_sayac, ad, takim, oz1, oz2, oz3, dayan, 1.2, dayan, 1)
            elif brans == "Basketbol":
                kart = Basketbolcu(id_sayac, ad, takim, oz1, oz2, oz3, dayan, 1.2, dayan, 1)
            elif brans == "Voleybol":
                kart = Voleybolcu(id_sayac, ad, takim, oz1, oz2, oz3, dayan, 1.2, dayan, 1)
            else:
                continue

            kart.ozel_yetenek = uygun_yetenek_ata(ozel)
            kart.resim = os.path.join(base_dir, RESIMLER.get(ad, "images/default.jpg"))
            kartlar.append(kart)
            id_sayac += 1

    return kartlar


class VeriOkuyucu:
    @staticmethod
    def kartlari_oku(dosya_yolu):
        return kartlari_oku(dosya_yolu)



class OzelYetenek:
    def __init__(self):
        self.aciklama = "Genel yetenek"
        self.aktif = False

    def uygula(self, kart, rakip, oyun, ozellik=None):
        return 0


class ClutchPlayer(OzelYetenek):
    def __init__(self):
        super().__init__()
        self.aciklama = "Son 3 turda +10 bonus"

    def uygula(self, kart, rakip, oyun, ozellik=None):
        if oyun and kart in oyun.son_3_tur:
            return 10
        return 0


class Finisher(OzelYetenek):
    def __init__(self):
        super().__init__()
        self.aciklama = "Enerjisi düşükken +8 ek bonus alır"

    def uygula(self, kart, rakip, oyun, ozellik=None):
        if not self.aktif and kart.enerji < 30:
            self.aktif = True
            return 8
        return 0

    def reset_tur(self):
        self.aktif = False


class Defender(OzelYetenek):
    def __init__(self):
        super().__init__()
        self.aciklama = "Rakibin özel yetenek bonusunu yarıya düşürür"

    def uygula(self, kart, rakip, oyun, ozellik=None):
        return 0

    def rakip_bonusunu_azalt(self, rakip, kart, oyun, ozellik):
        if rakip and rakip.ozel_yetenek and not isinstance(rakip.ozel_yetenek, Defender):
            return rakip.ozel_yetenek.uygula(rakip, kart, oyun, ozellik) // 2
        return 0


class Veteran(OzelYetenek):
    def __init__(self):
        super().__init__()
        self.aciklama = "Enerji kaybını %50 azaltır"

    def enerji_azalt(self, miktar):
        return miktar // 2


class Legend(OzelYetenek):
    def __init__(self):
        super().__init__()
        self.aciklama = "Bir maçta bir kez seçilen özelliği iki kat etkileyebilir"

    def uygula(self, kart, rakip, oyun, ozellik=None):
        if not self.aktif and ozellik:
            self.aktif = True
            return getattr(kart, ozellik, 0)
        return 0


class Captain(OzelYetenek):
    def __init__(self):
        super().__init__()
        self.aciklama = "Aynı branştaki takım kartlarına +5 moral"

    def uygula(self, kart, rakip, oyun, ozellik=None):
        if oyun is None:
            return 0
        for k in oyun.oyuncu.kartlar:
            if k.brans == kart.brans and k is not kart:
                k.moral = min(k.moral + 5, 100)
        return 0


YETENEK_SINIFLARI = {
    "ClutchPlayer": ClutchPlayer,
    "Finisher": Finisher,
    "Defender": Defender,
    "Veteran": Veteran,
    "Legend": Legend,
    "Captain": Captain
}

def uygun_yetenek_ata(isim):
    sinif = YETENEK_SINIFLARI.get(isim)
    return sinif() if sinif else None


class Sporcu(ABC):
    def __init__(self, id, ad, takim, brans, enerji, dayaniklilik, seviye, ozel_yetenek):
        self.id = id
        self.ad = ad
        self.takim = takim
        self.brans = brans
        self.enerji = enerji
        self.max_enerji = enerji
        self.dayaniklilik = dayaniklilik
        self.seviye = seviye
        self.deneyim = 0
        self.ozel_yetenek = ozel_yetenek
        self.kullanildi = False
        self.moral = 50
        self.clutch = False
        self.seviye_atladi_flag = False
        self.kart_galibiyet = 0

    def sporcuPuaniGoster(self, ozellik):
        print(f"{self.ad} ({self.brans}) - {ozellik}: {getattr(self, ozellik, 0)}")

    def kartBilgisiYazdir(self):
        print(f"{self.ad} | Takım: {self.takim} | Enerji: {self.enerji}/{self.max_enerji} | Moral: {self.moral}")

    @abstractmethod
    def performans_hesapla(self, ozellik, rakip=None, oyun=None):
        pass

    def enerji_guncelle(self, sonuc, ozel_yetenek=False):
        if sonuc == "win":
            kayip = 5
        elif sonuc == "lose":
            kayip = 10
        else:
            kayip = 3

        if ozel_yetenek:
            kayip += 5

        if isinstance(self.ozel_yetenek, Veteran):
            kayip = self.ozel_yetenek.enerji_azalt(kayip)

        self.enerji -= kayip
        if self.enerji < 0:
            self.enerji = 0

        if self.enerji < 20:
            print(f" {self.ad} kritik enerji seviyesinde: {self.enerji}")

    def moral_bonusu(self):
        if self.moral > 80:
            return 10
        elif self.moral > 60:
            return 5
        elif self.moral < 40:
            return -5
        else:
            return 0

    def moral_guncelle(self, miktar):
        self.moral = max(0, min(100, self.moral + miktar))

    def seviye_bonusu(self):
        if self.seviye == 1:
            return 0
        elif self.seviye == 2:
            return 5
        elif self.seviye == 3:
            return 10
        else:
            return self.seviye * 5

    def deneyim_kazan(self, miktar):
        self.deneyim += miktar
        self.seviye_guncelle()

    def seviye_guncelle(self):
        """
        - 2 galibiyet VEYA 4 deneyim → Seviye 2
        - 4 galibiyet VEYA 8 deneyim → Seviye 3
        """
        while self.seviye < 3:
            if self.seviye == 1 and (self.deneyim >= 4 or self.kart_galibiyet >= 2):
                self.seviye += 1
                self.brans_ozellik_artir()
                self.seviye_atladi_flag = True
                print(f"{self.ad} seviye atladı! Yeni seviye: {self.seviye}")
            elif self.seviye == 2 and (self.deneyim >= 8 or self.kart_galibiyet >= 4):
                self.seviye += 1
                self.brans_ozellik_artir()
                self.seviye_atladi_flag = True
                print(f"{self.ad} seviye atladı! Yeni seviye: {self.seviye}")
            else:
                break

    def brans_ozellik_artir(self):
        for attr in ['penalti', 'serbestVurus', 'kaleciKarsiKarsiya',
                     'ucluk', 'ikilik', 'serbestAtis',
                     'servis', 'blok', 'smac']:
            if hasattr(self, attr):
                setattr(self, attr, getattr(self, attr) + 5)
        self.dayaniklilik += 5
        self.max_enerji += 10
        self.enerji = min(self.enerji + 10, self.max_enerji)

    def ozel_yetenek_kullan(self, hedef=None):
        self.enerji = min(self.enerji + 10, self.max_enerji)
        print(f"{self.ad} özel yeteneğini kullandı ve enerjisini yeniledi!")


class Futbolcu(Sporcu):
    def __init__(self, id, ad, takim, penalti, serbestVurus, kaleciKarsiKarsiya,
                 dayaniklilik, ozelYetenekKatsayisi, enerji, seviye):
        super().__init__(id, ad, takim, "futbol", enerji, dayaniklilik, seviye, ozelYetenekKatsayisi)
        self.penalti = penalti
        self.serbestVurus = serbestVurus
        self.kaleciKarsiKarsiya = kaleciKarsiKarsiya

    def performans_hesapla(self, ozellik, rakip=None, oyun=None):
        temel = getattr(self, ozellik, 0)
        ceza = 0
        if 40 <= self.enerji <= 70:
            ceza = temel * 0.10
        elif 0 < self.enerji < 40:
            ceza = temel * 0.20

        moral = self.moral_bonusu()
        seviye = self.seviye_bonusu()

        if isinstance(self.ozel_yetenek, Finisher):
            self.ozel_yetenek.reset_tur()

        ozel = self.ozel_yetenek.uygula(self, rakip, oyun, ozellik) if self.ozel_yetenek else 0

        defender_indirim = 0
        if isinstance(self.ozel_yetenek, Defender) and rakip:
            defender_indirim = self.ozel_yetenek.rakip_bonusunu_azalt(rakip, self, oyun, ozellik)

        try:
            ozel = int(ozel)
        except:
            ozel = 0

        return int(temel) + int(moral) + ozel - int(ceza) + int(seviye) - defender_indirim


class Basketbolcu(Sporcu):
    def __init__(self, id, ad, takim, ucluk, ikilik, serbestAtis,
                 dayaniklilik, ozelYetenekKatsayisi, enerji, seviye):
        super().__init__(id, ad, takim, "basketbol", enerji, dayaniklilik, seviye, ozelYetenekKatsayisi)
        self.ucluk = ucluk
        self.ikilik = ikilik
        self.serbestAtis = serbestAtis

    def performans_hesapla(self, ozellik, rakip=None, oyun=None):
        temel = getattr(self, ozellik, 0)
        ceza = 0
        if 40 <= self.enerji <= 70:
            ceza = temel * 0.10
        elif 0 < self.enerji < 40:
            ceza = temel * 0.20

        moral = self.moral_bonusu()
        seviye = self.seviye_bonusu()

        if isinstance(self.ozel_yetenek, Finisher):
            self.ozel_yetenek.reset_tur()

        ozel = self.ozel_yetenek.uygula(self, rakip, oyun, ozellik) if self.ozel_yetenek else 0

        defender_indirim = 0
        if isinstance(self.ozel_yetenek, Defender) and rakip:
            defender_indirim = self.ozel_yetenek.rakip_bonusunu_azalt(rakip, self, oyun, ozellik)

        try:
            ozel = int(ozel)
        except:
            ozel = 0

        return int(temel) + int(moral) + ozel - int(ceza) + int(seviye) - defender_indirim


class Voleybolcu(Sporcu):
    def __init__(self, id, ad, takim, servis, blok, smac,
                 dayaniklilik, ozelYetenekKatsayisi, enerji, seviye):
        super().__init__(id, ad, takim, "voleybol", enerji, dayaniklilik, seviye, ozelYetenekKatsayisi)
        self.servis = servis
        self.blok = blok
        self.smac = smac

    def performans_hesapla(self, ozellik, rakip=None, oyun=None):
        temel = getattr(self, ozellik, 0)
        ceza = 0
        if 40 <= self.enerji <= 70:
            ceza = temel * 0.10
        elif 0 < self.enerji < 40:
            ceza = temel * 0.20

        moral = self.moral_bonusu()
        seviye = self.seviye_bonusu()

        if isinstance(self.ozel_yetenek, Finisher):
            self.ozel_yetenek.reset_tur()

        ozel = self.ozel_yetenek.uygula(self, rakip, oyun, ozellik) if self.ozel_yetenek else 0

        defender_indirim = 0
        if isinstance(self.ozel_yetenek, Defender) and rakip:
            defender_indirim = self.ozel_yetenek.rakip_bonusunu_azalt(rakip, self, oyun, ozellik)

        try:
            ozel = int(ozel)
        except:
            ozel = 0

        return int(temel) + int(moral) + ozel - int(ceza) + int(seviye) - defender_indirim


class KartSecmeStratejisi(ABC):
    @abstractmethod
    def kart_sec(self, kartlar, brans):
        pass


class KolayStrateji(KartSecmeStratejisi):
    def kart_sec(self, kartlar, brans):
        uygun = [k for k in kartlar if k.brans == brans and k.enerji > 0]
        return random.choice(uygun) if uygun else None


class OrtaStrateji(KartSecmeStratejisi):
    def kart_sec(self, kartlar, brans):
        uygun = [k for k in kartlar if k.brans == brans and k.enerji > 0]
        if not uygun:
            return None

        IGNORE = {"id", "ad", "takim", "brans", "enerji", "max_enerji",
                  "dayaniklilik", "seviye", "deneyim", "ozel_yetenek",
                  "kullanildi", "moral", "clutch", "seviye_atladi_flag",
                  "kart_galibiyet", "resim"}

        def ortalama_performans(kart):
            attrs = [a for a in vars(kart) if a not in IGNORE and isinstance(getattr(kart, a), (int, float))]
            if not attrs:
                return 0
            toplam = sum(kart.performans_hesapla(attr, rakip=None, oyun=None) for attr in attrs)
            return toplam / len(attrs)

        uygun.sort(key=ortalama_performans, reverse=True)
        return uygun[0]


class Oyuncu(ABC):
    def __init__(self, ad, strateji=None):
        self.ad = ad
        self.kartlar = []
        self.skor = 0
        self.strateji = strateji
        self.kazanma_serisi = 0
        self.kaybetme_serisi = 0
        self.son_brans = None
        self.brans_kayip_serisi = 0
        self.son_kazanc_ozel = False
        self.goster = False
        self.toplam_galibiyet = 0
        self.toplam_beraberlik = 0
        self.ozel_yetenek_galibiyet = 0
        self.maks_galibiyet_serisi = 0

    @abstractmethod
    def kartSec(self, brans):
        pass

    def kart_sec(self, brans):
        if self.strateji:
            return self.strateji.kart_sec(self.kartlar, brans)
        else:
            uygun = [k for k in self.kartlar if k.brans == brans and k.enerji > 0]
            return random.choice(uygun) if uygun else None

    def kartlari_goster(self):
        if self.goster:
            for k in self.kartlar:
                print(f"{k.ad} ({k.brans}) - Enerji: {k.enerji}")
        else:
            print("Bilgisayar kartları gizli.")


class Kullanici(Oyuncu):
    def __init__(self, ad):
        super().__init__(ad, strateji=None)

    def kartSec(self, brans):
        return self.kart_sec(brans)


class Bilgisayar(Oyuncu):
    def __init__(self, ad, strateji=None):
        super().__init__(ad, strateji=strateji)

    def kartSec(self, brans):
        return self.kart_sec(brans)


class OyunYonetici:
    TOPLAM_TUR = 9

    def __init__(self, oyuncu, bilgisayar):
        self.oyuncu = oyuncu
        self.bilgisayar = bilgisayar
        self.turlar = ["futbol", "basketbol", "voleybol"]
        self.son_3_tur = []
        self.turda_aktif_ozel = False
        self.istatistik = MacIstatistik()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.kartlar = kartlari_oku(os.path.join(base_dir, "sporcular.txt"))

        self._kartlari_dagit()

    def _kartlari_dagit(self):
        """
        Toplam 24 kart: 8 futbol, 8 basketbol, 8 voleybol → her oyuncuya 4'er kart.
        """
        futbolcular = [k for k in self.kartlar if k.brans == "futbol"]
        basketbolcular = [k for k in self.kartlar if k.brans == "basketbol"]
        voleybolcular = [k for k in self.kartlar if k.brans == "voleybol"]

        random.shuffle(futbolcular)
        random.shuffle(basketbolcular)
        random.shuffle(voleybolcular)

        self.oyuncu.kartlar = futbolcular[:4] + basketbolcular[:4] + voleybolcular[:4]
        self.bilgisayar.kartlar = futbolcular[4:] + basketbolcular[4:] + voleybolcular[4:]

    def ozellik_listesi(self, kart):
        """Karta ait karşılaştırılabilir özellik listesini döndürür"""
        IGNORE = {"id", "ad", "takim", "brans", "enerji", "max_enerji", "dayaniklilik",
                  "seviye", "deneyim", "ozel_yetenek", "kullanildi", "moral",
                  "clutch", "seviye_atladi_flag", "kart_galibiyet", "resim"}
        return [o for o in vars(kart).keys()
                if o not in IGNORE and isinstance(getattr(kart, o), (int, float))]

    def ozellik_sec(self, kart, secilen_ozellik=None):
        """Özellik seçer; kullanıcı seçim yaptıysa onu, yoksa rastgele"""
        ozellikler = self.ozellik_listesi(kart)
        if secilen_ozellik and secilen_ozellik in ozellikler:
            return secilen_ozellik
        return random.choice(ozellikler)

    def kart_bul(self, oyuncu, brans):
        uygun = [k for k in oyuncu.kartlar if k.brans == brans and k.enerji > 0]
        return random.choice(uygun) if uygun else None

    def tur_oyna(self, i, secilen_kart=None, secilen_ozellik=None):
        brans = self.turlar[i % 3]
        self.turda_aktif_ozel = False

        o_kart = secilen_kart if secilen_kart else self.kart_bul(self.oyuncu, brans)
        b_kart = self.kart_bul(self.bilgisayar, brans)

        if not o_kart and not b_kart:
            print(f"{brans} turu atlandı (kart yok)")
            return None
        if not o_kart:
            print("Bilgisayar hükmen kazandı!")
            self.bilgisayar.skor += 8
            return {"sonuc": "bilgisayar_hukmen"}
        if not b_kart:
            print("Sen hükmen kazandın!")
            self.oyuncu.skor += 8
            return {"sonuc": "oyuncu_hukmen"}

        ozellik = self.ozellik_sec(o_kart, secilen_ozellik)

        o_puan = o_kart.performans_hesapla(ozellik, rakip=b_kart, oyun=self)
        b_puan = b_kart.performans_hesapla(ozellik, rakip=o_kart, oyun=self)

        if random.random() < 0.2:
            o_kart.ozel_yetenek_kullan()
            o_kart.enerji_guncelle("win", ozel_yetenek=True)
            o_puan = o_kart.performans_hesapla(ozellik, rakip=b_kart, oyun=self)

        if random.random() < 0.2:
            b_kart.ozel_yetenek_kullan()
            b_kart.enerji_guncelle("win", ozel_yetenek=True)
            b_puan = b_kart.performans_hesapla(ozellik, rakip=o_kart, oyun=self)

        kazanan = None

        if o_puan > b_puan:
            kazanan = "oyuncu"
        elif b_puan > o_puan:
            kazanan = "bilgisayar"
        else:
            diger_ozellikler = [o for o in self.ozellik_listesi(o_kart) if o != ozellik]
            for oz in diger_ozellikler:
                o2 = o_kart.performans_hesapla(oz, rakip=b_kart, oyun=self)
                b2 = b_kart.performans_hesapla(oz, rakip=o_kart, oyun=self)
                if o2 > b2:
                    kazanan = "oyuncu_yedek"
                    break
                elif b2 > o2:
                    kazanan = "bilgisayar_yedek"
                    break

            if kazanan is None:
                o_bonus = o_kart.ozel_yetenek.uygula(o_kart, b_kart, self, ozellik) if o_kart.ozel_yetenek else 0
                b_bonus = b_kart.ozel_yetenek.uygula(b_kart, o_kart, self, ozellik) if b_kart.ozel_yetenek else 0
                if o_bonus > b_bonus:
                    kazanan = "oyuncu_ozel"
                elif b_bonus > o_bonus:
                    kazanan = "bilgisayar_ozel"

            if kazanan is None:
                if o_kart.dayaniklilik > b_kart.dayaniklilik:
                    kazanan = "oyuncu_dayan"
                elif b_kart.dayaniklilik > o_kart.dayaniklilik:
                    kazanan = "bilgisayar_dayan"
                elif o_kart.enerji > b_kart.enerji:
                    kazanan = "oyuncu_enerji"
                elif b_kart.enerji > o_kart.enerji:
                    kazanan = "bilgisayar_enerji"
                elif o_kart.seviye > b_kart.seviye:
                    kazanan = "oyuncu_seviye"
                elif b_kart.seviye > o_kart.seviye:
                    kazanan = "bilgisayar_seviye"
                else:
                    kazanan = "berabere"

        if kazanan and kazanan.startswith("oyuncu"):
            mesaj = {
                "oyuncu": "Kazandın!",
                "oyuncu_ozel": "Özel yetenek bonusuyla Kazandın!",
                "oyuncu_yedek": "Yedek özelliklerle Kazandın!",
                "oyuncu_dayan": "Dayanıklılıkla Kazandın!",
                "oyuncu_enerji": "Enerji ile Kazandın!",
                "oyuncu_seviye": "Seviye ile Kazandın!"
            }
            print(mesaj.get(kazanan, "Kazandın!"))

            puan = 10
            if kazanan == "oyuncu_ozel":
                puan = 15
                self.oyuncu.ozel_yetenek_galibiyet += 1

            self.oyuncu.toplam_galibiyet += 1
            self.oyuncu.kazanma_serisi += 1
            self.oyuncu.kaybetme_serisi = 0
            self.bilgisayar.kazanma_serisi = 0
            self.oyuncu.maks_galibiyet_serisi = max(
                self.oyuncu.maks_galibiyet_serisi, self.oyuncu.kazanma_serisi)

            if self.oyuncu.kazanma_serisi == 2:
                o_kart.moral_guncelle(10)
            elif self.oyuncu.kazanma_serisi >= 3:
                o_kart.moral_guncelle(15)

            self.oyuncu.brans_kayip_serisi = 0
            self.oyuncu.son_brans = brans

            if o_kart.enerji < 30:
                puan += 5
            if o_kart.seviye_atladi_flag:
                puan += 5
                o_kart.seviye_atladi_flag = False
            if o_kart.clutch and o_kart in self.son_3_tur:
                puan += 5

            self.oyuncu.skor += puan

            if self.oyuncu.kazanma_serisi == 3:
                self.oyuncu.skor += 10
            elif self.oyuncu.kazanma_serisi == 5:
                self.oyuncu.skor += 20

            o_kart.enerji_guncelle("win")
            b_kart.enerji_guncelle("lose")
            o_kart.moral_guncelle(5)
            b_kart.moral_guncelle(-10)

            o_kart.kart_galibiyet += 1
            o_kart.deneyim_kazan(2)
            b_kart.deneyim_kazan(0)

        elif kazanan and kazanan.startswith("bilgisayar"):
            mesaj = {
                "bilgisayar": "Kaybettin!",
                "bilgisayar_ozel": "Özel yetenek bonusuyla Kaybettin!",
                "bilgisayar_yedek": "Yedek özelliklerle Kaybettin!",
                "bilgisayar_dayan": "Dayanıklılıkla Kaybettin!",
                "bilgisayar_enerji": "Enerji ile Kaybettin!",
                "bilgisayar_seviye": "Seviye ile Kaybettin!"
            }
            print(mesaj.get(kazanan, "Kaybettin!"))

            self.bilgisayar.skor += 10
            self.bilgisayar.toplam_galibiyet += 1
            self.bilgisayar.kazanma_serisi += 1
            self.bilgisayar.kaybetme_serisi = 0
            self.oyuncu.kazanma_serisi = 0
            self.bilgisayar.maks_galibiyet_serisi = max(
                self.bilgisayar.maks_galibiyet_serisi, self.bilgisayar.kazanma_serisi)

            self.oyuncu.kaybetme_serisi += 1
            if self.oyuncu.kaybetme_serisi == 2:
                o_kart.moral_guncelle(-10)

            if self.oyuncu.son_brans == brans:
                self.oyuncu.brans_kayip_serisi += 1
                if self.oyuncu.brans_kayip_serisi >= 2:
                    o_kart.moral_guncelle(-5)
            else:
                self.oyuncu.brans_kayip_serisi = 1
            self.oyuncu.son_brans = brans

            o_kart.enerji_guncelle("lose")
            b_kart.enerji_guncelle("win")
            o_kart.moral_guncelle(-5)
            b_kart.moral_guncelle(10)

            b_kart.kart_galibiyet += 1
            o_kart.deneyim_kazan(0)
            b_kart.deneyim_kazan(2)

        else:
            print("Tam berabere!")
            self.oyuncu.toplam_beraberlik += 1
            self.bilgisayar.toplam_beraberlik += 1
            o_kart.enerji_guncelle("draw")
            b_kart.enerji_guncelle("draw")
            # DÜZELTİLDİ: Beraberlik +1 deneyim
            o_kart.deneyim_kazan(1)
            b_kart.deneyim_kazan(1)

        print(f"\n{brans.upper()} TURU")
        print(f"Özellik: {ozellik}")
        print(f"{self.oyuncu.ad}: {o_puan}")
        print(f"Bilgisayar: {b_puan}")
        print(f"Tur Sonu Durumu:")
        print(f"{o_kart.ad} - Enerji: {o_kart.enerji}, Seviye: {o_kart.seviye}, Deneyim: {o_kart.deneyim}")
        print(f"{b_kart.ad} - Enerji: {b_kart.enerji}, Seviye: {b_kart.seviye}, Deneyim: {b_kart.deneyim}")
        print(f"Skor: {self.oyuncu.skor} - {self.bilgisayar.skor}")

        self.son_3_tur.append(o_kart)
        if len(self.son_3_tur) > 3:
            self.son_3_tur.pop(0)

        if o_puan > b_puan:
            self.istatistik.kaydet(i + 1, o_kart, b_kart, self.oyuncu.ad, ozellik, o_puan, b_puan)
        elif b_puan > o_puan:
            self.istatistik.kaydet(i + 1, o_kart, b_kart, self.bilgisayar.ad, ozellik, o_puan, b_puan)
        else:
            self.istatistik.kaydet(i + 1, o_kart, b_kart, "Berabere", ozellik, o_puan, b_puan)

        return {
            "kazanan": kazanan,
            "o_kart": o_kart,
            "b_kart": b_kart,
            "ozellik": ozellik,
            "o_puan": o_puan,
            "b_puan": b_puan,
            "brans": brans
        }

    def oyun_bitti_mi(self, tur_index):
        return tur_index >= self.TOPLAM_TUR

    def ozellik_listesi_gui(self, brans):
        """GUI için branşa ait özellik isimlerini döndürür"""
        if brans == "futbol":
            return ["penalti", "serbestVurus", "kaleciKarsiKarsiya"]
        elif brans == "basketbol":
            return ["ucluk", "ikilik", "serbestAtis"]
        elif brans == "voleybol":
            return ["servis", "blok", "smac"]
        return []


class MacIstatistik:
    def __init__(self):
        self.kayitlar = []

    def kaydet(self, tur_no, o_kart, b_kart, kazanan, ozellik="", o_puan=0, b_puan=0):
        self.kayitlar.append({
            "tur": tur_no,
            "oyuncu_kart": o_kart.ad,
            "bilgisayar_kart": b_kart.ad,
            "kazanan": kazanan,
            "ozellik": ozellik,
            "oyuncu_puan": o_puan,
            "bilgisayar_puan": b_puan
        })

    def rapor_olustur(self):
        print(f"\n{'='*60}")
        print(f"{'TUR':<5} {'OYUNCU KARTI':<22} {'BİLGİSAYAR KARTI':<22} {'KAZANAN':<15} {'SKOR'}")
        print(f"{'-'*60}")
        for k in self.kayitlar:
            print(f"{k['tur']:<5} {k['oyuncu_kart']:<22} {k['bilgisayar_kart']:<22} "
                  f"{k['kazanan']:<15} {k['oyuncu_puan']}-{k['bilgisayar_puan']}")
        print(f"{'='*60}")

    def rapor_listesi(self):
        """GUI için kayıtları liste olarak döndürür"""
        return self.kayitlar


def kart_detay(kart):
    print(f"Ad: {kart.ad}, Branş: {kart.brans}")
    print(f"Seviye: {kart.seviye}, Enerji: {kart.enerji}, Deneyim: {kart.deneyim}")
    if kart.ozel_yetenek:
        print(f"Özel Yetenek: {type(kart.ozel_yetenek).__name__}")
        print(f"Açıklama: {kart.ozel_yetenek.aciklama}")


def kazanani_belirle(o1, o2):
    print("\n--- OYUN SONU KARŞILAŞTIRMASI ---")

    if o1.skor != o2.skor:
        return o1 if o1.skor > o2.skor else o2

    print("Puanlar eşit! Detaylı inceleme yapılıyor...")

    if o1.toplam_galibiyet != o2.toplam_galibiyet:
        return o1 if o1.toplam_galibiyet > o2.toplam_galibiyet else o2

    if o1.maks_galibiyet_serisi != o2.maks_galibiyet_serisi:
        return o1 if o1.maks_galibiyet_serisi > o2.maks_galibiyet_serisi else o2

    o1_enerji = sum(k.enerji for k in o1.kartlar)
    o2_enerji = sum(k.enerji for k in o2.kartlar)
    if o1_enerji != o2_enerji:
        return o1 if o1_enerji > o2_enerji else o2

    o1_seviye3 = sum(1 for k in o1.kartlar if k.seviye == 3)
    o2_seviye3 = sum(1 for k in o2.kartlar if k.seviye == 3)
    if o1_seviye3 != o2_seviye3:
        return o1 if o1_seviye3 > o2_seviye3 else o2

    if o1.ozel_yetenek_galibiyet != o2.ozel_yetenek_galibiyet:
        return o1 if o1.ozel_yetenek_galibiyet > o2.ozel_yetenek_galibiyet else o2

    if o1.toplam_beraberlik != o2.toplam_beraberlik:
        return o1 if o1.toplam_beraberlik < o2.toplam_beraberlik else o2

    return None  # Tam beraberlik


class Oyun:
    def __init__(self):
        from PyQt5.QtWidgets import QApplication
        from kart import TestApp

        self.app = QApplication([])
        self.kullanici = Kullanici("Sen")
        self.bilgisayar = Bilgisayar("Bilgisayar", strateji=OrtaStrateji())
        self.tur_index = 0

        self.oyun_yonetici = OyunYonetici(self.kullanici, self.bilgisayar)

        self.gui = TestApp(self.oyun_yonetici, self.kart_secildi)
        self.gui.show()

    def kart_secildi(self, kart, secilen_ozellik=None):
        if self.oyun_yonetici.oyun_bitti_mi(self.tur_index):
            self._oyun_bitis()
            return

        print("Seçilen kart:", kart.ad)
        secilen_kart_objesi = next(
            (k for k in self.oyun_yonetici.oyuncu.kartlar if k.ad == kart.ad), None)

        if secilen_kart_objesi is None:
            print("Seçilen kart bulunamadı!")
            return

        sonuc = self.oyun_yonetici.tur_oyna(
            i=self.tur_index,
            secilen_kart=secilen_kart_objesi,
            secilen_ozellik=secilen_ozellik
        )
        self.tur_index += 1

        if hasattr(self.gui, 'tur_sonucu_goster') and sonuc:
            self.gui.tur_sonucu_goster(sonuc, self.tur_index)

        if self.oyun_yonetici.oyun_bitti_mi(self.tur_index):
            self._oyun_bitis()

    def _oyun_bitis(self):
        kazanan = kazanani_belirle(self.kullanici, self.bilgisayar)
        print("\n========== OYUN BİTTİ ==========")
        print(f"Final Skor: {self.kullanici.ad}: {self.kullanici.skor} - "
              f"{self.bilgisayar.ad}: {self.bilgisayar.skor}")
        if kazanan:
            print(f" Kazanan: {kazanan.ad}")
        else:
            print(" Oyun berabere bitti!")
        print("\n--- Maç İstatistikleri ---")
        self.oyun_yonetici.istatistik.rapor_olustur()

        if hasattr(self.gui, 'oyun_bitis_goster'):
            self.gui.oyun_bitis_goster(
                self.kullanici, self.bilgisayar, kazanan,
                self.oyun_yonetici.istatistik.rapor_listesi()
            )


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    oyun = Oyun()
    oyun.app.exec_()                             
