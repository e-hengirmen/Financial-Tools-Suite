import math
import os

INPUT_FILE = "processed_data.txt"
OUTPUT_FILE = "grouped_data.txt"

# --- DİNAMİK PARAMETRELER ---
# T-1 (kümülatif arefe) veya T gününde bu orandan fazla (veya eşit) oynayan hisseler "Aykırı Değer" kabul edilir.
OUTLIER_THRESHOLD = 9.5


def parse_percentage(val_str):
    """'+1.24%' veya '-2.06%' gibi stringleri float sayıya çevirir."""
    return float(val_str.replace("%", "").replace("+", "").strip())


if not os.path.exists(INPUT_FILE):
    print(
        f"Hata: '{INPUT_FILE}' dosyası bulunamadı! Lütfen önce verileri işleyen scripti çalıştırın."
    )
    exit()

# Gruplar ve havuzlar
grup_notr = []
grup_pozitif = []
grup_negatif = []
tum_hisseler = []
temizlenmis_hisseler = []  # Parametreye göre filtrelenmiş temiz havuz

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    parts = line.strip().split()
    # Başlık veya ortalama satırlarını atla, dikey çizgi içeren ham parçaları güvenle işle
    if not parts or parts[0] in ["Hisse", "AVERAGE", "GEOMETRIC"] or "-" in parts[0]:
        continue

    # Eğer satırda daha önce eklenmiş ayraçlar (|) varsa onları temizle
    parts = [p for p in parts if p != "|"]

    try:
        ticker = parts[0]
        tarih = parts[1]
        verim = parse_percentage(parts[2])

        # Sadece %2 ve üstü temettü verenler önemli
        if verim < 2.0:
            continue

        # 3 parçalı yapıya göre sütun eşleşmeleri
        c_m3 = parse_percentage(parts[3])  # T-3
        c_m2 = parse_percentage(parts[4])  # T-2
        c_m1 = parse_percentage(parts[5])  # T-1 (Sol grubun kümülatif zirvesi)
        c_t = parse_percentage(parts[6])  # T_Günü (Orta grup bağımsız)
        c_p1 = parse_percentage(parts[7])  # T+1 (Sağ grup kümülatif)
        c_p2 = parse_percentage(parts[8])  # T+2 (Sağ grup kümülatif)
        c_p3 = parse_percentage(parts[9])  # T+3 (Sağ grup kümülatif)

        # --- NET ETKİ HESAPLAMA ---
        net_etki = verim + c_t

        # --- RELATIVE %10 GRUPLAMA MANTIĞI ---
        teorik_dusus = -verim
        tolerans = abs(teorik_dusus) * 0.10

        ust_sinir = teorik_dusus + tolerans
        alt_sinir = teorik_dusus - tolerans

        hisse_data = {
            "ticker": ticker,
            "tarih": tarih,
            "verim": verim,
            "net_etki": net_etki,
            "c_m3": c_m3,
            "c_m2": c_m2,
            "c_m1": c_m1,
            "c_t": c_t,
            "c_p1": c_p1,
            "c_p2": c_p2,
            "c_p3": c_p3,
        }

        # Ham genel havuza ekle
        tum_hisseler.append(hisse_data)

        # --- DİNAMİK AYKIRI DEĞER (OUTLIER) FİLTRESİ ---
        if abs(c_m1) < OUTLIER_THRESHOLD and abs(c_t) < OUTLIER_THRESHOLD:
            temizlenmis_hisseler.append(hisse_data)

        # Mikro gruplara T_Günü performansına göre dağıt
        if alt_sinir <= c_t <= ust_sinir:
            grup_notr.append(hisse_data)
        elif c_t > ust_sinir:
            grup_pozitif.append(hisse_data)
        else:
            grup_negatif.append(hisse_data)

    except Exception:
        continue


def write_grup_to_file(file_handle, grup_adi, grup_listesi):
    """Belirtilen listeyi 3 parçalı izole gruplara (dikey ayraçlı) ayırarak dosyaya yazar."""
    file_handle.write(
        f"=== {grup_adi} (Hisse Sayısı: {len(grup_listesi)}) ===\n"
    )

    if not grup_listesi:
        file_handle.write("Bu grupta kriterlere uyan hisse bulunamadı.\n\n")
        return

    # Sütunları net ayırmak için dikey çizgili (|) başlık yapısı
    header = f"{'Hisse':<9} {'Temettü Tar':<12} {'Verim':<7} | {'T-3':<7} {'T-2':<7} {'T-1':<7} | {'T_Günü':<8} {'Net_Etki':<9} | {'T+1':<7} {'T+2':<7} {'T+3':<7}\n"
    file_handle.write(header)
    file_handle.write("-" * len(header.strip()) + "\n")

    # Aritmetik Toplam Değişkenleri
    sum_verim, sum_net, sum_m3, sum_m2, sum_m1, sum_t, sum_p1, sum_p2, sum_p3 = (
        0, 0, 0, 0, 0, 0, 0, 0, 0
    )

    # Geometrik Çarpım Değişkenleri (Başlangıç değeri 1 olan faktörler)
    prod_verim, prod_net, prod_m3, prod_m2, prod_m1, prod_t, prod_p1, prod_p2, prod_p3 = (
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0
    )

    for h in grup_listesi:
        file_handle.write(
            f"{h['ticker']:<9} {h['tarih']:<12} %{h['verim']:<5.2f} | "
            f"{h['c_m3']:+6.2f}% {h['c_m2']:+6.2f}% {h['c_m1']:+6.2f}% | "
            f"{h['c_t']:+7.2f}% {h['net_etki']:+8.2f}% | "
            f"{h['c_p1']:+6.2f}% {h['c_p2']:+6.2f}% {h['c_p3']:+6.2f}%\n"
        )
        
        # 1. Aritmetik Toplama Yapılıyor
        sum_verim += h["verim"]
        sum_net += h["net_etki"]
        sum_m3 += h["c_m3"]
        sum_m2 += h["c_m2"]
        sum_m1 += h["c_m1"]
        sum_t += h["c_t"]
        sum_p1 += h["c_p1"]
        sum_p2 += h["c_p2"]
        sum_p3 += h["c_p3"]

        # 2. Geometrik Çarpan Dönüşümü Yapılıyor (1 + R/100)
        prod_verim *= (1 + h["verim"] / 100)
        prod_net *= (1 + h["net_etki"] / 100)
        prod_m3 *= (1 + h["c_m3"] / 100)
        prod_m2 *= (1 + h["c_m2"] / 100)
        prod_m1 *= (1 + h["c_m1"] / 100)
        prod_t *= (1 + h["c_t"] / 100)
        prod_p1 *= (1 + h["c_p1"] / 100)
        prod_p2 *= (1 + h["c_p2"] / 100)
        prod_p3 *= (1 + h["c_p3"] / 100)

    n = len(grup_listesi)
    file_handle.write("-" * len(header.strip()) + "\n")

    # --- 1. SATIR: ARİTMETİK ORTALAMA (AVERAGE) ---
    file_handle.write(
        f"{'AVERAGE':<9} {'':<12} %{sum_verim/n:<5.2f} | "
        f"{sum_m3/n:+6.2f}% {sum_m2/n:+6.2f}% {sum_m1/n:+6.2f}% | "
        f"{sum_t/n:+7.2f}% {sum_net/n:+8.2f}% | "
        f"{sum_p1/n:+6.2f}% {sum_p2/n:+6.2f}% {sum_p3/n:+6.2f}%\n"
    )

    # --- 2. SATIR: GEOMETRİK ORTALAMA (GEOMETRIC) ---
    def format_geo(prod_val, count, width, has_sign=True):
        """Kök hesaplayıp stringe sağa hizalı tam genişlik verir, yüzdelik işaretini ekler."""
        if prod_val <= 0:
            return f"{'------%':>{width}}"
        geo_pct = (math.pow(prod_val, 1.0 / count) - 1) * 100
        sign_str = "+" if geo_pct >= 0 and has_sign else ""
        res_str = f"{sign_str}{geo_pct:.2f}%"
        return f"{res_str:>{width}}"

    # Verim sütunu için '%3.69%' yapısı (Yüzde işareti dışarıda değil, iç formatta çözülüyor)
    if prod_verim <= 0:
        geo_verim_str = f"{'------%':>6}"
    else:
        geo_verim_pct = (math.pow(prod_verim, 1.0 / n) - 1) * 100
        geo_verim_str = f"{geo_verim_pct:.2f}%"

    file_handle.write(
        f"{'GEOMETRIC':<9} {'':<12} %{geo_verim_str:<5} | "
        f"{format_geo(prod_m3, n, 6)} {format_geo(prod_m2, n, 6)} {format_geo(prod_m1, n, 6)} | "
        f"{format_geo(prod_t, n, 7)} {format_geo(prod_net, n, 8)} | "
        f"{format_geo(prod_p1, n, 6)} {format_geo(prod_p2, n, 6)} {format_geo(prod_p3, n, 6)}\n"
    )

    file_handle.write("\n" + "=" * len(header.strip()) + "\n\n")


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(
        "===================================================================================================\n"
    )
    f.write(
        "                 TEMETTÜ İZOLASYONLU İŞ GÜNÜ GRUPLAMA RAPORU (Verim >= %2)                       \n"
    )
    f.write(
        "         (Önceki Günler: T-4 Tabanlı Kümülatif | Sonraki Günler: T-1 Tabanlı Kümülatif)            \n"
    )
    f.write(
        "===================================================================================================\n\n"
    )

    # 1. Özel Gruplar
    write_grup_to_file(
        f,
        "1. GRUP: NÖTR (Temettü Günü Beklenen Kadar Düşenler - Relative +-%10)",
        grup_notr,
    )
    write_grup_to_file(
        f,
        "2. GRUP: POZİTİF (Temettü Günü Beklenenden Az Düşenler veya Artanlar)",
        grup_pozitif,
    )
    write_grup_to_file(
        f,
        "3. GRUP: NEGATİF (Temettü Günü Beklenenden Fazla Düşenler)",
        grup_negatif,
    )

    # 2. Ham Genel Havuz
    write_grup_to_file(
        f,
        "GENEL ÖZET: TÜM TEMETTÜ HİSSELERİ (Ham Veri - Kriter: Verim >= %2)",
        tum_hisseler,
    )

    # 3. Filtrelenmiş Genel Havuz
    write_grup_to_file(
        f,
        f"FİLTRELENMİŞ ÖZET: ANOMALİLERDEN ARINDIRILMIŞ (T-1 veya T Gününde %{OUTLIER_THRESHOLD} Üstü Oynayanlar Çıkarıldı)",
        temizlenmis_hisseler,
    )

print(
    f"İşlem tamamlandı! Filtre eşiği %{OUTLIER_THRESHOLD} olarak uygulandı, her iki ortalama türü hesaplandı ve '{OUTPUT_FILE}' dosyasına yazıldı."
)