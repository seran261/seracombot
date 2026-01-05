class SignalGenerator:
    def __init__(self, df, smc, waves, levels):
        self.df = df
        self.levels = levels

    def _get_price(self):
        return float(self.df["close"].iloc[-1])

    def _nearest_level(self, levels, above=True):
        """
        Find nearest level above or below price
        """
        price = self._get_price()
        prices = [lvl["price"] for lvl in levels]

        if above:
            higher = [p for p in prices if p > price]
            return min(higher) if higher else None
        else:
            lower = [p for p in prices if p < price]
            return max(lower) if lower else None

    def generate_signals(self):
        try:
            price = self._get_price()

            htf_sup = self.levels.get("HTF_support", [])
            htf_res = self.levels.get("HTF_resistance", [])
            ltf_sup = self.levels.get("LTF_support", [])
            ltf_res = self.levels.get("LTF_resistance", [])

            signals = []

            # -------------------------
            # HTF BIAS
            # -------------------------
            htf_support_price = self._nearest_level(htf_sup, above=False)
            htf_resistance_price = self._nearest_level(htf_res, above=True)

            # -------------------------
            # LONG SETUP
            # -------------------------
            if htf_support_price and price > htf_support_price:
                entry = self._nearest_level(ltf_sup, above=False) or price
                sl = htf_support_price
                tp = htf_resistance_price

                if tp and sl and tp > entry > sl:
                    rr = round((tp - entry) / (entry - sl), 2)
                    if rr >= 1.5:
                        signals.append({
                            "type": "BUY",
                            "entry": entry,
                            "sl": sl,
                            "target": tp,
                            "rr": rr,
                            "strength": "HTF+LTF confluence"
                        })

            # -------------------------
            # SHORT SETUP
            # -------------------------
            if htf_resistance_price and price < htf_resistance_price:
                entry = self._nearest_level(ltf_res, above=True) or price
                sl = htf_resistance_price
                tp = htf_support_price

                if tp and sl and sl > entry > tp:
                    rr = round((entry - tp) / (sl - entry), 2)
                    if rr >= 1.5:
                        signals.append({
                            "type": "SELL",
                            "entry": entry,
                            "sl": sl,
                            "target": tp,
                            "rr": rr,
                            "strength": "HTF+LTF confluence"
                        })

            return signals

        except Exception:
            # 🔒 Never crash bot
            return []
