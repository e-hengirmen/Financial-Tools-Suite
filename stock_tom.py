import cloudscraper
from datetime import datetime
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from copy import deepcopy
import yfinance as yf
import time
import os

import numpy as np
import pandas as pd

class TimePlotter:
    def plot_intraday_data(self, ticker, period="60d"):
        data = yf.download(ticker, period=period, interval="15m", auto_adjust=True)
        
        if data.empty:
            print(f"No data found for {ticker}.")
            return

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        df = data.reset_index()
        df['Date'] = df['Datetime'].dt.date
        df['TimeStr'] = df['Datetime'].dt.strftime('%H:%M')
        
        # Calculate % Change from Open
        daily_opens = df.groupby('Date')['Open'].transform('first')
        df['PctChange'] = ((df['Close'] - daily_opens) / daily_opens) * 100
        
        # --- Geometric Mean Calculation ---
        # Convert to growth factors: (1 + r) where r is decimal change
        # Adding 1 to the percentage decimal (e.g., 2% becomes 1.02)
        df['GrowthFactor'] = 1 + (df['PctChange'] / 100)
        
        # Calculate Geometric Mean per time interval
        # Formula: (product of growth factors)^(1/n) - 1
        geo_means = df.groupby('TimeStr')['GrowthFactor'].apply(
            lambda x: (np.prod(x)**(1/len(x)) - 1) * 100
        )
        
        print("\n--- Geometric Mean of % Changes by Time Interval ---")
        print(geo_means.sort_index())
        # ----------------------------------

        # Pivot and Plotting
        pivot_df = df.pivot(index='TimeStr', columns='Date', values='PctChange')
        plt.figure(figsize=(14, 7))
        
        for column in pivot_df.columns:
            plt.plot(pivot_df.index, pivot_df[column], alpha=0.3, linewidth=0.7)

        plt.axhline(0, color='black', linestyle='-', linewidth=1.5, alpha=0.6)
        plt.title(f"Intraday Percentage Change from Open for {ticker}")
        plt.ylabel("Percentage Change (%)")
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.show()

    def plot_monthly_stock(self, ticker, period="1y", plot=True):
        # 1. Handle Date Ranges for Single String or List Periods
        end_date = pd.Timestamp.now()
        
        if isinstance(period, (list, tuple)) and len(period) == 2:
            p1, p2 = period[0], period[1]
            # Calculate start and end dates manually to bypass yfinance's period limitation
            years_back_start = int(p1.replace('y', ''))
            years_back_end = int(p2.replace('y', ''))
            
            start_dt = (end_date - pd.DateOffset(years=years_back_start)).strftime('%Y-%m-%d')
            end_dt = (end_date - pd.DateOffset(years=years_back_end)).strftime('%Y-%m-%d')
            
            # Download using explicit start/end dates
            data = yf.download(ticker, start=start_dt, end=end_dt, interval="1d", auto_adjust=True)
            label_suffix = f"({p1} to {p2} ago)"
        else:
            # Standard download using standard string period
            data = yf.download(ticker, period=period, interval="1d", auto_adjust=True)
            label_suffix = f"(Last {period})"
        
        if data.empty:
            print(f"No data found for {ticker}.")
            return

        # Flatten MultiIndex if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        # 2. Resample to standard calendar days while 'Date' is still the index
        df_resampled = data.resample('D').ffill()
        df = df_resampled.reset_index()
        
        # Generate calendar tracking columns
        df['Day'] = df['Date'].dt.day
        df['Month'] = df['Date'].dt.to_period('M')
        
        # 3. Calculate the baseline using the LAST day of the PREVIOUS month
        last_day_of_months = df.groupby('Month').last().reset_index()
        last_day_of_months['NextMonth'] = last_day_of_months['Month'] + 1
        
        # Map the previous month's closing price into the current month's rows
        base_prices = dict(zip(last_day_of_months['NextMonth'].astype(str), last_day_of_months['Close']))
        
        df['MonthStr'] = df['Month'].astype(str)
        df['PrevMonthClose'] = df['MonthStr'].map(base_prices)
        
        # Drop rows that don't have a previous month base price (like the very first month)
        df = df.dropna(subset=['PrevMonthClose']).copy()
        
        # 4. Calculate % Change relative to Day 0 (Prev Month Close)
        df['PctChange'] = ((df['Close'] - df['PrevMonthClose']) / df['PrevMonthClose']) * 100
        
        # 5. Geometric Mean Calculation via growth factors
        df['GrowthFactor'] = 1 + (df['PctChange'] / 100)
        
        geo_means = df.groupby('Day')['GrowthFactor'].apply(
            lambda x: (np.prod(x)**(1/len(x)) - 1) * 100
        )
        
        # Create a synthetic Day 0 point that is always exactly 0%
        geo_means_dict = geo_means.to_dict()
        geo_means_final = {0: 0.0}
        geo_means_final.update(geo_means_dict)
        
        # 6. Print to Terminal (Now starting from Day 0)
        print(f"\n=========================================")
        print(f" GEOMETRIC MEAN TRAJECTORY FOR {ticker} {label_suffix}")
        print(f"=========================================")
        print(f"{'Calendar Day':<15}{'Average Compounded Return (%)':<30}")
        print(f"-----------------------------------------")
        for day in sorted(geo_means_final.keys()):
            val = geo_means_final[day]
            print(f"Day {day:<11}{val:>+6.2f}%")
        print(f"=========================================\n")

        if plot:
            # 7. Prepare Plotting Data
            pivot_data = df[['Day', 'MonthStr', 'PctChange']].drop_duplicates(subset=['Day', 'MonthStr'])
            pivot_df = pivot_data.pivot(index='Day', columns='MonthStr', values='PctChange')
            
            # Insert a Row 0 of all zeros into the pivot table for visual consistency
            pivot_df.loc[0] = 0.0
            pivot_df = pivot_df.sort_index()

            # 8. Generation of the Visualization
            plt.figure(figsize=(14, 7))
            
            for col in pivot_df.columns:
                plt.plot(pivot_df.index, pivot_df[col], alpha=0.15, color='gray', linewidth=0.8)
                    
            plt.plot(list(geo_means_final.keys()), list(geo_means_final.values()), color='black', linewidth=3, label="Day 0 Aligned Geo Mean")
            
            plt.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)
            plt.title(f"Monthly Performance Profiles: {ticker} {label_suffix}")
            plt.xlabel("Day of Month (0 = Prior Month Close)")
            plt.ylabel("Cumulative % Change from Prior Month Close")
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.3)
            plt.tight_layout()
            plt.show()
        return geo_means_final
    
    def save_processed_data(self, ticker, periods, geo_means):
        """
        Takes pre-calculated geometric mean data and period tracking lists,
        combines them into a single consolidated table, and writes it to a file named after the ticker.
        """
        import os
        import pandas as pd

        # 1. Setup paths and directory structure
        folder_name = "processed_data"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Created directory: {folder_name}")
            
        # Clean ticker name for file safety (e.g., XU100.IS -> XU100_IS)
        clean_ticker = ticker.replace(".", "_").replace(" ", "_")
        file_name = f"{clean_ticker}.txt"
        file_path = os.path.join(folder_name, file_name)
        
        # 2. Build a combined DataFrame using Day as the index
        combined_df = pd.DataFrame(index=sorted(geo_means[0].keys()))
        combined_df.index.name = "Calendar Day"

        for period, geo_data in zip(periods, geo_means):
            # Create a clean column name based on the period format
            if isinstance(period, (list, tuple)):
                col_name = f"{period[0]} to {period[1]} ago"
            else:
                col_name = f"Last {period}"
            
            # Map values (supporting both dictionaries and pandas Series)
            combined_df[col_name] = combined_df.index.map(geo_data)
        
        # 3. Format the data to string percentages (e.g., +1.25%)
        formatted_df = combined_df.map(lambda x: f"{x:>+6.2f}%" if pd.notnull(x) else "   N/A ")
        formatted_df = formatted_df.reset_index()
        
        # Add a custom 'Day ' prefix to the index column for clear text rendering
        formatted_df['Calendar Day'] = formatted_df['Calendar Day'].apply(lambda x: f"Day {x:<2}")

        # 4. Write data to the formatted file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"=========================================================================\n")
            f.write(f" CONSOLIDATED INTRAMONTH CHANGES FOR {ticker}\n")
            f.write(f"=========================================================================\n")
            
            # Use pandas built-in text table layout generator
            f.write(formatted_df.to_string(index=False))
            
            f.write(f"\n=========================================================================\n")
            
        print(f"Successfully compiled all timelines into a single table at: {file_path}")



tp = TimePlotter()


"""
stockscraper.create_tables(['BSM'])

# Doğrudan yeni ismiyle çağırma
stockscraper.calculate_cumulative_growth_with_search('BSM', 'USDTRY', start_date=month_12, end_date=month_6)
# stockscraper.calculate_cumulative_growth_with_search('BSM', 'USDTRY', start_date=month_6, end_date=month_4)
# stockscraper.calculate_cumulative_growth_with_search('BSM', 'USDTRY', start_date=month_4, end_date=month_2)
stockscraper.calculate_cumulative_growth_with_search('BSM', 'USDTRY', start_date=month_3, end_date=today)

stockscraper.calculate_cumulative_growth_with_search('BSM', 'USDTRY', start_date=month_6, end_date=today)
"""



ticker = "XU100.IS"
periods = [
"2y",
"5y",
"25y",
["25y", "7y"],
]

geo_means = []
for period in periods:
    geo_mean = tp.plot_monthly_stock(ticker, period, plot=False)
    geo_means.append(geo_mean)


tp.save_processed_data(ticker, periods, geo_means)