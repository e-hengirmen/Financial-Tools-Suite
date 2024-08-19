import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd



class IndexTrendVisualiser:
    def __init__(self, ticker="^GSPC"):
        self.ticker = ticker

    def collect_data(self):
        """Collect S&P 500 data from Yahoo Finance."""
    
        sp500 = yf.Ticker(self.ticker)
        data = sp500.history(period="10y")
        data.reset_index(inplace=True)
    
        return data

    def calculate_results_and_last_x_days(self, data, drop_percent=5.5, period=2, prev_day_count=10, next_day_count=10, current_day=14):
        """Calculate the N days before and M days after each drop of X percent in the last Y days, and the last X days."""
    
        data['Pct_Change'] = data['Close'].pct_change(periods=period) * 100
        # Find the indices where the drop is more than the specified percentage
        drop_indices = data[data['Pct_Change'] <= -drop_percent].index.tolist()
    
        result = []
        # Loop over each drop index
        for idx in drop_indices:
            start_idx = max(0, idx - prev_day_count)  # Ensure we don't go below index 0
            end_idx = min(len(data), idx + next_day_count + 1)  # Ensure we don't exceed the data length
            surrounding_data = data.loc[start_idx:end_idx, ['Date', 'Close']].values.tolist()
            result.append(surrounding_data)
        # Extract the last X days of data
        last_x_days = data.tail(current_day)[['Date', 'Close']].values.tolist()
   
        return result, last_x_days

    def filter_events_by_skip_limit(self, events, skip_same_limit):
        """Filter events to skip those that start within a certain limit of previous events."""
    
        filtered_events = []
        last_event_date = None
        for event in events:
            start_date = pd.to_datetime(event[0][0])  # Convert to datetime if necessary
            if last_event_date is not None:
                if (start_date - last_event_date).days <= skip_same_limit:
                    continue
            filtered_events.append(event)
            last_event_date = start_date
        
        return filtered_events

    def create_graph(self, match_day=14):
        """Create a graph with the percentage changes for each event and the last X days."""
    
        plt.figure(figsize=(14, 7))
        for i, period_data in enumerate(self.result):
            # Extract the close prices
            # Calculate the percentage change relative to the matching day's close value
            close_prices = [entry[1] for entry in period_data]
            match_day_value = close_prices[match_day]
            percentage_changes = [(price - match_day_value) / match_day_value * 100 for price in close_prices]
            # Extract the start date and plot percentage changes
            start_date = period_data[0][0].strftime('%Y-%m-%d')
            plt.plot(percentage_changes, label=f'Start Date: {start_date}')

        # Calculate the percentage changes for the last X days centered at xth day
        last_x_mid_value = self.last_x_days[match_day][1]
        last_x_percentage_changes = [(price - last_x_mid_value) / last_x_mid_value * 100 for _, price in self.last_x_days]

        last_x_start_date = self.last_x_days[0][0].strftime('%Y-%m-%d')
        plt.plot(last_x_percentage_changes, label=f'Current movement: {last_x_start_date}', color='black', linewidth=2)

        plt.title('S&P 500 Percentage Changes (Centered at Drop Day)')
        plt.xlabel('Days Relative to Drop (0 = Day of Drop)')
        plt.ylabel('Percentage Change (%)')

        plt.grid(True)
        plt.legend(loc="upper right", fontsize='small', ncol=2)
        plt.show()

    def process_data(
        self,
        current_day,
        drop_percent,
        period,
        previous_days=10,
        next_days=20,
        skip_same=True,
        skip_same_limit=20,
    ):
        data = self.collect_data()
        self.result, self.last_x_days = self.calculate_results_and_last_x_days(data, drop_percent=drop_percent, period=period, prev_day_count=previous_days, next_day_count=next_days, current_day=current_day)
        if skip_same:
            self.result = self.filter_events_by_skip_limit(self.result, skip_same_limit)
