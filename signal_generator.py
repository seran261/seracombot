class SignalGenerator:
    def __init__(self, df, smc, waves, levels):
        self.df = df
        self.levels = levels

    # -------------------------
    # Helpers
    # -------------------------
    def price(self):
        return float(self.df["close"].iloc[-1])

    def prev_price(self):
        return float(self.df["close"].iloc[-2])

    def atr(self, period=14):
        tr = (self.df["high"] - self.df["low"]).rolling(period).mean()
        return float(tr.iloc[-1])

    def nearest(self, levels, above=True):
        if not levels:
            return None
        p = self.price()
        prices = [l["price"] for l in levels]
        if above:
            higher = [x for x in prices if x > p]
            return min(higher) if higher else None
        else:
            lower = [x for x in prices if x < p]
            return max(lower) if lower else None

    # -------------------------
    # Structure logic
    # -------------------------
    def in_htf_midrange(self, sup, res):
        if not sup or not res:
            return False
        mid = (sup + res) / 2
        return abs(self.price() - mid) / mid < 0.001  # relaxed

    def liquidity_sweep(self, level, side):
        if not level:
            return False
        prev = self.prev_price()
        curr = self.price()
        return (prev < level and curr > level) if side == "buy" else (prev > level and curr < level)

    def break_retest(self, level, side):
        if not level:
            return False
        prev = self.prev_price()
        curr = self.price()
        return (prev >= level and curr >= level) if side == "buy" else (prev <= level and curr <= level)

    # -------------------------
    # Confidence scoring
    # -------------------------
    def confidence_score(self, rr, sweep, retest, volume_ok):
        score = 40
        if rr >= 1.3:
            score += 15
        if sweep:
            score += 15
        if retest:
            score += 15
        if volume_ok:
            score += 15
        return min(score, 100)

    # -------------------------
    # Main Engine
    # -------------------------
    def generate_signals(self):
        try:
            price = self.price()
            atr = self.atr()

            htf_sup = self.levels.get("HTF_support", [])
            htf_res = self.levels.get("HTF_resistance", [])
            ltf_sup = self.levels.get("LTF_support", [])
            ltf_res = self.levels.get("LTF_resistance", [])

            htf_support = self.nearest(htf_sup, above=False)
            htf_resistance = self.nearest(htf_res, above=True)

            # 🔒 Skip bad HTF structure
            if self.in_htf_midrange(htf_support, htf_resistance):
                return []

            signals = []

            # =========================
            # BUY SETUP
            # =========================
            if htf_support and price > htf_support:
                entry = price
                sl = htf_support - atr * 0.4
                tp = htf_resistance

                if tp and sl and tp > entry > sl:
                    rr = round((tp - entry) / (entry - sl), 2)
                    sweep = self.liquidity_sweep(htf_support, "buy")
                    retest = self.break_retest(self.nearest(ltf_sup, False), "buy")
                    volume_ok = self.df["volume"].iloc[-1] > self.df["volume"].rolling(20).mean().iloc[-1]

                    conf = self.confidence_score(rr, sweep, retest, volume_ok)

                    if rr >= 1.3 and conf >= 60:
                        signals.append({
                            "type": "BUY",
                            "entry": entry,
                            "sl": sl,
                            "target": tp,
                            "rr": rr,
                            "confidence": conf,
                            "strength": f"{conf}/100"
                        })

            # =========================
            # SELL SETUP
            # =========================
            if htf_resistance and price < htf_resistance:
                entry = price
                sl = htf_resistance + atr * 0.4
                tp = htf_support

                if tp and sl and sl > entry > tp:
                    rr = round((entry - tp) / (sl - entry), 2)
                    sweep = self.liquidity_sweep(htf_resistance, "sell")
                    retest = self.break_retest(self.nearest(ltf_res, True), "sell")
                    volume_ok = self.df["volume"].iloc[-1] > self.df["volume"].rolling(20).mean().iloc[-1]

                    conf = self.confidence_score(rr, sweep, retest, volume_ok)

                    if rr >= 1.3 and conf >= 60:
                        signals.append({
                            "type": "SELL",
                            "entry": entry,
                            "sl": sl,
                            "target": tp,
                            "rr": rr,
                            "confidence": conf,
                            "strength": f"{conf}/100"
                        })

            return signals

        except Exception:
            return []
