from pyalgotrade import strategy
from pyalgotrade.technical import ma

class DeathCross(strategy.BacktestingStrategy):

    def __init__(self, feed, instrument):
        super(DeathCross, self).__init__(feed)
        self.instrument = instrument
        self.position = None
        self.ema50 = ma.EMA(feed[instrument].getAdjCloseDataSeries(), 50)
        self.ema200 = ma.EMA(feed[instrument].getAdjCloseDataSeries(), 200)
        self.setUseAdjustedValues(True)

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info(f"===== BUY at {execInfo.getPrice()} {execInfo.getQuantity()} =====")

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info(f"===== SELL at {execInfo.getPrice()} =====")
        self.position = None

    def onBars(self, bars):
        if self.ema50[-1] is None or self.ema200[-1] is None:
            return
        
        bar = bars[self.instrument]
        close = bar.getAdjClose()
        date = bar.getDateTime().date().isoformat()

        if self.position is None:
            broker = self.getBroker()
            cash = broker.getCash() * .98

            if self.ema50[-1] > self.ema200[-1]:
                quantity = cash / close
                self.info(f"buying at {close}, as EMA50: {self.ema50[-1]} is ABOVE EMA200: {self.ema200[-1]}")
                self.position = self.enterLong(self.instrument, quantity)

        elif self.ema50[-1] < self.ema200[-1] and self.position is not None:
            self.info(f"selling at {close}, as EMA50: {self.ema50[-1]} is BELOW EMA200: {self.ema200[-1]}")
            self.position.exitMarket()
            self.position = None