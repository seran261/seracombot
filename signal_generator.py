class SignalGenerator:
    def __init__(self, df, smc, waves, levels):
        self.df = df
        self.levels = levels

    # -------------------------
    # Helpers
    # -------------------------
    def price(self):
        return float(self.df["close"].iloc[-1])

    def prev(self):
        return float(self.df["close"].iloc[-2])

    def atr(self, period=14):
        return float((self.df["high"] - self.df["low"]).rolling(period).mean().iloc[-1])

    def nearest(self, levels, above=True):
        if not levels:
            return None
        p = self.price()
        prices = [l["price"] for l in levels]
        return min([x for x in prices if x > p], default=None) if above else max([x for x in prices if x < p], default=None)

    # -------------------------
    # Filters
    # -------------------------
    def liquidity_sweep(self, level, side):
        if not level:
            return False
        return (self.prev() < level < self.price()) if side == "buy" else (self.prev() > level > self.price())

    def break_hold(self, level, side):
        if not level:
            return False
        return self.price() >= level if side == "buy" else self.price() <= level

    # -------------------------
    # Confidence
    # -------------------------
    def confidence(self, rr, sweep, volume):
        score = 50
        if rr >= 1.3:
            score += 15
        if sweep:
            score += 15
        if volume:
            score += 10
        return min(score, 100)

    # -------------------------
    # MAIN ENGINE
    # -------------------------
    def generate_signals(self):
        try:
            price = self.price()
            atr = self.atr()

            htf_sup = self.levels.get("HTF_support", [])
            htf_res = self.levels.get("HTF_resistance", [])
            ltf_sup = self.levels.get("LTF_support", [])
            ltf_res = self.levels.get("LTF_resistance", [])

            htf_s = self.nearest(htf_sup, above=False)
            htf_r = self.nearest(htf_res, above=True)

            vol_ok = self.df["volume"].iloc[-1] > self.df["volume"].rolling(20).mean().iloc[-1]

            signals = []

            # =================================================
            # 🔥 LAYER 1 — HIGH CONFIDENCE (PREMIUM)
            # =================================================
            if htf_s and price > htf_s:
                sl = htf_s - atr * 0.4
                tp = htf_r
                if tp and sl and tp > price > sl:
                    rr = round((tp - price) / (price - sl), 2)
                    sweep = self.liquidity_sweep(htf_s, "buy")
                    conf = self.confidence(rr, sweep, vol_ok)

                    if rr >= 1.3 and conf >= 60:
                        return [{
                            "type": "BUY",
                            "entry": price,
                            "sl": sl,
                            "target": tp,
                            "rr": rr,
                            "confidence": conf,
                            "strength": "Premium HTF setup"
                        }]

            if htf_r and price < htf_r:
                sl = htf_r + atr * 0.4
                tp = htf_s
                if tp and sl and sl > price > tp:
                    rr = round((price - tp) / (sl - price), 2)
                    sweep = self.liquidity_sweep(htf_r, "sell")
                    conf = self.confidence(rr, sweep, vol_ok)

                    if rr >= 1.3 and conf >= 60:
                        return [{
                            "type": "SELL",
                            "entry": price,
                            "sl": sl,
                            "target": tp,
                            "rr": rr,
                            "confidence": conf,
                            "strength": "Premium HTF setup"
                        }]

            # =================================================
            # ⚙️ LAYER 2 — CONTINUATION / SCALP (FALLBACK)
            # =================================================
            if htf_s and self.break_hold(self.nearest(ltf_sup, False), "buy"):
                sl = htf_s - atr * 0.3
                tp = price + atr * 1.2
                rr = round((tp - price) / (price - sl), 2)

                if rr >= 1.1:
                    return [{
                        "type": "BUY",
                        "entry": price,
                        "sl": sl,
                        "target": tp,
                        "rr": rr,
                        "confidence": 55,
                        "strength": "Continuation"
                    }]

            if htf_r and self.break_hold(self.nearest(ltf_res, True), "sell"):
                sl = htf_r + atr * 0.3
                tp = price - atr * 1.2
                rr = round((price - tp) / (sl - price), 2)

                if rr >= 1.1:
                    return [{
                        "type": "SELL",
                        "entry": price,
                        "sl": sl,
                        "target": tp,
                        "rr": rr,
                        "confidence": 55,
                        "strength": "Continuation"
                    }]

            return []

        except Exception:
            return []
