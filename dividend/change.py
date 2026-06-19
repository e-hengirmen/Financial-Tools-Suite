import datetime
import os
import yfinance as yf

INPUT_FILE = "data.txt"
OUTPUT_FILE = "processed_data.txt"

if not os.path.exists(INPUT_FILE):
    print(
        f"Hata: '{INPUT_FILE}' dosyası bulunamadı! Lütfen girdi verilerini bu dosyaya kaydedin."
    )
    exit()

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    satirlar = [line.strip().split() for line in f if line.strip()]

sonuclar = []

# Ortalama hesaplamak için sayısal değişimleri biriktireceğimiz listeler
c1_list, c2_list, c3_list, c4_list, c5_list = [], [], [], [], []

print("BIST verileri çekiliyor ve iş günleri analiz ediliyor...\n")

for parca in satirlar:
    if len(parca) < 3:
        continue

    ticker_raw, tarih_str, verim_str = parca[0], parca[1], parca[2]
    ticker = f"{ticker_raw}.IS"

    temettu_tarihi = datetime.datetime.strptime(tarih_str, "%Y-%m-%d").date()

    baslangic = (temettu_tarihi - datetime.timedelta(days=10)).strftime(
        "%Y-%m-%d"
    )
    bitis = (temettu_tarihi + datetime.timedelta(days=15)).strftime("%Y-%m-%d")

    try:
        df = yf.Ticker(ticker).history(
            start=baslangic, end=bitis, auto_adjust=False
        )

        if df.empty:
            continue

        df.index = df.index.date
        df = df.sort_index()

        all_dates = list(df.index)

        valid_dates = [d for d in all_dates if d >= temettu_tarihi]
        if not valid_dates:
            continue
        t_gunu = valid_dates[0]
        t_idx = all_dates.index(t_gunu)

        if t_idx - 1 < 0 or t_idx + 3 >= len(all_dates):
            continue

        p_t_eksi_1 = df.iloc[t_idx - 1]["Close"]
        p_t = df.iloc[t_idx]["Close"]
        p_t_arti_1 = df.iloc[t_idx + 1]["Close"]
        p_t_arti_2 = df.iloc[t_idx + 2]["Close"]
        p_t_arti_3 = df.iloc[t_idx + 3]["Close"]

        p_t_eksi_2 = (
            df.iloc[t_idx - 2]["Close"] if t_idx - 2 >= 0 else p_t_eksi_1
        )

        # Yüzdesel değişimler (Sayısal olarak)
        c1 = ((p_t_eksi_1 - p_t_eksi_2) / p_t_eksi_2) * 100
        c2 = ((p_t - p_t_eksi_1) / p_t_eksi_1) * 100
        c3 = ((p_t_arti_1 - p_t_eksi_1) / p_t_eksi_1) * 100
        c4 = ((p_t_arti_2 - p_t_eksi_1) / p_t_eksi_1) * 100
        c5 = ((p_t_arti_3 - p_t_eksi_1) / p_t_eksi_1) * 100

        # Ortalamalar için listelere ekle
        c1_list.append(c1)
        c2_list.append(c2)
        c3_list.append(c3)
        c4_list.append(c4)
        c5_list.append(c5)

        sonuclar.append(
            {
                "ticker": ticker_raw,
                "tarih": tarih_str,
                "verim": verim_str,
                "c1": f"{c1:+.2f}%",
                "c2": f"{c2:+.2f}%",
                "c3": f"{c3:+.2f}%",
                "c4": f"{c4:+.2f}%",
                "c5": f"{c5:+.2f}%",
            }
        )

    except Exception:
        continue

# --- PROCESSED_DATA.TXT DOSYASINA YAZMA ---

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    # Başlık Satırı
    header = f"{'Hisse':<8} {'Temettü Tar':<12} {'Verim':<7} {'1G_Önce':<9} {'T_Günü':<9} {'T+1_Günü':<9} {'T+2_Günü':<9} {'T+3_Günü':<9}\n"
    f.write(header)
    f.write("-" * len(header.strip()) + "\n")

    # Veri Satırları
    for s in sonuclar:
        f.write(
            f"{s['ticker']:<8} {s['tarih']:<12} %{s['verim']:<5} {s['c1']:<9} {s['c2']:<9} {s['c3']:<9} {s['c4']:<9} {s['c5']:<9}\n"
        )

    # Alt sınır çizgisi ve Ortalamalar (Averages)
    if sonuclar:
        f.write("-" * len(header.strip()) + "\n")
        avg_c1 = sum(c1_list) / len(c1_list)
        avg_c2 = sum(c2_list) / len(c2_list)
        avg_c3 = sum(c3_list) / len(c3_list)
        avg_c4 = sum(c4_list) / len(c4_list)
        avg_c5 = sum(c5_list) / len(c5_list)

        # Verim sütunu boş bırakılarak hizalandı
        f.write(
            f"{'AVERAGE':<8} {'':<12} {'':<7} {avg_c1:+.2f}%   {avg_c2:+.2f}%   {avg_c3:+.2f}%   {avg_c4:+.2f}%   {avg_c5:+.2f}%\n"
        )

print(
    f"Analiz tamamlandı! Ortalamalar hesaplanarak '{OUTPUT_FILE}' dosyasına eklendi."
)