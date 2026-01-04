class SignalGenerator:
    def __init__(self, df, smc, waves, levels):
        self.df = df
        self.levels = levels

    def generate_signals(self):
        price = self.df['close'].iloc[-1]

        if price > self.levels['s1']:
            return [{
                "type": "BUY",
                "entry": price,
                "sl": self.levels['s1'],
                "target": self.levels['r1'],
                "rr": abs(self.levels['r1'] - price) / abs(price - self.levels['s1']),
                "strength": 70
            }]
        return []
