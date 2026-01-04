class SignalGenerator:
    def __init__(self, df, smc, waves, levels):
        self.df = df
        self.levels = levels

    def generate_signals(self):
        try:
            # 🔥 FORCE scalar values
            price = float(self.df['close'].iloc[-1])
            s1 = float(self.levels['s1'])
            r1 = float(self.levels['r1'])

            # Basic validation
            if s1 <= 0 or r1 <= 0:
                return []

            signals = []

            if price > s1:
                signals.append({
                    "type": "BUY",
                    "entry": price,
                    "sl": s1,
                    "target": r1,
                    "rr": round(abs(r1 - price) / abs(price - s1), 2),
                    "strength": 70
                })

            elif price < r1:
                signals.append({
                    "type": "SELL",
                    "entry": price,
                    "sl": r1,
                    "target": s1,
                    "rr": round(abs(price - s1) / abs(r1 - price), 2),
                    "strength": 70
                })

            return signals

        except Exception:
            # Fail-safe: never break the bot
            return []
