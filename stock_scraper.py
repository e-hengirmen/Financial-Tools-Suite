import cloudscraper
from datetime import datetime
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

class StockScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.start_date = '2010-01-01'
        self.start_date_datetime = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        self.data_center = {}
    
    def get_data(self, abbr):
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

    def get_data_within(self, abbr, start_date, end_date):
        if type(start_date) is str:
            start_date = self.get_date(start_date)
        if type(end_date) is str:
            end_date = self.get_date(end_date)
        res = []
        for row in self.data_center[abbr]:
            if start_date <= row['date'] < end_date:
                res.append(row)
        initial_value = res[0]['value']
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
                data = finscraper.get_data_within(abbr, start_date, end_date)
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
        self.plot_graph(data_lists, titles)
    
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
            print(data)
            data_lists.append(data)
            titles.append(str(current_date))
            current_date = next_date
        self.plot_graph(data_lists, titles)





stockscraper = StockScraper()
general_fund_list = [
    'DVT',
    'IJC',
    'ICZ',
    'IJZ',
    'IHK',
    'YZG',
    'MJG',
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
stockscraper.create_tables(fund_list)


stockscraper.plot_within_dates(fund_list, '2023-06-01', '2024-1-18', drop_late_starts=True)
x = stockscraper.get_data_within('DVT', '2024-01-01', '2024-06-01')




stockscraper.plot_monthly('DVT', '2023-01-01', '2024-06-01')


