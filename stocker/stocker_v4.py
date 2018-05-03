import quandl
import pandas as pd
import numpy as np
import fbprophet

class Stocker_v4():

    mainDays = None
    # Initialization requires a ticker symbol
    def __init__(self, ticker, timer, exchange='NSE'):
        print('In stocker_v4')
        # Enforce capitalization
        ticker = ticker.upper()

        # Symbol is used for labeling plots
        self.symbol = ticker
        self.mainDays = timer
        # Use Api Key
        quandl.ApiConfig.api_key = 'AL5rA7kD-SXUJiSFx2eM'

        # Retrieval the financial data
        try:
            print('Try')
            stock = quandl.get('%s/%s' % (exchange, ticker))
            print(stock.head())
        except Exception as e:
            print('Error Retrieving Data.')
            stock = pd.read_csv('20MICRONS.csv',parse_dates=['Date'])



        # Set date as Index
        stock = stock.reset_index(level=0)

        # Columns required for prophet
        stock['ds'] = stock['Date']

        if ('Adj. Close' not in stock.columns):
            stock['Adj. Close'] = stock['Close']
            stock['Adj. Open'] = stock['Open']

        stock['y'] = stock['Adj. Close']
        stock['Daily Change'] = stock['Adj. Close'] - stock['Adj. Open']

        # Data copied to class
        self.stock = stock.copy()

        # Minimum and maximum date in range
        self.min_date = min(stock['Date'])
        self.max_date = max(stock['Date'])


        # Number of years of data to train on
        self.training_years = 3

        # Prophet
        # Default
        self.changepoint_prior_scale = 0.05
        self.weekly_seasonality = False
        self.daily_seasonality = False
        self.monthly_seasonality = True
        self.yearly_seasonality = True
        self.changepoints = None

        print('{} Stocker Initialized. Data covers {} to {}.'.format(self.symbol,
                                                                     self.min_date.date(),
                                                                     self.max_date.date()))

    """
    Make sure start and end dates are in the range and can be
    converted to pandas datetimes. Returns dates in the correct format
    """

    def handle_dates(self, start_date = None, end_date = None):

        # Default start and end date are the beginning and end of data
        if start_date is None:
            start_date = self.min_date
        if end_date is None:
            end_date = self.max_date

        try:
            # Convert to pandas datetime for indexing dataframe
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

        except Exception as e:
            print('Invalid date format.')
            return


        return start_date, end_date

    def make_df(self,start_date = None, end_date = None):

        df = self.stock.copy()

        start_date, end_date = self.handle_dates(start_date, end_date)

        trim_df = df[(df['Date'] >= start_date.date()) &
                     (df['Date'] <= end_date.date())]

        return trim_df

    # Basic Historical Plots and Basic Statistics
    def plot_stock(self, start_date=None, stats=['Adj. Close']):

        self.reset_plot()

        # Assign dates
        if start_date is None:
            start_date = self.min_date

        # Get dataframe
        stock_plot = self.make_df(start_date)

        for i, stat in enumerate(stats):

            stat_min = min(stock_plot[stat])
            stat_max = max(stock_plot[stat])

            date_stat_min = stock_plot[stock_plot[stat] == stat_min]['Date']
            date_stat_min = date_stat_min[date_stat_min.index[0]].date()
            date_stat_max = stock_plot[stock_plot[stat] == stat_max]['Date']
            date_stat_max = date_stat_max[date_stat_max.index[0]].date()

            print('Maximum {} = {:.2f} on {}.'.format(stat, stat_max, date_stat_max))
            print('Minimum {} = {:.2f} on {}.'.format(stat, stat_min, date_stat_min))
            print('Current {} = {:.2f} on {}.\n'.format(stat, self.stock.ix[len(self.stock) - 1, stat],
                                                        self.max_date.date()))

            return stock_plot['Date'], stock_plot[stat]


    # Junk Method
    @staticmethod
    def reset_plot():
        print("Reset Plot Used")


    # Create a prophet model without training
    def create_model(self):

        # Make the model
        model = fbprophet.Prophet(daily_seasonality=self.daily_seasonality,
                                  weekly_seasonality=self.weekly_seasonality,
                                  yearly_seasonality=self.yearly_seasonality,
                                  changepoint_prior_scale=self.changepoint_prior_scale,
                                  changepoints=self.changepoints)

        return model



    # Basic prophet model for specified number of days
    def create_prophet_model(self, days=mainDays):

        self.reset_plot()

        model = self.create_model()

        # Fit on the stock history for self.training_years number of years
        stock_history = self.stock[
            self.stock['Date'] > (self.max_date - pd.DateOffset(years=self.training_years)).date()]

        model.fit(stock_history)

        # Make and predict for next year with future dataframe
        future = model.make_future_dataframe(periods=days, freq='D')
        future = model.predict(future)

        if days > 0:
            # Print the predicted price
            print('Predicted Price on {} = ${:.2f}'.format(
                future.ix[len(future) - 1, 'ds'].date(), future.ix[len(future) - 1, 'yhat']))

        return stock_history['ds'], stock_history['y'], future['ds'], future['yhat'], future['ds'].dt.to_pydatetime(), future['yhat_upper'], future['yhat_lower']

    # Evaluate prediction model for one year
    def evaluate_prediction(self):

        # if start_date is None:
        start_date = self.max_date - pd.DateOffset(years=1)
        # if end_date is None:
        end_date = self.max_date

        start_date, end_date = self.handle_dates(start_date, end_date)

        # Training data starts self.training_years years before start date and goes up to start date
        train = self.stock[(self.stock['Date'] < start_date.date()) &
                           (self.stock['Date'] > (start_date - pd.DateOffset(years=self.training_years)).date())]

        # Testing data is specified in the range
        test = self.stock[(self.stock['Date'] >= start_date.date()) & (self.stock['Date'] <= end_date.date())]

        # Create and train the model
        model = self.create_model()
        model.fit(train)

        # Make a future dataframe and predictions
        future = model.make_future_dataframe(periods=365, freq='D')
        future = model.predict(future)

        # Merge predictions with the known values
        test = pd.merge(test, future, on='ds', how='inner')

        train = pd.merge(train, future, on='ds', how='inner')

        # Calculate the differences between consecutive measurements
        test['pred_diff'] = test['yhat'].diff()
        test['real_diff'] = test['y'].diff()

        # Correct is when we predicted the correct direction
        test['correct'] = (np.sign(test['pred_diff']) == np.sign(test['real_diff'])) * 1

        # Accuracy when we predict increase and decrease
        increase_accuracy = 100 * np.mean(test[test['pred_diff'] > 0]['correct'])
        decrease_accuracy = 100 * np.mean(test[test['pred_diff'] < 0]['correct'])

        # Calculate mean absolute error
        test_errors = abs(test['y'] - test['yhat'])
        test_mean_error = np.mean(test_errors)

        train_errors = abs(train['y'] - train['yhat'])
        train_mean_error = np.mean(train_errors)

        # Calculate percentage of time actual value within prediction range
        test['in_range'] = False

        for i in test.index:
            if (test.ix[i, 'y'] < test.ix[i, 'yhat_upper']) & (test.ix[i, 'y'] > test.ix[i, 'yhat_lower']):
                test.ix[i, 'in_range'] = True

        in_range_accuracy = 100 * np.mean(test['in_range'])



        # Date range of predictions
        print('\nPrediction Range: {} to {}.'.format(start_date.date(),
                                                     end_date.date()))

        # Final prediction vs actual value
        print('\nPredicted price on {} = ${:.2f}.'.format(max(future['ds']).date(),
                                                          future.ix[len(future) - 1, 'yhat']))
        print('Actual price on    {} = ${:.2f}.\n'.format(max(test['ds']).date(), test.ix[len(test) - 1, 'y']))

        print('Average Absolute Error on Training Data = ${:.2f}.'.format(train_mean_error))
        print('Average Absolute Error on Testing  Data = ${:.2f}.\n'.format(test_mean_error))

        # Direction accuracy
        print('When the model predicted an increase, the price increased {:.2f}% of the time.'.format(
            increase_accuracy))
        print('When the model predicted a  decrease, the price decreased  {:.2f}% of the time.\n'.format(
            decrease_accuracy))

        print('The actual value was within the {:d}% confidence interval {:.2f}% of the time.'.format(
            int(100 * model.interval_width), in_range_accuracy))

        return train['ds'], train['y'], test['ds'], test['y'], future['ds'], future['yhat']

