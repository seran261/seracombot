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
        peaks, _ = find_peaks(self.df['high'], distance=5)
        return peaks.tolist()

class SupportResistanceDetector:
    def __init__(self, df):
        self.df = df

    def detect_levels(self):
        return {
            "s1": self.df['low'].tail(50).min(),
            "s2": self.df['low'].tail(100).min(),
            "r1": self.df['high'].tail(50).max(),
            "r2": self.df['high'].tail(100).max()
        }
