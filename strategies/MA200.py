import pandas as pd
import pandas_market_calendars as market_calendar
from pyalgotrade import strategy
from pyalgotrade.technical import ma


class MA200(strategy.BacktestingStrategy):

    def __init__(self, feed, instrument):
        super(MA200, self).__init__(feed)
        self.instrument = instrument
        self.position = None
        self.ma = ma.SMA(feed[instrument].getAdjCloseDataSeries(), 200)
        self.setUseAdjustedValues(True)
        
        def checkDate():
            nyse = market_calendar.get_calendar('NYSE')
            df = nyse.schedule(start_date='2000-01-01', end_date = '2030-01-01')
            df = df.groupby(df.index.strftime('%Y-%m')).tail(1)
            df['date'] = pd.to_datetime(df['market_open']).dt.date
            last_days_of_month = [date.isoformat() for date in df['date'].tolist()]
            return last_days_of_month

        self.datelist = checkDate()
    
    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info(f"===== BUY at {execInfo.getPrice()} {execInfo.getQuantity()} =====")

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info(f"===== SELL at {execInfo.getPrice()} =====")
        self.position = None

    def onBars(self, bars):
        if self.ma[-1] is None:
            return
        
        bar = bars[self.instrument]
        close = bar.getAdjClose()
        date = bar.getDateTime().date().isoformat()

        if date in self.datelist:
            if self.position is None:
                broker = self.getBroker()
                cash = broker.getCash() * .98

                if date in self.datelist and close > self.ma[-1]:
                    quantity = cash / close
                    self.info(f"buying at {close}, which is above {self.ma[-1]}")
                    self.position = self.enterLong(self.instrument, quantity)

            elif close < self.ma[-1] and self.position is not None:
                self.info(f"selling at {close}, which is below {self.ma[-1]}")
                self.position.exitMarket()
                self.position = None