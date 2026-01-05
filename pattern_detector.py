import numpy as np
from scipy.signal import find_peaks

# -----------------------------
# Smart Money Detector
# -----------------------------
class SmartMoneyDetector:
    def __init__(self, df):
        self.df = df

    def detect_all_patterns(self):
        return {
            "order_blocks": self.df.tail(5).to_dict(),
            "fvgs": self.df.tail(3).to_dict()
        }

# -----------------------------
# Elliott Wave Detector
# -----------------------------
class ElliotWaveDetector:
    def __init__(self, df):
        self.df = df

    def detect_waves(self):
        try:
            highs = np.asarray(self.df["high"], dtype=float).ravel()
            if len(highs) < 20:
                return []
            peaks, _ = find_peaks(highs, distance=5)
            return peaks.tolist()
        except Exception:
            return []

# -----------------------------
# ADVANCED SUPPORT / RESISTANCE
# -----------------------------
class SupportResistanceDetector:
    def __init__(self, df):
        self.df = df

    # -------- Swing Points --------
    def _swing_highs(self, lookback=5):
        highs = self.df["high"].values
        idx, _ = find_peaks(highs, distance=lookback)
        return idx

    def _swing_lows(self, lookback=5):
        lows = -self.df["low"].values
        idx, _ = find_peaks(lows, distance=lookback)
        return idx

    # -------- Volume Weight --------
    def _volume_weight(self, idx):
        vols = self.df["volume"].values
        avg_vol = np.mean(vols)
        return vols[idx] / avg_vol if avg_vol > 0 else 1

    # -------- Level Strength --------
    def _classify_strength(self, touches, vol_weight):
        score = touches * vol_weight
        return "strong" if score >= 2.5 else "weak"

    # -------- Main Detection --------
    def detect_levels(self):
        prices_high = self.df["high"].values
        prices_low = self.df["low"].values

        swing_highs = self._swing_highs()
        swing_lows = self._swing_lows()

        resistance_levels = []
        support_levels = []

        # ----- Resistance -----
        for idx in swing_highs[-10:]:
            price = prices_high[idx]
            touches = sum(abs(prices_high - price) < price * 0.002)
            vol_w = self._volume_weight(idx)
            strength = self._classify_strength(touches, vol_w)

            resistance_levels.append({
                "price": float(price),
                "strength": strength,
                "touches": int(touches),
                "volume_weight": round(vol_w, 2)
            })

        # ----- Support -----
        for idx in swing_lows[-10:]:
            price = prices_low[idx]
            touches = sum(abs(prices_low - price) < price * 0.002)
            vol_w = self._volume_weight(idx)
            strength = self._classify_strength(touches, vol_w)

            support_levels.append({
                "price": float(price),
                "strength": strength,
                "touches": int(touches),
                "volume_weight": round(vol_w, 2)
            })

        # ----- HTF vs LTF separation -----
        # HTF = strongest levels
        strong_support = sorted(
            [s for s in support_levels if s["strength"] == "strong"],
            key=lambda x: x["price"]
        )

        strong_resistance = sorted(
            [r for r in resistance_levels if r["strength"] == "strong"],
            key=lambda x: x["price"]
        )

        # LTF = weaker / execution levels
        weak_support = [s for s in support_levels if s["strength"] == "weak"]
        weak_resistance = [r for r in resistance_levels if r["strength"] == "weak"]

        return {
            "HTF_support": strong_support[:2],
            "HTF_resistance": strong_resistance[-2:],
            "LTF_support": weak_support[:2],
            "LTF_resistance": weak_resistance[-2:]
        }
