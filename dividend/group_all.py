import math
import os

# --- DİNAMİK GLOBAL PARAMETLER ---
INPUT_FOLDERS = ["2023", "2024", "2025"]
FILENAME = "processed_data.txt"
OUTPUT_FILE = "grouped_data_all.txt"

# Gün parametreleri
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


def write_grup_to_file(file_handle, grup_adi, grup_listesi, days_before, days_after):
    """Belirtilen listeyi dinamik gün parametrelerine göre dikey ayraçlı bloklar halinde dosyaya yazar."""
    file_handle.write(f"=== {grup_adi} (Hisse Sayısı: {len(grup_listesi)}) ===\n")

    if not grup_listesi:
        file_handle.write("Bu grupta kriterlere uyan hisse bulunamadı.\n\n")
        return

    before_headers = [f"T-{i}" for i in range(days_before, 0, -1)]
    after_headers = [f"T+{i}" for i in range(1, days_after + 1)]
    
    left_part = " ".join([f"{h:<7}" for h in before_headers])
    mid_part = f"{'T_Günü':<8} {'Net_Etki':<9}"
    right_part = " ".join([f"{h:<7}" for h in after_headers])
    
    header = f"{'Hisse':<9} {'Yıl':<5} {'Temettü Tar':<12} {'Verim':<7} | {left_part} | {mid_part} | {right_part}\n"
    file_handle.write(header)
    file_handle.write("-" * len(header.strip()) + "\n")

    offsets_before = list(range(-days_before, 0))
    offsets_after = list(range(1, days_after + 1))
    all_offsets = offsets_before + [0] + offsets_after

    prod_returns = {offset: 1.0 for offset in all_offsets}
    prod_verim = 1.0
    prod_net = 1.0

    for h in grup_listesi:
        left_str = " ".join([f"{h['returns'].get(off, 0.0):+7.2f}%" for off in offsets_before])
        right_str = " ".join([f"{h['returns'].get(off, 0.0):+7.2f}%" for off in offsets_after])
        mid_str = f"{h['returns'].get(0, 0.0):+8.2f}% {h['net_etki']:+9.2f}%"
        
        file_handle.write(
            f"{h['ticker']:<9} {h['yil']:<5} {h['tarih']:<12} %{h['verim']:<5.2f} | "
            f"{left_str} | {mid_str} | {right_str}\n"
        )
        
        prod_verim *= (1 + h["verim"] / 100)
        prod_net *= (1 + h["net_etki"] / 100)
        
        for off in all_offsets:
            val = h["returns"].get(off, 0.0)
            prod_returns[off] *= (1 + val / 100)

    n = len(grup_listesi)
    file_handle.write("-" * len(header.strip()) + "\n")

    # --- GEOMETRIC SATIRI ---
    geo_verim_str = f"{(math.pow(prod_verim, 1.0 / n) - 1) * 100:.2f}%" if prod_verim > 0 else f"{'------%':>5}"
    geo_left = " ".join([format_geo(prod_returns[off], n, 7) for off in offsets_before])
    geo_right = " ".join([format_geo(prod_returns[off], n, 7) for off in offsets_after])
    geo_mid = f"{format_geo(prod_returns[0], n, 8)} {format_geo(prod_net, n, 9)}"

    file_handle.write(
        f"{'GEOMETRIC':<9} {'':<5} {'':<12} %{geo_verim_str:<5} | "
        f"{geo_left} | {geo_mid} | {geo_right}\n"
    )

    file_handle.write("\n" + "=" * len(header.strip()) + "\n\n")


def generate_multi_year_dividend_report(
    folders, filename, output_path, 
    days_before=7, days_after=7, 
    group_limits=[2.0, 5.0, 7.0, 15.0]
):
    """
    Belirlenen aralık limitlerine göre gruplama yapar ve 
    tablo sonlarında sadece Geometrik Ortalama hesaplar.
    """
    limits = sorted(group_limits)
    min_dividend = limits[0]
    max_dividend = limits[-1]

    # Makro grup sözlüğü dinamik kurulumu
    makro_gruplar = {(limits[i], limits[i+1]): [] for i in range(len(limits)-1)}
    
    tum_hisseler = []
    realized_max_verim = min_dividend

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
            if len(parts) < 4:
                continue

            try:
                ticker = parts[0]
                tarih = parts[1]
                verim = parse_percentage(parts[2])

                if verim < min_dividend or verim > max_dividend:
                    continue
                
                if verim > realized_max_verim:
                    realized_max_verim = verim

                # --- SABİT 4. SÜTUN BAZLI MAPLEME ---
                hisse_returns = {}
                for i in range(days_before):
                    offset = -days_before + i
                    col_idx = 3 + i
                    if col_idx < len(parts):
                        hisse_returns[offset] = parse_percentage(parts[col_idx])

                t_gunu_idx = 3 + days_before
                if t_gunu_idx < len(parts):
                    hisse_returns[0] = parse_percentage(parts[t_gunu_idx])

                for i in range(1, days_after + 1):
                    offset = i
                    col_idx = 3 + days_before + i
                    if col_idx < len(parts):
                        hisse_returns[offset] = parse_percentage(parts[col_idx])

                c_t = hisse_returns.get(0, 0.0)
                net_etki = verim + c_t

                hisse_data = {
                    "ticker": ticker, "yil": folder, "tarih": tarih, "verim": verim, 
                    "net_etki": net_etki, "returns": hisse_returns
                }

                tum_hisseler.append(hisse_data)

                # --- FONKSİYONEL ARALIK DAĞILIMI ---
                for (alt, ust) in makro_gruplar.keys():
                    if alt <= verim < ust or (ust == max_dividend and verim == ust):
                        makro_gruplar[(alt, ust)].append(hisse_data)
                        break

            except Exception:
                continue

    # Dinamik Adımsal 1'erlik Aralık Yapısı
    verim_araliklari = {}
    baslangic = math.floor(min_dividend)
    bitis = math.ceil(realized_max_verim)
    
    for i in range(baslangic, bitis):
        verim_araliklari[(i, i+1)] = []
        
    for h in tum_hisseler:
        v = h["verim"]
        for (alt, ust) in verim_araliklari.keys():
            if alt <= v < ust or (ust == bitis and v >= ust):
                verim_araliklari[(alt, ust)].append(h)
                break

    # Rapor Yazımı
    with open(output_path, "w", encoding="utf-8") as f:
        line_len = 50 + (days_before + days_after + 1) * 8
        divider = "=" * line_len + "\n"
        
        f.write(divider)
        f.write(f"                  TEMETTÜ VERİM BAZLI ÇOKLU YIL GRUPLAMA RAPORU\n")
        f.write(f"                       Aktif Sınırlar -> En Düşük: %{min_dividend:.2f} | En Yüksek: %{max_dividend:.2f}\n")
        f.write(divider + "\n")

        # Genel Özet
        write_grup_to_file(f, "GENEL ÖZET: LİMİTLERE UYAN TÜM HİSSELER", tum_hisseler, days_before, days_after)

        # Makro Aralıklar
        f.write(divider)
        f.write("                           FONKSİYONEL MAKRO TEMETTÜ VERİM ARALIKLARI\n")
        f.write(divider + "\n")
        for (alt, ust), g_list in sorted(makro_gruplar.items()):
            write_grup_to_file(f, f"MAKRO ARALIK: %{alt:.2f} - %{ust:.2f} ARASI", g_list, days_before, days_after)

        # Adımsal Aralıklar
        f.write(divider)
        f.write("                           DİNAMİK ADIMSAL TEMETTÜ VERİM ARALIKLARI RAPORU\n")
        f.write(divider + "\n")
        for (alt, ust), g_list in sorted(verim_araliklari.items()):
            if g_list:
                write_grup_to_file(f, f"TEMETTÜ VERİM ARALIĞI: %{alt} - %{ust} ARASI", g_list, days_before, days_after)

    print(f"Rapor başarıyla '{output_path}' olarak üretildi. Yalnızca geometrik ortalamalar korundu.")


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