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
        high = self.df["high"]
        low = self.df["low"]
        close = self.df["close"]
        tr = (high - low).rolling(period).mean()
        return float(tr.iloc[-1])

    def nearest(self, levels, above=True):
        p = self.price()
        prices = [l["price"] for l in levels]
        if above:
            higher = [x for x in prices if x > p]
            return min(higher) if higher else None
        else:
            lower = [x for x in prices if x < p]
            return max(lower) if lower else None

    # -------------------------
    # Market structure logic
    # -------------------------
    def in_htf_midrange(self, support, resistance):
        if not support or not resistance:
            return False
        mid = (support + resistance) / 2
        return abs(self.price() - mid) / mid < 0.002  # ~0.2%

    def liquidity_sweep(self, level, direction):
        """
        Price sweeps HTF level and closes back inside
        """
        if not level:
            return False

        prev = self.prev_price()
        curr = self.price()

        if direction == "buy":
            return prev < level and curr > level
        else:
            return prev > level and curr < level

    def break_and_retest(self, level, direction):
        """
        Break → pullback → continuation
        """
        if not level:
            return False

        prev = self.prev_price()
        curr = self.price()

        if direction == "buy":
            return prev > level and curr >= level
        else:
            return prev < level and curr <= level

    # -------------------------
    # Confidence scoring
    # -------------------------
    def confidence(self, rr, sweep, retest, volume_ok):
        score = 40
        if sweep:
            score += 20
        if retest:
            score += 15
        if rr >= 2:
            score += 15
        if volume_ok:
            score += 10
        return min(score, 100)

    # -------------------------
    # Main Signal Engine
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

            # 🔒 Disable trading in HTF midpoint
            if self.in_htf_midrange(htf_support, htf_resistance):
                return []

            signals = []

            # =========================
            # LONG SETUP
            # =========================
            if htf_support and price > htf_support:
                sweep = self.liquidity_sweep(htf_support, "buy")
                retest = self.break_and_retest(
                    self.nearest(ltf_sup, above=False), "buy"
                )

                if sweep and retest:
                    entry = price
                    sl = htf_support - atr * 0.5   # 🔥 SL beyond HTF
                    tp = htf_resistance

                    if tp and sl and tp > entry > sl:
                        rr = round((tp - entry) / (entry - sl), 2)
                        if rr >= 1.5:
                            vol_ok = self.df["volume"].iloc[-1] > self.df["volume"].rolling(20).mean().iloc[-1]
                            conf = self.confidence(rr, sweep, retest, vol_ok)

                            signals.append({
                                "type": "BUY",
                                "entry": entry,
                                "sl": sl,
                                "target": tp,
                                "rr": rr,
                                "strength": f"Confidence {conf}/100",
                                "confidence": conf
                            })

            # =========================
            # SHORT SETUP
            # =========================
            if htf_resistance and price < htf_resistance:
                sweep = self.liquidity_sweep(htf_resistance, "sell")
                retest = self.break_and_retest(
                    self.nearest(ltf_res, above=True), "sell"
                )

                if sweep and retest:
                    entry = price
                    sl = htf_resistance + atr * 0.5
                    tp = htf_support

                    if tp and sl and sl > entry > tp:
                        rr = round((entry - tp) / (sl - entry), 2)
                        if rr >= 1.5:
                            vol_ok = self.df["volume"].iloc[-1] > self.df["volume"].rolling(20).mean().iloc[-1]
                            conf = self.confidence(rr, sweep, retest, vol_ok)

                            signals.append({
                                "type": "SELL",
                                "entry": entry,
                                "sl": sl,
                                "target": tp,
                                "rr": rr,
                                "strength": f"Confidence {conf}/100",
                                "confidence": conf
                            })

            return signals

        except Exception:
            return []
