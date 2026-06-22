import datetime
import os
import yfinance as yf

# --- PARAMETRELER ---
INPUT_FILE = "data.txt"
OUTPUT_FILE = "processed_data.txt"

# Gün Sayısı Parametreleri (İstediğin gibi değiştirebilirsin)
DAYS_BEFORE = 7  # T'den önceki kaç gün incelenecek (örn: T-3, T-2, T-1)
DAYS_AFTER = 7   # T'den sonraki kaç gün incelenecek (örn: T+1, T+2, T+3)


def calculate_isolated_daily_returns(input_path, output_path, days_before=3, days_after=3):
    """
    BIST verilerini çeker, kümülatif yerine SADECE O GÜNÜN izole günlük getirisini
    hesaplar ve dosyaya yazar. Gün sayıları parametrik olarak ayarlanabilir.
    """
    if not os.path.exists(input_path):
        print(f"Hata: '{input_path}' dosyası bulunamadı! Lütfen girdi verilerini bu dosyaya kaydedin.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        satirlar = [line.strip().split() for line in f if line.strip()]

    sonuclar = []
    
    # Ortalama hesapları için dinamik bir sözlük yapısı (örn: -3, -2, -1, 0, 1, 2, 3)
    target_offsets = list(range(-days_before, days_after + 1))
    return_pools = {offset: [] for offset in target_offsets}

    print(f"BIST verileri çekiliyor ve T-{days_before} ile T+{days_after} arası İZOLE günlük getiriler hesaplanıyor...\n")

    for parca in satirlar:
        if len(parca) < 3:
            continue

        ticker_raw, tarih_str, verim_str = parca[0], parca[1], parca[2]
        ticker = f"{ticker_raw}.IS"

        temettu_tarihi = datetime.datetime.strptime(tarih_str, "%Y-%m-%d").date()

        # Güvenli veri aralığı (Günlük bazda bir önceki güne ihtiyaç duyduğumuz için sol tarafa +5 gün ek tolerans koyduk)
        baslangic = (temettu_tarihi - datetime.timedelta(days=days_before + 7)).strftime("%Y-%m-%d")
        bitis = (temettu_tarihi + datetime.timedelta(days=days_after + 7)).strftime("%Y-%m-%d")

        try:
            df = yf.Ticker(ticker).history(start=baslangic, end=bitis, auto_adjust=False)

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

            # İndeks sınır kontrolleri: 
            # En eski gün (t_idx - days_before) ve onun değişimini hesaplamak için bir öncesi (t_idx - days_before - 1) mevcut olmalı.
            if t_idx - days_before - 1 < 0 or t_idx + days_after >= len(all_dates):
                continue

            # --- İZOLE GÜNLÜK GETİRİ HESAPLAMA ---
            hisse_returns = {}
            
            for offset in target_offsets:
                current_day_idx = t_idx + offset
                
                # Her günün fiyatı, kendisinden bir önceki işlem gününün kapanışına bölünür
                p_current = df.iloc[current_day_idx]["Close"]
                p_previous = df.iloc[current_day_idx - 1]["Close"]
                
                isolated_return = ((p_current - p_previous) / p_previous) * 100
                
                hisse_returns[offset] = isolated_return
                return_pools[offset].append(isolated_return)

            sonuclar.append({
                "ticker": ticker_raw,
                "tarih": tarih_str,
                "verim": verim_str,
                "returns": hisse_returns
            })

        except Exception:
            continue

    # --- DOSYAYA YAZMA AŞAMASI ---
    with open(output_path, "w", encoding="utf-8") as f:
        # Dinamik Başlık Yapısı OLUŞTURMA
        before_headers = [f"T-{i}" for i in range(days_before, 0, -1)]
        after_headers = [f"T+{i}" for i in range(1, days_after + 1)]
        all_headers = before_headers + ["T_Günü"] + after_headers
        
        header_str = f"{'Hisse':<8} {'Temettü Tar':<12} {'Verim':<7} " + " ".join([f"{h:<9}" for h in all_headers]) + "\n"
        f.write(header_str)
        f.write("-" * len(header_str.strip()) + "\n")

        # Hisseleri Yazdır
        for s in sonuclar:
            line_str = f"{s['ticker']:<8} {s['tarih']:<12} %{s['verim']:<5} "
            return_strs = []
            for offset in target_offsets:
                ret_val = s["returns"][offset]
                return_strs.append(f"{ret_val:+.2f}%")
            
            line_str += " ".join([f"{r:<9}" for r in return_strs]) + "\n"
            f.write(line_str)

        # Ortalama (AVERAGE) Satırını Yazdır
        if sonuclar:
            f.write("-" * len(header_str.strip()) + "\n")
            avg_strs = []
            for offset in target_offsets:
                avg_val = sum(return_pools[offset]) / len(return_pools[offset])
                avg_strs.append(f"{avg_val:+.2f}%")
                
            avg_line = f"{'AVERAGE':<8} {'':<12} {'':<7} " + " ".join([f"{a:<9}" for a in avg_strs]) + "\n"
            f.write(avg_line)

    print(f"Analiz tamamlandı! İzole günlük verilerle '{output_path}' dosyasına basıldı.")


# --- FONKSİYONU ÇALIŞTIRMA ---
if __name__ == "__main__":
    calculate_isolated_daily_returns(INPUT_FILE, OUTPUT_FILE, days_before=DAYS_BEFORE, days_after=DAYS_AFTER)