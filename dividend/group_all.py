import math
import os

# --- DİNAMİK GLOBAL PARAMETLER ---
INPUT_FOLDERS = ["2023", "2024", "2025"]
FILENAME = "processed_data.txt"
OUTPUT_FILE = "grouped_data_all.txt"

DAYS_BEFORE = 7
DAYS_AFTER = 7


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


# ==========================================
# 1. INITIALIZER (VERİ YÜKLEME)
# ==========================================
def load_all_stocks(folders, filename, days_before=7, days_after=7):
    """Processed dosyalarını okur ve filtresiz düz bir liste döner."""
    all_stocks = []
    for folder in folders:
        input_path = os.path.join(folder, filename)
        if not os.path.exists(input_path):
            continue

        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            if not line.strip() or line.startswith("Hisse") or line.startswith("-"):
                continue

            parts = line.strip().split()
            if len(parts) < 5:
                continue

            try:
                ticker = parts[0]
                tarih = parts[1]
                verim = parse_percentage(parts[2])
                t_1_price = float(parts[3])

                hisse_returns = {}
                for i in range(days_before):
                    offset = -days_before + i
                    col_idx = 4 + i
                    if col_idx < len(parts):
                        hisse_returns[offset] = parse_percentage(parts[col_idx])

                t_gunu_idx = 4 + days_before
                if t_gunu_idx < len(parts):
                    hisse_returns[0] = parse_percentage(parts[t_gunu_idx])

                for i in range(1, days_after + 1):
                    offset = i
                    col_idx = 4 + days_before + i
                    if col_idx < len(parts):
                        hisse_returns[offset] = parse_percentage(parts[col_idx])

                c_t = hisse_returns.get(0, 0.0)
                net_etki = verim + c_t

                all_stocks.append({
                    "ticker": ticker, "yil": folder, "tarih": tarih, "verim": verim, 
                    "t_1_price": t_1_price, "net_etki": net_etki, "returns": hisse_returns
                })
            except Exception:
                continue
    return all_stocks


# ==========================================
# 2. CREATE FILTERED LIST & GEO MEANS (YENİ)
# ==========================================
def create_filtered_list(master_list, group_name, min_dividend=0.0, max_dividend=math.inf, min_price=0.0, max_price=math.inf):
    """
    Verilen filtrelere göre listeyi süzerek, listenin kendisini ve 
    tüm sütunların geometrik ortalama (prod) değerlerini tek bir paket olarak döndürür.
    """
    # 1. Filtreleme Uygula
    filtered_stocks = []
    for s in master_list:
        if not (min_dividend <= s["verim"] <= max_dividend):
            continue
        if not (min_price <= s["t_1_price"] <= max_price):
            continue
        filtered_stocks.append(s)

    # 2. Geometrik Ortalama Çarpımlarını Hesapla (Eğer liste boş değilse)
    geo_data = {}
    if filtered_stocks:
        prod_verim = 1.0
        prod_net = 1.0
        
        # İlk hissenin return offset anahtarlarını referans alarak dinamik sözlük kuruyoruz
        offsets = list(filtered_stocks[0]["returns"].keys())
        prod_returns = {off: 1.0 for off in offsets}

        for h in filtered_stocks:
            prod_verim *= (1 + h["verim"] / 100)
            prod_net *= (1 + h["net_etki"] / 100)
            for off in offsets:
                prod_returns[off] *= (1 + h["returns"].get(off, 0.0) / 100)

        geo_data = {
            "prod_verim": prod_verim,
            "prod_net": prod_net,
            "prod_returns": prod_returns,
            "count": len(filtered_stocks)
        }

    # Her şeyi tek bir paket halinde paketleyip dönüyoruz
    return {
        "group_name": group_name,
        "stocks": filtered_stocks,
        "geo_data": geo_data
    }


# ==========================================
# 3. WRITE FILTERED LIST TO FILE (YENİ)
# ==========================================
def write_filtered_list(file_handle, group_package, days_before=7, days_after=7):
    """
    create_filtered_list fonksiyonundan gelen hazır paketi alır 
    ve dikey ayraçlı rapor şablonuna basar.
    """
    grup_adi = group_package["group_name"]
    grup_listesi = group_package["stocks"]
    geo_data = group_package["geo_data"]

    file_handle.write(f"=== {grup_adi} (Hisse Sayısı: {len(grup_listesi)}) ===\n")

    if not grup_listesi:
        file_handle.write("Bu grupta kriterlere uyan hisse bulunamadı.\n\n")
        return

    before_headers = [f"T-{i}" for i in range(days_before, 0, -1)]
    after_headers = [f"T+{i}" for i in range(1, days_after + 1)]
    
    left_part = " ".join([f"{h:<7}" for h in before_headers])
    mid_part = f"{'T_Günü':<8} {'Net_Etki':<9}"
    right_part = " ".join([f"{h:<7}" for h in after_headers])
    
    header = f"{'Hisse':<9} {'Yıl':<5} {'Temettü Tar':<12} {'Verim':<7} {'T-1_Fiyat':<10} | {left_part} | {mid_part} | {right_part}\n"
    file_handle.write(header)
    file_handle.write("-" * len(header.strip()) + "\n")

    offsets_before = list(range(-days_before, 0))
    offsets_after = list(range(1, days_after + 1))

    # Hisseleri Listele
    for h in grup_listesi:
        left_str = " ".join([f"{h['returns'].get(off, 0.0):+7.2f}%" for off in offsets_before])
        right_str = " ".join([f"{h['returns'].get(off, 0.0):+7.2f}%" for off in offsets_after])
        mid_str = f"{h['returns'].get(0, 0.0):+8.2f}% {h['net_etki']:+9.2f}%"
        
        file_handle.write(
            f"{h['ticker']:<9} {h['yil']:<5} {h['tarih']:<12} %{h['verim']:<5.2f} {h['t_1_price']:<10.2f} | "
            f"{left_str} | {mid_str} | {right_str}\n"
        )
        
    file_handle.write("-" * len(header.strip()) + "\n")

    # --- PAKETTEN GEOMETRIC SATIRINI BASMA ---
    n = geo_data["count"]
    prod_verim = geo_data["prod_verim"]
    prod_returns = geo_data["prod_returns"]
    prod_net = geo_data["prod_net"]

    geo_verim_str = f"{(math.pow(prod_verim, 1.0 / n) - 1) * 100:.2f}%" if prod_verim > 0 else f"{'------%':>5}"
    geo_left = " ".join([format_geo(prod_returns[off], n, 7) for off in offsets_before])
    geo_right = " ".join([format_geo(prod_returns[off], n, 7) for off in offsets_after])
    geo_mid = f"{format_geo(prod_returns[0], n, 8)} {format_geo(prod_net, n, 9)}"

    file_handle.write(
        f"{'GEOMETRIC':<9} {'':<5} {'':<12} %{geo_verim_str:<5} {'':<10} | "
        f"{geo_left} | {geo_mid} | {geo_right}\n"
    )
    file_handle.write("\n" + "=" * len(header.strip()) + "\n\n")


# ==========================================
# MAIN COORDINATOR (BORU HATTI)
# ==========================================
def generate_multi_year_dividend_report(folders, filename, output_path, days_before=7, days_after=7, group_limits=[2.0, 5.0, 7.0, math.inf]):
    """
    Ana çalıştırıcı boru hattı. Artık listeleri oluşturmak ve 
    dosyaya yazmak sadece tek satırlık fonksiyon çağrılarına bakıyor.
    """
    # 1. INITIALIZE: Tüm veriyi filtresiz tek seferde çek
    master_list = load_all_stocks(folders, filename, days_before, days_after)
    if not master_list:
        print("Hata: Hiçbir veri yüklenemedi.")
        return

    limits = sorted(group_limits)
    min_global_div = limits[0]
    max_global_div = limits[-1]

    # Dosya açıp grupları fırlatıyoruz
    with open(output_path, "w", encoding="utf-8") as f:
        line_len = 62 + (days_before + days_after + 1) * 8
        divider = "=" * line_len + "\n"
        
        f.write(divider)
        f.write(f"                  TEMETTÜ VERİM BAZLI ÇOKLU YIL GRUPLAMA RAPORU (PIPELINE)\n")
        f.write(divider + "\n")

        # --- GRUP 1: GENEL ÖZET ---
        genel_paket = create_filtered_list(master_list, "GENEL ÖZET: KRİTERE UYAN TÜM HİSSELER", min_dividend=min_global_div, max_dividend=max_global_div)
        write_filtered_list(f, genel_paket, days_before, days_after)

        # --- GRUP 2: MAKRO ARALIKLAR ---
        f.write(divider)
        f.write("                           FONKSİYONEL MAKRO TEMETTÜ VERİM ARALIKLARI\n")
        f.write(divider + "\n")
        
        for i in range(len(limits) - 1):
            alt, ust = limits[i], limits[i+1]
            grup_adi = f"MAKRO ARALIK: %{alt:.2f} - %{ust:.2f} ARASI"
            
            # Tek satırda filtrele paketle, tek satırda yazdır!
            makro_paket = create_filtered_list(master_list, grup_adi, min_dividend=alt, max_dividend=ust)
            write_filtered_list(f, makro_paket, days_before, days_after)

        # --- GRUP 3: DİNAMİK ADIMSAL ARALIKLAR ---
        f.write(divider)
        f.write("                           DİNAMİK ADIMSAL TEMETTÜ VERİM ARALIKLARI RAPORU\n")
        f.write(divider + "\n")
        
        realized_max_verim = max([h["verim"] for h in genel_paket["stocks"]]) if genel_paket["stocks"] else min_global_div
        baslangic = math.floor(min_global_div)
        bitis = math.ceil(realized_max_verim) if realized_max_verim > min_global_div else baslangic + 1
        
        for i in range(baslangic, bitis):
            grup_adi = f"TEMETTÜ VERİM ARALIĞI: %{i} - %{i+1} ARASI"
            adim_paket = create_filtered_list(genel_paket["stocks"], grup_adi, min_dividend=i, max_dividend=i+1)
            
            if adim_paket["stocks"]:  # Boş adımsal gruplarla kalabalık yapmayalım
                write_filtered_list(f, adim_paket, days_before, days_after)
        
        f.write(divider)
        f.write("                           CRAFTED FILTER FOR CASE\n")
        f.write(divider + "\n")

        ucuz_hisseler_paketi = create_filtered_list(master_list, "DENEME", max_price=10, min_dividend=7.0)
        write_filtered_list(f, ucuz_hisseler_paketi, days_before, days_after)
        ucuz_hisseler_paketi = create_filtered_list(master_list, "DENEME20", max_price=20, min_dividend=7.0)
        write_filtered_list(f, ucuz_hisseler_paketi, days_before, days_after)
        ucuz_hisseler_paketi = create_filtered_list(master_list, "DENEME40", max_price=40, min_dividend=7.0)
        write_filtered_list(f, ucuz_hisseler_paketi, days_before, days_after)

        ucuz_hisseler_paketi = create_filtered_list(master_list, "2-2.5", min_dividend=2, max_dividend=2.5)
        write_filtered_list(f, ucuz_hisseler_paketi, days_before, days_after)

        ucuz_hisseler_paketi = create_filtered_list(master_list, "2.5-3", min_dividend=2.5, max_dividend=3)
        write_filtered_list(f, ucuz_hisseler_paketi, days_before, days_after)

    print(f"Rapor başarıyla '{output_path}' olarak üretildi. İki yeni fonksiyon mimariye kusursuz bağlandı.")


if __name__ == "__main__":
    MY_LIMITS = [2.0, 5.0, 7.0, math.inf]

    generate_multi_year_dividend_report(
        INPUT_FOLDERS, 
        FILENAME, 
        OUTPUT_FILE, 
        days_before=DAYS_BEFORE, 
        days_after=DAYS_AFTER,
        group_limits=MY_LIMITS
    )