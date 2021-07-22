from pyalgotrade import strategy

class BuyHold(strategy.BacktestingStrategy):

    def __init__(self, feed, instrument):
        super(BuyHold, self).__init__(feed)
        self.instrument = instrument
        self.setUseAdjustedValues(True)
        self.position = None

    def onEnterOk(self, position):
        self.info(f"{position.getEntryOrder().getExecutionInfo()}")
    
    def onBars(self, bars):
        bar = bars[self.instrument]

        if self.position is None:
            close = bar.getAdjClose()
            broker = self.getBroker()
            cash = broker.getCash() * .98
            quantity = cash / close

            self.position = self.enterLong(self.instrument, quantity)