import os
import re

# Dosya isimleri
INPUT_FILE = "raw_data.txt"
OUTPUT_FILE = "data.txt"

# Türkçe ay isimlerini sayısal formata dönüştürme sözlüğü
aylar = {
    "Oca": "01",
    "Şub": "02",
    "Mar": "03",
    "Nis": "04",
    "May": "05",
    "Haz": "06",
    "Tem": "07",
    "Ağu": "08",
    "Eyl": "09",
    "Eki": "10",
    "Kas": "11",
    "Ara": "12",
}

# Giriş dosyası kontrolü
if not os.path.exists(INPUT_FILE):
    print(
        f"Hata: '{INPUT_FILE}' dosyası bulunamadı! Lütfen veriyi bu isimde bir dosyaya kaydedip tekrar dene."
    )
    exit()

# Dosyadan satırları oku ve temizle
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    satirlar = [s.strip() for s in f.readlines() if s.strip()]

temiz_liste = []
current_ticker = None
current_date = None
current_yield = None

# Satır satır tüm metni tarayan durum makinesi
for idx, satir in enumerate(satirlar):

    # 1. Durum: Satır 3 ila 5 karakter arası tamamen büyük harf ise bu yeni bir TICKER'dır.
    if re.match(r"^[A-Z]{3,5}$", satir):
        # Eğer halihazırda biriktirdiğimiz bir önceki veri eksiksizse listeye ekle
        if current_ticker and current_date and current_yield:
            temiz_liste.append((current_ticker, current_date, current_yield))

        # Yeni hisseye geçiş yapıyoruz, hafızayı sıfırla
        current_ticker = satir
        current_date = None
        current_yield = None
        continue

    # 2. Durum: Satır "Tarih" ise, bir sonraki satır o hissenin tarih değeridir.
    if satir == "Tarih" and idx + 1 < len(satirlar):
        tarih_metni = satirlar[idx + 1]  # Örn: "06 Oca 2025"
        parcalar = tarih_metni.split()
        if len(parcalar) == 3:
            gun = parcalar[0].zfill(2)
            ay = aylar.get(parcalar[1], "01")
            yil = parcalar[2]
            current_date = f"{yil}-{ay}-{gun}"  # YYYY-MM-DD formatı

    # 3. Durum: Satır "Verim (Net)" ise, bir sonraki satır verim yüzdesidir.
    if "Verim (Net)" in satir and idx + 1 < len(satirlar):
        # Örn: "%0,81" -> "0.81" haline getiriyoruz (% işaretini siliyoruz)
        current_yield = (
            satirlar[idx + 1].replace("%", "").replace(",", ".").strip()
        )

# Son kalan entry'yi de listeye ekle
if current_ticker and current_date and current_yield:
    temiz_liste.append((current_ticker, current_date, current_yield))

# Sonuçları data.txt dosyasına yazdır (Header yok, saf veri)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for ticker, tarih, verim in temiz_liste:
        # Aralarında sadece birer boşluk bırakarak yazar, başka kodların split() etmesi kolay olur
        f.write(f"{ticker} {tarih} {verim}\n")

print(
    f"İşlem tamamlandı! {len(temiz_liste)} adet saf veri satırı '{OUTPUT_FILE}' dosyasına yazıldı."
)