import numpy as np
from scipy.signal import find_peaks

# -----------------------------
# Smart Money Concepts (SAFE)
# -----------------------------
class SmartMoneyDetector:
    def __init__(self, df):
        self.df = df

    def detect_all_patterns(self):
        # Minimal, safe placeholders (won’t crash)
        return {
            "order_blocks": self.df.tail(5).to_dict(),
            "fvgs": self.df.tail(3).to_dict()
        }

# -----------------------------
# Elliott Wave Detector (SAFE)
# -----------------------------
class ElliotWaveDetector:
    def __init__(self, df):
        self.df = df

    def detect_waves(self):
        try:
            highs = np.asarray(self.df["high"], dtype=float).ravel()
            if len(highs) < 10:
                return []

            peaks, _ = find_peaks(highs, distance=5)
            return peaks.tolist()
        except Exception:
            # Never crash the bot
            return []

# -----------------------------
# Support / Resistance (SAFE)
# -----------------------------
class SupportResistanceDetector:
    def __init__(self, df):
        self.df = df

    def detect_levels(self):
        lows = np.asarray(self.df["low"], dtype=float).ravel()
        highs = np.asarray(self.df["high"], dtype=float).ravel()

        return {
            "s1": float(np.min(lows[-50:])),
            "s2": float(np.min(lows[-100:])),
            "r1": float(np.max(highs[-50:])),
            "r2": float(np.max(highs[-100:]))
        }
