import os

INPUT_FILE = "processed_data.txt"
OUTPUT_FILE = "grouped_data.txt"

# --- DİNAMİK PARAMETRELER ---
# T-1 veya T gününde bu orandan fazla (veya eşit) oynayan hisseler "Aykırı Değer" kabul edilir.
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
    if not parts or parts[0] in ["Hisse", "AVERAGE"] or "-" in parts[0]:
        continue

    try:
        ticker = parts[0]
        tarih = parts[1]
        verim = parse_percentage(parts[2])

        # Sadece %2 ve üstü temettü verenler önemli
        if verim < 2.0:
            continue

        c1 = parse_percentage(parts[3])  # 1G_Önce
        c2 = parse_percentage(parts[4])  # T Günü Değişimi
        c3 = parse_percentage(parts[5])
        c4 = parse_percentage(parts[6])
        c5 = parse_percentage(parts[7])

        # --- NET ETKİ HESAPLAMA ---
        net_etki = verim + c2

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
            "c1": c1,
            "c2": c2,
            "c3": c3,
            "c4": c4,
            "c5": c5,
        }

        # Ham genel havuza ekle
        tum_hisseler.append(hisse_data)

        # --- DİNAMİK AYKIRI DEĞER (OUTLIER) FİLTRESİ ---
        # T-1 (c1) veya T günü (c2) değişimi OUTLIER_THRESHOLD değerinden küçükse listeye ekle
        if abs(c1) < OUTLIER_THRESHOLD and abs(c2) < OUTLIER_THRESHOLD:
            temizlenmis_hisseler.append(hisse_data)

        # Mikro gruplara dağıt
        if alt_sinir <= c2 <= ust_sinir:
            grup_notr.append(hisse_data)
        elif c2 > ust_sinir:
            grup_pozitif.append(hisse_data)
        else:
            grup_negatif.append(hisse_data)

    except Exception:
        continue


def write_grup_to_file(file_handle, grup_adi, grup_listesi):
    """Belirtilen listeyi dosyaya Net Etki sütunuyla birlikte yazar."""
    file_handle.write(
        f"=== {grup_adi} (Hisse Sayısı: {len(grup_listesi)}) ===\n"
    )

    if not grup_listesi:
        file_handle.write("Bu grupta kriterlere uyan hisse bulunamadı.\n\n")
        return

    # Tablo Düzeni
    header = f"{'Hisse':<8} {'Temettü Tar':<12} {'Verim':<7} {'T_Günü':<9} {'Net_Etki':<10} {'1G_Önce':<9} {'T+1_Günü':<9} {'T+2_Günü':<9} {'T+3_Günü':<9}\n"
    file_handle.write(header)
    file_handle.write("-" * len(header.strip()) + "\n")

    sum_verim, sum_net, sum_c1, sum_c2, sum_c3, sum_c4, sum_c5 = (
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    )

    for h in grup_listesi:
        file_handle.write(
            f"{h['ticker']:<8} {h['tarih']:<12} %{h['verim']:<5.2f} {h['c2']:+8.2f}% {h['net_etki']:+9.2f}% {h['c1']:+8.2f}% {h['c3']:+8.2f}% {h['c4']:+8.2f}% {h['c5']:+8.2f}%\n"
        )
        sum_verim += h["verim"]
        sum_net += h["net_etki"]
        sum_c1 += h["c1"]
        sum_c2 += h["c2"]
        sum_c3 += h["c3"]
        sum_c4 += h["c4"]
        sum_c5 += h["c5"]

    n = len(grup_listesi)
    file_handle.write("-" * len(header.strip()) + "\n")
    file_handle.write(
        f"{'AVERAGE':<8} {'':<12} %{sum_verim/n:<5.2f} {sum_c2/n:+8.2f}% {sum_net/n:+9.2f}% {sum_c1/n:+8.2f}% {sum_c3/n:+8.2f}% {sum_c4/n:+8.2f}% {sum_c5/n:+8.2f}%\n"
    )
    file_handle.write("\n" + "=" * len(header.strip()) + "\n\n")


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(
        "=========================================================================================\n"
    )
    f.write(
        "                 TEMETTÜ SONRASI İŞ GÜNÜ GRUPLAMA RAPORU (Verim >= %2)                  \n"
    )
    f.write(
        "=========================================================================================\n\n"
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
    f"İşlem tamamlandı! Filtre eşiği %{OUTLIER_THRESHOLD} olarak uygulandı ve '{OUTPUT_FILE}' dosyasına yazıldı."
)