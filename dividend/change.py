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

c_minus3_list = []
c_minus2_list = []
c_minus1_list = []
c_t_list = []
c_plus1_list = []
c_plus2_list = []
c_plus3_list = []

print(
    "BIST verileri çekiliyor ve T-4 tabanlı Sol Grup kümülatif mantığına göre analiz ediliyor...\n"
)

for parca in satirlar:
    if len(parca) < 3:
        continue

    ticker_raw, tarih_str, verim_str = parca[0], parca[1], parca[2]
    ticker = f"{ticker_raw}.IS"

    temettu_tarihi = datetime.datetime.strptime(tarih_str, "%Y-%m-%d").date()

    # T-4'ten güvenli veri alabilmek için aralığı sola doğru biraz daha açtık
    baslangic = (temettu_tarihi - datetime.timedelta(days=15)).strftime(
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

        # T-4 ve T+3 indekslerinin sınır kontrolü (T-4 mevcut olmalı)
        if t_idx - 4 < 0 or t_idx + 3 >= len(all_dates):
            continue

        # Fiyat Noktaları
        p_t_eksi_4 = df.iloc[t_idx - 4]["Close"]  # Sol grubun ana taban fiyatı
        p_t_eksi_3 = df.iloc[t_idx - 3]["Close"]
        p_t_eksi_2 = df.iloc[t_idx - 2]["Close"]
        p_t_eksi_1 = df.iloc[t_idx - 1]["Close"]
        p_t = df.iloc[t_idx]["Close"]
        p_t_arti_1 = df.iloc[t_idx + 1]["Close"]
        p_t_arti_2 = df.iloc[t_idx + 2]["Close"]
        p_t_arti_3 = df.iloc[t_idx + 3]["Close"]

        # --- YENİ 3 PARÇALI KÜMÜLATİF MANTIK (T-4 TABANLI) ---

        # 1. SOL GRUP (Taban: T-4 kapanış fiyatı | 24 saatlik döngüler kümülatif birikir)
        c_minus3 = ((p_t_eksi_3 - p_t_eksi_4) / p_t_eksi_4) * 100
        c_minus2 = ((p_t_eksi_2 - p_t_eksi_4) / p_t_eksi_4) * 100
        c_minus1 = ((p_t_eksi_1 - p_t_eksi_4) / p_t_eksi_4) * 100

        # 2. ORTA GRUP (Sadece T günü kendisi | Taban: T-1 kapanış fiyatı)
        c_t = ((p_t - p_t_eksi_1) / p_t_eksi_1) * 100

        # 3. SAĞ GRUP (T günü dahil kümülatif | Taban: T-1 kapanış fiyatı)
        c_plus1 = ((p_t_arti_1 - p_t_eksi_1) / p_t_eksi_1) * 100
        c_plus2 = ((p_t_arti_2 - p_t_eksi_1) / p_t_eksi_1) * 100
        c_plus3 = ((p_t_arti_3 - p_t_eksi_1) / p_t_eksi_1) * 100

        # Ortalamalar için listelere ekle
        c_minus3_list.append(c_minus3)
        c_minus2_list.append(c_minus2)
        c_minus1_list.append(c_minus1)
        c_t_list.append(c_t)
        c_plus1_list.append(c_plus1)
        c_plus2_list.append(c_plus2)
        c_plus3_list.append(c_plus3)

        sonuclar.append(
            {
                "ticker": ticker_raw,
                "tarih": tarih_str,
                "verim": verim_str,
                "c_m3": f"{c_minus3:+.2f}%",
                "c_m2": f"{c_minus2:+.2f}%",
                "c_m1": f"{c_minus1:+.2f}%",
                "c_t": f"{c_t:+.2f}%",
                "c_p1": f"{c_plus1:+.2f}%",
                "c_p2": f"{c_plus2:+.2f}%",
                "c_p3": f"{c_plus3:+.2f}%",
            }
        )

    except Exception:
        continue

# --- PROCESSED_DATA.TXT DOSYASINA YAZMA ---

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    header = f"{'Hisse':<8} {'Temettü Tar':<12} {'Verim':<7} {'T-3':<9} {'T-2':<9} {'T-1':<9} {'T_Günü':<9} {'T+1':<9} {'T+2':<9} {'T+3':<9}\n"
    f.write(header)
    f.write("-" * len(header.strip()) + "\n")

    for s in sonuclar:
        f.write(
            f"{s['ticker']:<8} {s['tarih']:<12} %{s['verim']:<5} {s['c_m3']:<9} {s['c_m2']:<9} {s['c_m1']:<9} {s['c_t']:<9} {s['c_p1']:<9} {s['c_p2']:<9} {s['c_p3']:<9}\n"
        )

    if sonuclar:
        f.write("-" * len(header.strip()) + "\n")
        avg_m3 = sum(c_minus3_list) / len(c_minus3_list)
        avg_m2 = sum(c_minus2_list) / len(c_minus2_list)
        avg_m1 = sum(c_minus1_list) / len(c_minus1_list)
        avg_t = sum(c_t_list) / len(c_t_list)
        avg_p1 = sum(c_plus1_list) / len(c_plus1_list)
        avg_p2 = sum(c_plus2_list) / len(c_plus2_list)
        avg_p3 = sum(c_plus3_list) / len(c_plus3_list)

        f.write(
            f"{'AVERAGE':<8} {'':<12} {'':<7} {avg_m3:+.2f}%   {avg_m2:+.2f}%   {avg_m1:+.2f}%   {avg_t:+.2f}%   {avg_p1:+.2f}%   {avg_p2:+.2f}%   {avg_p3:+.2f}%\n"
        )

print(
    f"Analiz tamamlandı! Sol grup T-4 tabanlı gerçek kümülatif değerlerle '{OUTPUT_FILE}' dosyasına basıldı."
)