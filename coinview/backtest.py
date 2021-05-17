#!/usr/bin/env python
import backtrader as bt
import datetime
import logging



class stoch_rsi_macd(bt.Strategy):

    params = (
        ('RSIPeriod', 14),
        ('stochperiod', 14),
        ('stochpfast', 3),
        ('stochpslow', 3),
        ('stochupperLimit', 80),
        ('stochlowerLimit', 20),
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9)
    )


    def __init__(self):
        self.rsi = bt.talib.RSI(self.data, period=self.p.RSIPeriod)
        self.stochastic = bt.indicators.Stochastic(self.data,
                                                   period=self.p.stochperiod,
                                                   period_dfast=self.p.stochpfast,
                                                   period_dslow=self.params.stochpslow,
                                                   upperband=self.params.stochupperLimit,
                                                   lowerband=self.params.stochlowerLimit)
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.stochastic_low = False
        self.rsiup = False
        self.macd_crossed = False
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                print('buy executed {}'.format(order.executed.price))
            elif order.issell():
                print('sell executed {}'.format(order.executed.price))

            self.bar_execute = len(self)

        self.order = None

    def next(self):
        # run next for every data period.
        if self.order:
            return

        if not self.position:  # if we are not already in the market
            if self.stochastic.lines.percD[0] < self.p.stochlowerLimit and self.stochastic.lines.percK[0] < self.p.stochlowerLimit:
                self.stochastic_low = True

            if self.rsi > 50:
                self.rsiup = True

            if self.mcross[0] > 0:
                self.macd_crossed = True
            elif self.mcross[0] < 0:
                self.macd_crossed = False

            if self.stochastic_low and self.rsiup and self.macd_crossed:
                if self.stochastic.lines.percD[0] < self.p.stochupperLimit and self.stochastic.lines.percK[0] < self.p.stochupperLimit:
                    print('BUY BUY BUY')
                    self.buy(size=1)
        else:
            if len(self) >= (self.bar_execute + 200):
                self.order = self.sell()
                self.stochastic_low = False
                self.rsiup = False
                self.macd_crossed = False

        #if self.up:
        #    print('IS TRENDING UP')
        #else:
        #    print('IS TRENDING DOWN')







cerebro = bt.Cerebro()
cerebro.broker.set_cash(10000)
print('Starting Portfolio Value %.2f' % cerebro.broker.getvalue())
fromdate = datetime.datetime.strptime('2020-07-01', '%Y-%m-%d')
todate = datetime.datetime.strptime('2020-07-30', '%Y-%m-%d')

data = bt.feeds.GenericCSVData(dataname='data/2020_5minute.csv', dtformat=2, compression=15, timeframe=bt.TimeFrame.Minutes, fromdate=fromdate, todate=todate)

cerebro.adddata(data)

cerebro.addstrategy(stoch_rsi_macd)

cerebro.run()
print('Ending Portfolio Value %.2f' % cerebro.broker.getvalue())

cerebro.plot()
