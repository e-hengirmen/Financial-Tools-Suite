import math
import os

# --- DİNAMİK PARAMETRELER ---
INPUT_FILE = "processed_data.txt"
OUTPUT_FILE = "grouped_data.txt"
OUTLIER_THRESHOLD = 9.5


def parse_percentage(val_str):
    """'+1.24%' veya '-2.06%' gibi stringleri float sayıya çevirir."""
    return float(val_str.replace("%", "").replace("+", "").strip())


def format_geo(prod_val, count, width, has_sign=True):
    """Kök hesaplayıp stringe sağa hizalı tam genişlik verir, yüzdelik işaretini ekler."""
    if prod_val <= 0:
        return f"{'------%':>{width}}"
    geo_pct = (math.pow(prod_val, 1.0 / count) - 1) * 100
    sign_str = "+" if geo_pct >= 0 and has_sign else ""
    res_str = f"{sign_str}{geo_pct:.2f}%"
    return f"{res_str:>{width}}"


def write_grup_to_file(file_handle, grup_adi, grup_listesi):
    """Belirtilen listeyi 3 parçalı izole gruplara (dikey ayraçlı) ayırarak dosyaya yazar ve aggregate verileri hesaplar."""
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


def generate_dividend_report(input_path, output_path, outlier_threshold=9.5):
    """
    Belirtilen girdi dosyasından temettü verilerini okur, dinamik dilimlere göre gruplar,
    istatistiksel özetleri (aggregate) hesaplar ve hedef dosyaya raporlar.
    """
    if not os.path.exists(input_path):
        print(f"Hata: '{input_path}' dosyası bulunamadı!")
        return

    grup_notr = []
    grup_pozitif = []
    grup_negatif = []
    tum_hisseler = []
    temizlenmis_hisseler = []
    
    max_verim = 2.0  # Dinamik aralık tespiti için maksimum verim takibi

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        if not parts or parts[0] in ["Hisse", "AVERAGE", "GEOMETRIC"] or "-" in parts[0]:
            continue

        parts = [p for p in parts if p != "|"]

        try:
            ticker = parts[0]
            tarih = parts[1]
            verim = parse_percentage(parts[2])

            if verim < 2.0:
                continue
                
            if verim > max_verim:
                max_verim = verim

            c_m3 = parse_percentage(parts[3])
            c_m2 = parse_percentage(parts[4])
            c_m1 = parse_percentage(parts[5])
            c_t = parse_percentage(parts[6])
            c_p1 = parse_percentage(parts[7])
            c_p2 = parse_percentage(parts[8])
            c_p3 = parse_percentage(parts[9])

            net_etki = verim + c_t
            teorik_dusus = -verim
            tolerans = abs(teorik_dusus) * 0.10

            ust_sinir = teorik_dusus + tolerans
            alt_sinir = teorik_dusus - tolerans

            hisse_data = {
                "ticker": ticker, "tarih": tarih, "verim": verim, "net_etki": net_etki,
                "c_m3": c_m3, "c_m2": c_m2, "c_m1": c_m1, "c_t": c_t,
                "c_p1": c_p1, "c_p2": c_p2, "c_p3": c_p3
            }

            tum_hisseler.append(hisse_data)

            if abs(c_m1) < outlier_threshold and abs(c_t) < outlier_threshold:
                temizlenmis_hisseler.append(hisse_data)

            if alt_sinir <= c_t <= ust_sinir:
                grup_notr.append(hisse_data)
            elif c_t > ust_sinir:
                grup_pozitif.append(hisse_data)
            else:
                grup_negatif.append(hisse_data)

        except Exception:
            continue

    # --- DİNAMİK VERİM ARALIKLARI OLUŞTURMA ---
    # Örneğin max_verim 7.4 ise aralıklar: [2, 3), [3, 4), [4, 5), [5, 6), [6, 7), [7, 8) olacak.
    verim_araliklari = {}
    baslangic = 2
    bitis = math.ceil(max_verim)
    
    for i in range(baslangic, bitis):
        verim_araliklari[(i, i+1)] = []
        
    for h in tum_hisseler:
        v = h["verim"]
        for (alt, ust) in verim_araliklari.keys():
            if alt <= v < ust:
                verim_araliklari[(alt, ust)].append(h)
                break
            # Eğer tam sınırda veya dışarıda kalan uç bir durum varsa son aralığa dahil et
            elif ust == bitis and v >= ust:
                verim_araliklari[(alt, ust)].append(h)
                break

    # Dosyaya Rapor Yazma Aşaması
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("===================================================================================================\n")
        f.write("                  TEMETTÜ İZOLASYONLU İŞ GÜNÜ GRUPLAMA RAPORU (Verim >= %2)                       \n")
        f.write("         (Önceki Günler: T-4 Tabanlı Kümülatif | Sonraki Günler: T-1 Tabanlı Kümülatif)            \n")
        f.write("===================================================================================================\n\n")

        # 1. Ana Mikro Gruplar
        write_grup_to_file(f, "1. GRUP: NÖTR (Temettü Günü Beklenen Kadar Düşenler - Relative +-%10)", grup_notr)
        write_grup_to_file(f, "2. GRUP: POZİTİF (Temettü Günü Beklenenden Az Düşenler veya Artanlar)", grup_pozitif)
        write_grup_to_file(f, "3. GRUP: NEGATİF (Temettü Günü Beklenenden Fazla Düşenler)", grup_negatif)

        f.write("===================================================================================================\n")
        f.write("                           DİNAMİK TEMETTÜ VERİM ARALIKLARI RAPORU                                 \n")
        f.write("===================================================================================================\n\n")

        # 2. Dinamik Aralık Tabloları (İstediğin gibi Negatif gruptan hemen sonra ekleniyor)
        for (alt, ust), grup_listesi in sorted(verim_araliklari.items()):
            write_grup_to_file(f, f"TEMETTÜ VERİM ARALIĞI: %{alt} - %{ust} ARASI", grup_listesi)

        # 3. Genel Özet Havuzları
        write_grup_to_file(f, "GENEL ÖZET: TÜM TEMETTÜ HİSSELERİ (Ham Veri - Kriter: Verim >= %2)", tum_hisseler)
        write_grup_to_file(f, f"FİLTRELENMİŞ ÖZET: ANOMALİLERDEN ARINDIRILMIŞ (T-1 veya T Gününde %{outlier_threshold} Üstü Oynayanlar Çıkarıldı)", temizlenmis_hisseler)

    print(f"İşlem tamamlandı! Verim aralıkları dinamik olarak eklenip '{output_path}' dosyası başarıyla güncellendi.")


# --- FONKSİYONU ÇALIŞTIRMA ---
if __name__ == "__main__":
    generate_dividend_report(INPUT_FILE, OUTPUT_FILE, OUTLIER_THRESHOLD)