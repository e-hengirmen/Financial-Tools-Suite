import cloudscraper
from datetime import datetime
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from copy import deepcopy
import yfinance as yf
import time

import numpy as np
import pandas as pd

class StockScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.start_date = '2010-01-01'
        self.start_date_datetime = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        self.data_center = {}

    def get_data(self, abbr):
        import time
        # Fintables artık Unix Timestamp istiyor. 
        # Başlangıç tarihini saniyeye çeviriyoruz.
        from_timestamp = int(time.mktime(self.start_date_datetime.timetuple()))
        # Bitiş tarihini 'bugün' olarak dinamik alıp saniyeye çeviriyoruz.
        to_timestamp = int(time.time())
        
        # Yeni endpoint URL yapısı
        url = f'https://markets.fintables.com/barbar/udf/history?symbol={abbr}&resolution=D&from={from_timestamp}&to={to_timestamp}'
        
        response = self.scraper.get(url)
        if response.status_code == 200:
            json_res = response.json()
            
            # API'den veri gelmediyse veya boşsa koruma
            if json_res.get('s') != 'ok':
                raise Exception(f"{abbr} için veri alınamadı veya sembol bulunamadı.")
                
            # TradingView UDF formatını eski kodunuzun okuyabileceği formata (liste içine dict) dönüştürüyoruz
            timestamps = json_res['t'] # Zaman listesi (Unix)
            close_prices = json_res['c'] # Kapanış fiyatları listesi
            
            transformed_data = []
            for t_val, c_val in zip(timestamps, close_prices):
                # Unix saniyesini tekrar datetime.date objesine çeviriyoruz
                row_date = datetime.fromtimestamp(t_val).date()
                
                # Eski kodunuzun beklediği mimariyi taklit ediyoruz: {'value': X, 'date': Y}
                transformed_data.append({
                    'value': float(c_val),
                    'date': row_date
                })
                
            return transformed_data
        else:
            raise Exception(f'Gotten {response.status_code} from fintables api')
    
    def get_data_old(self, abbr):
        # url = f'https://api.fintables.com/funds/{abbr}/chart/?start_date={self.start_date}&compare='
        url = f'https://api.fintables.com/funds/{abbr}/chart/?start_date={self.start_date}'
        response = self.scraper.get(url)
        if response.status_code == 200:
            data = response.json()['results']['data']
            for row in data:
                value = row[abbr]
                row['value'] = value
                row['date'] = self.get_date(row['date'])
                del row[abbr]
            return data
        else:
            raise Exception(f'Gotten {response.status_code} from fintables api')

    def get_date(self, date_str):
        return datetime.strptime(date_str, '%Y-%m-%d').date()

    def create_tables(self, abbr_list):
        for abbr in abbr_list:
            if abbr not in self.data_center:
                self.data_center[abbr] = self.get_data(abbr)

    def get_data_within(self, abbr, start_date, end_date, daily=False):
        if type(start_date) is str:
            start_date = self.get_date(start_date)
        if type(end_date) is str:
            end_date = self.get_date(end_date)
        res = []
        for row in self.data_center[abbr]:
            if start_date <= row['date'] <= end_date:
                res.append(deepcopy(row))
        initial_value = res[0]['value']
        if daily:
            for i in range(1, len(res)):
                prev = res[i-1]['value']
                curr = res[i]['value']
                res[i]['percentage'] = (curr - prev) / prev
            res[0]['percentage'] = 0
        else:
            for row in res:
                row['percentage'] = (row['value'] - initial_value) / initial_value

        return res
    
    def plot_graph(self, data_lists, titles=None, plot_title='Fund Data'):
        plt.figure(figsize=(12, 6))
    
        for i, data in enumerate(data_lists):
            dates = [d['date'] for d in data]
            values = [d['percentage'] for d in data]
            
            plt.plot(dates, values, marker='o', linestyle='-', label=titles[i] if titles else f'Dataset {i+1}')
        
        plt.xlabel('Date')
        plt.ylabel('Change')
        plt.title(plot_title)
        plt.legend(loc='center left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    def plot_within_dates(self, abbr_list, start_date, end_date, drop_late_starts=False):
        data_lists = []
        titles = []
        min_date = datetime.now().date()
        for abbr in abbr_list:
            try:
                data = self.get_data_within(abbr, start_date, end_date)
                if drop_late_starts and min_date > data[0]['date']:
                    min_date = data[0]['date']
                data_lists.append(data)
                titles.append(abbr)
            except:
                pass
        if drop_late_starts:
            data_lists2 = data_lists
            data_lists = []
            titles2 = titles
            titles = []
            for data_list, abbr in zip(data_lists2, titles2):
                current_date = data_list[0]['date']
                if current_date == min_date:
                    data_lists.append(data_list)
                    titles.append(abbr)
                else:
                    print(f'{abbr} dropped starting at {current_date} after min date of {min_date}')
        self.plot_graph(data_lists, titles, plot_title=f'{str(start_date)} <-> {str(end_date)}')
    
    def year_zero(self, data):
        time_diff = data[0]['date'] - datetime(2000,1,1).date()
        for row in data:
            row['date'] -= time_diff


    def plot_monthly(self, abbr, start_time=None, end_time=None):
        end_date = (datetime.now() + relativedelta(months=1)).date().replace(day=1)
        
        current_date = (self.data_center[abbr][0]['date'] + relativedelta(months=1)).replace(day=1)
        current_date = (self.data_center[abbr][0]['date']).replace(day=1)
        if start_time and end_time:
            end_date = self.get_date(end_time)
            current_date = max(self.get_date(start_time), current_date)

        data_lists = []
        titles = []
        while current_date < end_date:
            next_date = current_date + relativedelta(months=1)
            data = self.get_data_within(abbr, current_date, next_date)
            self.year_zero(data)
            data_lists.append(data)
            titles.append(str(current_date))
            current_date = next_date
        

        result = {}
        for data_list, time in zip(data_lists, titles):
            for row in data_list:
                day = row['date'].day
                percentage = row['percentage']
                old_val, count = result.get(day, (0, 0))
                result[day] = (old_val + percentage, count + 1)
        for day in range(1,32):
            if day in result:
                val, count = result[day]
                print(f"\033[{91 if val/count < 0.0015 else 92 if val/count > 0.05 else 0}mDay {day} res: {val/count}")

        self.plot_graph(data_lists, titles)

    def calculate_correlation(
        self,
        abbr1,
        abbr2,
        start_date = (datetime.today() - relativedelta(months=12)).date(),
        end_date = datetime.now().date(),
        method = 'pearson'
    ):
        """
        Calculate correlation between two funds.

        :param abbr1: First fund abbreviation
        :param abbr2: Second fund abbreviation
        :param start_date: optional start date (YYYY-MM-DD or datetime.date)
        :param end_date: optional end date (YYYY-MM-DD or datetime.date)
        :param method: correlation method ('pearson' or 'spearman')
        :return: correlation value
        """
        # Get data
        data1 = pd.DataFrame(self.get_data_within(abbr1, start_date, end_date, daily=True))
        data2 = pd.DataFrame(self.get_data_within(abbr2, start_date, end_date, daily=True))

        # Align by date
        merged = pd.merge(data1[['date', 'percentage']], data2[['date', 'percentage']], 
                          on='date', suffixes=(f'_{abbr1}', f'_{abbr2}'))

        # Calculate correlation
        corr = merged[f'percentage_{abbr1}'].corr(merged[f'percentage_{abbr2}'], method=method)

        return corr
    
    def get_all_correlations(
            self,
            abbr_list=None,
            start_date = (datetime.today() - relativedelta(months=12)).date(),
            end_date = datetime.now().date(),
            method = 'pearson'
        ):
        if abbr_list is None:
            abbr_list = list(self.data_center.keys())

        n = len(abbr_list)
        correlations = []

        # Collect all correlations
        for i in range(n):
            for j in range(i + 1, n):
                a = abbr_list[i]
                b = abbr_list[j]
                corr = self.calculate_correlation(a, b, start_date, end_date, method)
                correlations.append((a, b, corr))

        # Sort descending by correlation
        correlations.sort(key=lambda x: x[2], reverse=True)

        # Print with color coding
        print('Correlations:')
        print('########################################')
        for a, b, corr in correlations:
            if corr >= 0.98:
                color = "\033[91m"  # red
            elif corr >= 0.95:
                color = "\033[33m"  # orange
            elif corr >= 0.85:
                color = "\033[93m"  # yellow
            elif corr >= 0.70:
                color = "\033[92m"  # green
            else:
                color = "\033[0m"   # default
            print(f"{color}{a} - {b}: {corr:.4f}\033[0m")
        print('########################################')
    
    def calculate_cumulative_growth_with_search(self, fund_abbr, compare_symbol='TRY=X', start_date=None, end_date=None, method='pearson'):
        """
        Fintables ve Yahoo Finance'ten ham verileri çeker.
        Doların dünkü kapanışını (Close.shift(1)) fonun bugünkü fiyatıyla eşitleyerek valör sapmasını düzeltir.
        Ardından temizlenen bu senkronize veri üzerinden Day 0 kümülatif büyümesini hesaplar.
        Greedy ve Ternary/Binary Search kombinasyonu ile kümülatif çizgileri en iyi eşleyen çarpanı bulur.
        """
        import yfinance as yf
        import time
        import numpy as np
        import matplotlib.pyplot as plt
        import pandas as pd
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        
        # --- YAHOO FINANCE OTOMATİK FORMAT DÜZELTME ---
        if compare_symbol.upper() in ['USDTRY', 'USD', 'DOLAR']:
            compare_symbol = 'TRY=X'
        elif compare_symbol.upper() in ['EURTRY', 'EUR', 'EURO']:
            compare_symbol = 'EURTRY=X'
            
        if start_date is None:
            start_date = (datetime.today() - relativedelta(months=12)).date()
        if end_date is None:
            end_date = datetime.now().date()
            
        if type(start_date) is str:
            start_date = self.get_date(start_date)
        if type(end_date) is str:
            end_date = self.get_date(end_date)

        # --- 1. ADIM: Fintables'tan Fon Verisini Çekme ---
        from_timestamp = int(time.mktime(start_date.timetuple()))
        to_timestamp = int(time.time())
        
        url = f'https://markets.fintables.com/barbar/udf/history?symbol={fund_abbr}&resolution=D&from={from_timestamp}&to={to_timestamp}'
        response = self.scraper.get(url)
        
        if response.status_code != 200:
            raise Exception(f'Fintables API\'sinden {response.status_code} hatası alındı.')
            
        json_res = response.json()
        if json_res.get('s') != 'ok':
            print(f"{fund_abbr} için veri bulunamadı.")
            return

        fund_rows = []
        for t_val, c_val in zip(json_res['t'], json_res['c']):
            fund_rows.append({
                'date': datetime.fromtimestamp(t_val).date(),
                'fund_value': float(c_val)
            })
        df_fund = pd.DataFrame(fund_rows)

        # --- 2. ADIM: Yahoo Finance'ten Karşılaştırma Sembolünü Çekme ---
        yf_start = start_date.strftime('%Y-%m-%d')
        yf_end = (end_date + relativedelta(days=1)).strftime('%Y-%m-%d')
        
        try:
            ticker_data = yf.download(compare_symbol, start=yf_start, end=yf_end, progress=False, auto_adjust=False)
            if ticker_data.empty:
                raise Exception()
            
            df_compare = ticker_data[['Close']].copy()
            df_compare.columns = ['compare_value']
            df_compare = df_compare.reset_index()
            df_compare['date'] = df_compare['Date'].dt.date
            df_compare = df_compare[['date', 'compare_value']]
        except:
            print(f"Yahoo Finance üzerinden {compare_symbol} sembolü indirilemedi.")
            return

        # --- 3. ADIM: İki Veriyi Ortak İşlem Günlerine Göre Eşitleme ---
        merged_df = pd.merge(df_fund, df_compare, on='date', how='inner').sort_values('date').reset_index(drop=True)

        if merged_df.empty:
            print(f"{start_date} ve {end_date} arasında ortak işlem günü bulunamadı.")
            return

        # --- 4. ADIM: ZAMAN KAYMASINI HAM FİYAT SEVİYESİNDE DÜZELTME ---
        # Doların dünkü kapanışını fonun bugünkü fiyatının karşısına getiriyoruz (Valör düzeltmesi)
        merged_df['compare_value_lagged'] = merged_df['compare_value'].shift(1)
        
        # Shift işleminden dolayı oluşan ilk satırdaki NaN değerini temizliyoruz.
        # Böylece yeni tablomuzun İLK SATIRI her iki enstrümanın da GERÇEK EŞLEŞEN başlangıç noktası (Day 0) oluyor.
        clean_df = merged_df.dropna(subset=['compare_value_lagged']).copy().reset_index(drop=True)

        # --- 5. ADIM: YENİ SENKRONİZE BAŞLANGIÇ NOKTALARI (Day 0) ---
        initial_fund_price = clean_df['fund_value'].iloc[0]
        initial_compare_price = clean_df['compare_value_lagged'].iloc[0] # Senkronize başlangıç fiyatı

        # Kümülatif büyüme serileri (Artık başlangıç anları milimetrik olarak aynı)
        clean_df['fund_growth'] = (clean_df['fund_value'] / initial_fund_price) - 1
        clean_df['compare_growth_raw'] = (clean_df['compare_value'] / clean_df['compare_value'].iloc[0]) - 1 # Karşılaştırma için ham (eşlenmemiş) trend
        clean_df['compare_growth_lagged_base'] = (clean_df['compare_value_lagged'] / initial_compare_price) - 1

        # --- 6. ADIM: GREEDY & BINARY/TERNARY SEARCH İLE OPTİMAL MULTIPLIER BULMA ---
        def calculate_sse(m):
            return np.sum((clean_df['fund_growth'] - (clean_df['compare_growth_lagged_base'] * m)) ** 2)

        # Greedy kaba arama (1, 2, 4 ... 256)
        greedy_values = [1, 2, 4, 8, 16, 32, 64, 128, 256]
        best_greedy_idx = 0
        min_greedy_error = float('inf')
        
        for i, val in enumerate(greedy_values):
            err = calculate_sse(val)
            if err < min_greedy_error:
                min_greedy_error = err
                best_greedy_idx = i

        # Sınırları (Bound) Tanımlama
        if best_greedy_idx == 0:
            low_b, high_b = 0.0, 2.0
        elif best_greedy_idx == len(greedy_values) - 1:
            low_b, high_b = greedy_values[-2], greedy_values[-1] * 2
        else:
            low_b = greedy_values[best_greedy_idx - 1]
            high_b = greedy_values[best_greedy_idx + 1]

        # Hassas Arama Optimizasyonu
        for _ in range(60):
            mid1 = low_b + (high_b - low_b) / 3
            mid2 = high_b - (high_b - low_b) / 3
            if calculate_sse(mid1) < calculate_sse(mid2):
                high_b = mid2
            else:
                low_b = mid1
            
        estimated_multiplier = round((low_b + high_b) / 2, 4)

        # En ideal çarpanla ölçeklenmiş nihai seriyi oluşturuyoruz
        clean_df['compare_growth_scaled'] = clean_df['compare_growth_lagged_base'] * estimated_multiplier

        # --- 7. ADIM: GERÇEK VE NET KORELASYON FARKI ---
        # Aynı gün (hatalı/ham) kümülatif korelasyonu
        corr_raw = clean_df['fund_growth'].corr(clean_df['compare_growth_raw'], method=method)
        # 1 gün gecikmeli (senkronize edilmiş) kümülatif korelasyon
        corr_lagged = clean_df['fund_growth'].corr(clean_df['compare_growth_scaled'], method=method)

        # --- 8. ADIM: SONUÇLARI EKRANA YAZDIRMA ---
        if corr_lagged >= 0.70:
            color = "\033[92m"  # Yeşil
        elif corr_lagged <= -0.40:
            color = "\033[91m"  # Kırmızı
        else:
            color = "\033[0m"
            
        print('\n########################################')
        print(f"SENKRONİZE KÜMÜLATİF TREND ANALİZİ ({method.capitalize()}):")
        print(f"Aynı Gün Kümülatif Korelasyonu (Hatalı/Kaymış): {corr_raw:.4f}")
        print(f"{color}1 Gün Gecikmeli Kümülatif Korelasyon (DÜZELTİLMİŞ): {corr_lagged:.4f}\033[0m")
        print(f"\n* By greedy approaches we estimate the multiplier value to be {estimated_multiplier} and the correlation to be {corr_lagged:.4f} *")
        print("The data below is shown with given multiplier value.")
        print('########################################\n')

        # --- 9. ADIM: GÖRSEL GRAFİK ÇİZİMİ ---
        plt.figure(figsize=(14, 7))
        
        plt.plot(clean_df['date'], clean_df['fund_growth'] * 100, 
                 label=f'{fund_abbr} Birikimli Değişim (Day 0\'dan Beri)', linestyle='-', color='#1f77b4', linewidth=2)
        
        plt.plot(clean_df['date'], clean_df['compare_growth_scaled'] * 100, 
                 label=f'{compare_symbol} Birikimli Değişim (x{estimated_multiplier} Valör Senkronizeli)', 
                 linestyle='--', color='#ff7f0e', linewidth=2)
        
        plt.xlabel('Tarih')
        plt.ylabel('Day 0\'dan İtibaren Toplam Değişim (%)')
        plt.title(f'{fund_abbr} vs {compare_symbol} Senkronize Kümülatif Büyüme Grafiği\nOptimized Multiplier: {estimated_multiplier}x | Corrected Correlation: {corr_lagged:.4f}')
        plt.legend(loc='upper left')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.show()
        
        return corr_lagged



stockscraper = StockScraper()

general_fund_list = [
    'AES',
    'IHK',
    'TTE',
    'ADP',
    'TAU',
    'AFT',
    'DVT',
    'IJC',
    'BIO',
    'IJZ',
    'AFA',
]

money_market_fund_list = [  # para piyasası fonları
    'PPN',
    'RPP',
    'NVB',
    'IRY',
    'HYV',
    'PPZ',
    'NRG',
    'BGP',
    'IJV',
    'HVT',
    'AC4',
    'KIE',
    'IDL',
    'ZBJ',
    'IOO',
    'FIL',
    'UPP',
    'GO6',
    'PJL',
    'DLY',
    'HSL',
    'TCB',
    'EIL',
    'AAL',
    'ICE',
    'PPT',
    'DL2',
    'FPI',
    'KPP',
    'PPP',
    'PRY',
    'CFO',
]

silver_fund_list = [
    'MJG',
    'IOG',
    'YZG',
    'GTZ',
    # 'GMC',
    # 'GUM',
    'DMG',
    'FMG',
]

fund_list = general_fund_list

fund_list = [
'IHK',
'BIO',
'YZG',
'TTE',
'ADP',
'TAU',
'DVT',
'AFT',
'YAY',
]
stockscraper.create_tables(fund_list)



today_datetime = datetime.today()
today  = datetime.today().strftime('%Y-%m-%d')
month_0 = today_datetime.replace(day=1).strftime('%Y-%m-%d')
month_1 = (today_datetime - relativedelta(months=1)).replace(day=1).strftime('%Y-%m-%d')
month_2 = (today_datetime - relativedelta(months=2)).replace(day=1).strftime('%Y-%m-%d')
month_3 = (today_datetime - relativedelta(months=3)).replace(day=1).strftime('%Y-%m-%d')
month_4 = (today_datetime - relativedelta(months=4)).replace(day=1).strftime('%Y-%m-%d')
month_6 = (today_datetime - relativedelta(months=6)).replace(day=1).strftime('%Y-%m-%d')
month_12 = (today_datetime - relativedelta(months=12)).replace(day=1).strftime('%Y-%m-%d')
"""
stockscraper.plot_within_dates(fund_list, month_12, today, drop_late_starts=True)
stockscraper.plot_within_dates(fund_list, month_6, today, drop_late_starts=True)
stockscraper.plot_within_dates(fund_list, month_4, today, drop_late_starts=True)
stockscraper.plot_within_dates(fund_list, month_2, today, drop_late_starts=True)
stockscraper.plot_within_dates(fund_list, month_1, today, drop_late_starts=True)
stockscraper.plot_within_dates(fund_list, month_0, today, drop_late_starts=True)
# x = stockscraper.get_data_within('DVT', '2024-01-01', '2024-06-01')

stockscraper.get_all_correlations()
"""



# stockscraper.plot_monthly('YZG', '2022-01-01', '2023-01-1')
# stockscraper.plot_monthly('YZG', '2023-01-01', '2024-01-1')
# stockscraper.plot_monthly('YZG', '2024-01-01', '2024-8-18')

# stockscraper.plot_monthly('YZG', '2023-01-01', '2024-8-18')


# Listeye BSM fonunu eklediğinizden emin olun veya doğrudan tekil çağırın:

"""
stockscraper.create_tables(['BSM'])

# Doğrudan yeni ismiyle çağırma
stockscraper.calculate_cumulative_growth_with_search('BSM', 'USDTRY', start_date=month_12, end_date=month_6)
# stockscraper.calculate_cumulative_growth_with_search('BSM', 'USDTRY', start_date=month_6, end_date=month_4)
# stockscraper.calculate_cumulative_growth_with_search('BSM', 'USDTRY', start_date=month_4, end_date=month_2)
stockscraper.calculate_cumulative_growth_with_search('BSM', 'USDTRY', start_date=month_3, end_date=today)

stockscraper.calculate_cumulative_growth_with_search('BSM', 'USDTRY', start_date=month_6, end_date=today)
"""