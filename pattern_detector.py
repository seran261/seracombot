import numpy as np
from scipy.signal import find_peaks

class SmartMoneyDetector:
    def __init__(self, df):
        self.df = df

    def detect_all_patterns(self):
        return {
            "order_blocks": self.df.tail(5).to_dict(),
            "fvgs": self.df.tail(3).to_dict()
        }

class ElliotWaveDetector:
    def __init__(self, df):
        self.df = df

    def detect_waves(self):
        """
        FIX:
        Ensure input to find_peaks is a clean 1D numpy array
        """
        try:
            high_series = self.df['high']

            # 🔥 CRITICAL FIX: flatten to 1D array
            high_values = np.asarray(high_series).astype(float).ravel()

            if len(high_values) < 10:
                return []

            peaks, _ = find_peaks(high_values, distance=5)
            return peaks.tolist()

        except Exception as e:
            # Fail-safe: never break the bot
            return []

class SupportResistanceDetector:
    def __init__(self, df):
        self.df = df

    def detect_levels(self):
        lows = np.asarray(self.df['low']).astype(float).ravel()
        highs = np.asarray(self.df['high']).astype(float).ravel()

        return {
            "s1": float(np.min(lows[-50:])),
            "s2": float(np.min(lows[-100:])),
            "r1": float(np.max(highs[-50:])),
            "r2": float(np.max(highs[-100:]))
        }
