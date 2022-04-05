import pygame
import os
import random

pygame.font.init()  # font kullanabilmek için başlatma

genislik = 800  # pencere genişliği
yukseklik = 600  # pencere yüksekliği
FPS = 60


girisEkranCalisma = True  # oyunun açık-kapalı durumu için
hareketTipi = True  # klavye - fare için

pencere = pygame.display.set_mode((genislik, yukseklik))  # oyunun çalışacağı pencere

# fotoğrafların yüklenmesi :
# arka plan:
arkaPlan = pygame.image.load(os.path.join("pngDosyalari", "arkaPlan.png"))

# uzay gemimiz:
uzayGemisi = pygame.image.load(os.path.join("pngDosyalari", "uzayGemisi.png"))

# asteroidler:
asteroid1 = pygame.image.load(os.path.join("pngDosyalari", "asteroid1.png"))
asteroid2 = pygame.image.load(os.path.join("pngDosyalari", "asteroid2.png"))
asteroid3 = pygame.image.load(os.path.join("pngDosyalari", "asteroid3.png"))

# ates topları:
atesTopu1 = pygame.image.load(os.path.join("pngDosyalari", "atesTopu1.png"))
atesTopu2 = pygame.image.load(os.path.join("pngDosyalari", "atesTopu2.png"))
atesTopu3 = pygame.image.load(os.path.join("pngDosyalari", "atesTopu3.png"))

# soru isareti:
soruIsaretiResim = pygame.image.load(os.path.join("pngDosyalari", "soruIsareti.png"))


def carpisma(obje1, obje2):
    offset_x = obje2.x - obje1.x
    offset_y = obje2.y - obje1.y
    return obje1.mask.overlap(obje2.mask, (offset_x, offset_y)) #çarpışma kontrol


# uzay gemimizi üreteceğimiz sınıf:
class Gemi:
    # yapıcı fonksiyon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.can = 100
        self.gemiResmi = uzayGemisi
        self.atesTopuResmi = atesTopu1
        self.hasar = 10
        self.skor = 0
        self.oyuncuHizi = 5
        self.atesTopum = []
        self.atesTopuResmi = atesTopu1
        self.ATES_SOGUMA = 30
        self.kullanilanHak = 0
        self.mask = pygame.mask.from_surface(self.gemiResmi)

    # ates topu uret
    def ates(self):
        self.ATES_SOGUMA = 0
        atesTopumN = atesTopu(self.x, self.y, self.atesTopuResmi)
        self.atesTopum.append(atesTopumN)

    # ates topu hareket
    def atesHareket(self, hiz, objeler, objeler2):
        for ates in self.atesTopum:
            ates.hareket(hiz)
            # ateş topu asteroidlere çarptımı  kontrolü
            for obje in objeler:
                if ates.vurma(obje):
                    obje.can -= self.hasar
                    if ates in self.atesTopum:  # hata vermemesi için varsa siliyor
                        self.atesTopum.remove(ates)
            # ateş topu soru işaretlerine çarptımı kontrolü
            for obje2 in objeler2:
                if ates.vurma(obje2):
                    obje2.can -= self.hasar
                    if ates in self.atesTopum:  # hata vermemesi için varsa siliyor
                        self.atesTopum.remove(ates)

    # geminin ekrana çizilmesi için çağıracağımız fonksiyon:
    def ciz(self, window):
        window.blit(self.gemiResmi, (self.x, self.y))
        for ates in self.atesTopum:
            ates.ciz(window)


class Asteroids:
    SERTLIK = {
        "yumusak": (asteroid1, 10, 10),
        "orta": (asteroid2, 20, 20),
        "sert": (asteroid3, 30, 30)
    }

    def __init__(self, x, y, sertlik):
        self.x = x
        self.y = y
        self.asteroidResmi, self.hasar, self.can = self.SERTLIK[sertlik]
        self.mask = pygame.mask.from_surface(self.asteroidResmi)

    def ciz(self, window):
        window.blit(self.asteroidResmi, (self.x, self.y))

    def hareket(self, hiz):
        self.y += hiz

# ateş ettiğimiz ates toplarımızın türeyeceği sınıf
class atesTopu:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.resim = image
        self.mask = pygame.mask.from_surface(self.resim)

    def hareket(self, hiz):
        self.y -= hiz

    def ciz(self, window):
        window.blit(self.resim, (self.x + 8, self.y - 21))

    def vurma(self, obje):
        return carpisma(obje, self)


class soruIsareti:
    TUR = {
        "canVeren": (20, 0),
        "canAlan": (-20, 0),
        "skorVeren": (0, 50),
        "skorAlan": (0, -25)
    }

    def __init__(self, x, y, tur):
        self.x = x
        self.y = y
        self.canEtkisi, self.skorEtkisi = self.TUR[tur]
        self.can = 1
        self.resim = soruIsaretiResim
        self.mask = pygame.mask.from_surface(self.resim)

    def ciz(self, window):
        window.blit(self.resim, (self.x, self.y))

    def hareket(self):
        self.y += 10


def main():
    calisma = True
    asteroidler = []
    asteroidHizi = 2
    asteroidSayisi = 0
    soruIsaretleri = []
    kalanHak = 0
    ekranBekletme = 0

    ATESSOGUMA = 30  # saniyedeki atış sayısını sınırlamak için

    dalga = 0
    main_font = pygame.font.SysFont("Algerian", 30)
    kaybetme_font = pygame.font.SysFont("Algerian", 90)

    kaybetme = False
    kaybetme_ekrani_sure = 0
    clock = pygame.time.Clock()
    # oyuncu nesnemizi oluşturuyoruz
    oyuncu = Gemi(360, 500)

    def cizimler():
        # arka plan resminin çizilmesi/koyulması:
        pencere.blit(arkaPlan, (0, 0))

        # uzay gemimizi çizen fonksiyon:
        oyuncu.ciz(pencere)

        # asteroidlerin çizilmesi:
        for asteroid in asteroidler:
            asteroid.ciz(pencere)

        # soru işaretlerinin çizilmesi
        for hediye in soruIsaretleri:
            hediye.ciz(pencere)

        can_label = main_font.render("Can: {}".format(oyuncu.can), True, (255, 255, 255))
        pencere.blit(can_label, (10, 10))
        skor_label = main_font.render("Skor: {}".format(oyuncu.skor), True, (255, 255, 255))
        pencere.blit(skor_label, (10, 40))
        dalga_label = main_font.render("Dalga: {}".format(dalga), True, (255, 255, 255))
        pencere.blit(dalga_label, (690, 10))
        kalanHak_label = main_font.render("Kalan Hak: {}".format(kalanHak - oyuncu.kullanilanHak), True,
                                          (255, 255, 255))
        pencere.blit(kalanHak_label, (10, 70))

        if kaybetme:
            kaybetme_label = kaybetme_font.render("OYUN BİTTİ", True, (255, 0, 0))
            pencere.blit(kaybetme_label, (int(genislik / 2 - (kaybetme_label.get_width() / 2)),
                                          int(yukseklik / 2 - (kaybetme_label.get_height() / 2))))
            skor_bitti = main_font.render("Skor : {}".format(oyuncu.skor), True, (255, 0, 0))
            pencere.blit(skor_bitti, (kaybetme_label.get_width() + 20, kaybetme_label.get_height() + 260))
        # pencerede çizimlerin görünmesi için pencereyi güncelliyoruz:
        pygame.display.update()

    while calisma:
        # FPS değerinin ayarlanması
        clock.tick(60)
        cizimler()
        global girisEkranCalisma

        kalanHak = int(oyuncu.skor / 1000)  # her 1000 skor için öldüğünde kaldığı yerden devam etme hakkı
        # kaybedince ekrana çıkacaklar 5 sn süreyle
        if oyuncu.can <= 0:
            if kalanHak - oyuncu.kullanilanHak > 0:
                ekranBekletme += 1
                if ekranBekletme >= FPS:  # öldüğünde 1 saniye bekletiyor
                    ekranBekletme = 0
                    oyuncu.can = 100
                    oyuncu.kullanilanHak += 1
                else:
                    continue
            else:
                kaybetme = True
                if kaybetme:
                    kaybetme_ekrani_sure += 1
                    if kaybetme_ekrani_sure >= FPS * 3:
                        calisma = False
                    else:
                        continue

        # yeni dalga için tüm asteroidler yok edilmiş ya da ekrandan çıkmış olmalı:
        if len(asteroidler) == 0:
            dalga += 1
            if asteroidHizi <= 10 and (dalga % 3) - 1 == 0 and dalga != 1:
                asteroidHizi += 1  # her dalgada asteroid hızlari artar
            asteroidSayisi += 5  # her dalgada asteroid sayısı 5 artar

            for i in range(asteroidSayisi):  # her dalgadaki asteroidlerin oluşturulması
                asteroid = Asteroids(random.randrange(1, 700), random.randrange(-300 * dalga, -100),
                                     random.choice(["yumusak", "orta", "sert"]))
                asteroidler.append(asteroid)  # asteroidler listesine oluşturulan asteroidi ekle
            for i in range(dalga):
                hediye = soruIsareti(random.randrange(1, 700), random.randrange(-600 * dalga, -500),
                                     random.choice(["canVeren", "canAlan", "skorVeren", "skorAlan"]))
                soruIsaretleri.append(hediye)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisma = False
                girisEkranCalisma = False  # çarpıya tıklandığında başlangıç ekranına dönmemesi için

        oyuncu.ATES_SOGUMA += 1
        # basılan tuşu atıyoruz:
        keys = pygame.key.get_pressed()
        # fare tıklama kontrolleri
        tiklama = pygame.mouse.get_pressed()

        if hareketTipi:
            # hangi tuşa basınca hangi hareketi yapacağımızı ayarlayan kodlar:
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and oyuncu.x > 0:
                oyuncu.x -= oyuncu.oyuncuHizi
            if keys[pygame.K_RIGHT] or keys[pygame.K_d] and oyuncu.x < 720:
                oyuncu.x += oyuncu.oyuncuHizi
            if keys[pygame.K_UP] or keys[pygame.K_w] and oyuncu.y > 0:
                oyuncu.y -= oyuncu.oyuncuHizi
            if keys[pygame.K_DOWN] or keys[pygame.K_s] and oyuncu.y < 520:
                oyuncu.y += oyuncu.oyuncuHizi
            if keys[pygame.K_SPACE]:
                if oyuncu.ATES_SOGUMA >= ATESSOGUMA:
                    oyuncu.ates()
                else:
                    pass
        else:
            # farenin olduğu bölgeye uzay gemisinin hareketi:
            fareX , fareY = pygame.mouse.get_pos()
            oyuncu.x = fareX-35
            oyuncu.y = fareY-35
            if tiklama[0]: # tiklamanin 0. değeri (sol tıklama) True olursa ateş et
                if oyuncu.ATES_SOGUMA >= ATESSOGUMA:
                    oyuncu.ates()
                else:
                    pass

        # asteroidler ekrandan çıktığında ya da bizle çarpıştığında asteroid siliniyor
        for asteroid in asteroidler:
            asteroid.hareket(asteroidHizi)  # asteroidler aşağı doğru kayar
            if carpisma(asteroid, oyuncu):
                oyuncu.can -= asteroid.hasar
                asteroidler.remove(asteroid)
            if asteroid.y > yukseklik:  # ekrandan çıkan asteroidleri siliyoruz
                asteroidler.remove(asteroid)

        # soru işareti ekrandan çıktığında ya da bizle çarpıştığında
        for hediye in soruIsaretleri:
            hediye.hareket()
            if carpisma(hediye, oyuncu):
                oyuncu.can += hediye.canEtkisi
                oyuncu.skor += hediye.skorEtkisi
                soruIsaretleri.remove(hediye)
            if hediye.y > yukseklik:
                soruIsaretleri.remove(hediye)

        oyuncu.atesHareket(oyuncu.oyuncuHizi * 1.5, asteroidler, soruIsaretleri)

        # asteroidleri vurunca olan olaylar:
        for asteroid in asteroidler:
            if asteroid.can <= 0:
                oyuncu.skor += asteroid.hasar
                oyuncu.can += 1
                asteroidler.remove(asteroid)

        # soru işareti vurulunca olanlar:
        for hediye in soruIsaretleri:
            if hediye.can <= 0:
                oyuncu.skor += hediye.skorEtkisi
                oyuncu.can += hediye.canEtkisi
                soruIsaretleri.remove(hediye)

        # ekrandan çıkan ates toplarını siliyor
        for ates in oyuncu.atesTopum:
            if ates.y < 0:
                oyuncu.atesTopum.remove(ates)

        # skor arttıkça oyuncuya verilecek olan ödüller
        if oyuncu.skor >= 250 and oyuncu.skor < 500:
            ATESSOGUMA = 20  # saniyedeki atış miktarı 3e çıkar
            oyuncu.oyuncuHizi = 7  # oyuncunun hızı 7 ye çıkar
        elif oyuncu.skor >= 500 and oyuncu.skor < 1500:
            oyuncu.atesTopuResmi = atesTopu2  # 2. ateş topuna geçer
            oyuncu.hasar = 20
            ATESSOGUMA = 15  # saniyedeki atış miktarı 4 e çıkar
            oyuncu.oyuncuHizi = 10  # oyuncunun hızı 10 a çıkar
        elif oyuncu.skor >= 1500:
            oyuncu.atesTopuResmi = atesTopu3
            oyuncu.hasar = 30
            ATESSOGUMA = 10  # saniyedeki atış miktarı 6 ya çıkar
            oyuncu.oyuncuHizi = 13  # oyuncunun hızı 13e çıkar


# oyun başlamadan önceki ekranımız:
def anaEkran():
    yazi_fontu = pygame.font.SysFont("Algerian", 45)
    global girisEkranCalisma
    global hareketTipi
    while girisEkranCalisma:
        pencere.blit(arkaPlan, (0, 0))

        giris_yazisi = yazi_fontu.render("Klavye ile oynamak için \"k\" tuşuna basınız", True, (255, 255, 255))
        pencere.blit(giris_yazisi, (
        int(genislik / 2 - (giris_yazisi.get_width() / 2)), int(yukseklik / 2 - (giris_yazisi.get_height() / 2))-int(giris_yazisi.get_height())))
        giris_yazisi2 = yazi_fontu.render("Fare ile oynamak için \"m\" tuşuna basınız", True, (255, 255, 255))
        pencere.blit(giris_yazisi2,(int(genislik / 2 - (giris_yazisi2.get_width() / 2)), int(yukseklik / 2 - (giris_yazisi.get_height() / 2))+int(giris_yazisi.get_height())))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                girisEkranCalisma = False

        #oyun başlangıcında hangi kontrol ile oynayacağımızı seçtiğimiz kısım:
        key = pygame.key.get_pressed()
        if key[pygame.K_k]:
            hareketTipi = True
            main()
        elif key[pygame.K_m]:
            hareketTipi = False
            main()

    pygame.quit()


anaEkran()
