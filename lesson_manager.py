import os.path
import json
from typing import Iterable

"""
   1. Start with Hiragana and Katakana chars
   2. Reading examples for any of them
   3. Once all have been seen at least 20 times and have > 90% accuracy, introduce new Kanji
   4. Introduce Kanji in order of most frequently used.
   5. Allow AI to pick from at most N previously seen Kanji as well
   6. Follow steps 2 and 3
   """


def generate_hira_kata_alphabet():
    """
    Convienence function for generating all Hiragana and Katakana unicode characters.
    """
    hiragana_unicode_range = range(0x3041, 0x3097)
    katakana_unicode_range = range(0x30A1, 0x30F7)

    # Convert the unicode range to the characters
    hiragana = [chr(i) for i in hiragana_unicode_range]
    katakana = [chr(i) for i in katakana_unicode_range]

    yield from hiragana + katakana


class LessonManager:
    _KANJI_STATS_PATH = './data/kanji_stats.json'
    _OTHER_STATS_PATH = './data/other_stats.json'
    _KANJI_PATH = './data/kanji_freq_list.txt'

    ACCURACY_THRESHOLD = 0.9
    MIN_SEEN_THRESHOLD = 10

    def __init__(self):
        self.other_stats = self._load_stats(self._OTHER_STATS_PATH, generate_hira_kata_alphabet())
        self.kanji_stats = self._load_stats(self._KANJI_STATS_PATH, [])

    def get_focus_characters(self, count=1):
        """
        Picks the count chars to focus on in the next exercise
        TODO Rewrite to avoid duplicate data and repeated calculations
        """
        combined_stats = self.other_stats | self.kanji_stats

        # Calculate accuracies
        accuracies = [[c, correct / seen] if seen else [c, 0.0] for c, (seen, correct) in combined_stats.items()]

        # Sort from lowest to highest
        accuracies = sorted(accuracies, key=lambda x: x[1])

        # If at least one is below 90% accurate, practice it
        if accuracies[0][1] < self.ACCURACY_THRESHOLD:
            return [c for c, _ in accuracies[:count]]

        # Otherwise check seen count
        seen_counts = sorted([[c, seen] for c, (seen, correct) in combined_stats.items()], key=lambda x: x[1])

        # If at least one is below the seen threshold, practice it
        if seen_counts[0][1] < self.MIN_SEEN_THRESHOLD:
            return [c for c, _ in seen_counts[:count]]

        # If all else is fine, introduce a new character
        next_kanji = self._load_kanji(len(self.kanji_stats))

        if next_kanji:
            self.kanji_stats[next_kanji] = (0, 0)
            return [c for c, _ in seen_counts[:count - 1]] + [next_kanji]

        # Final guard: Return least seen
        return [c for c, _ in seen_counts[:count]]

    def _load_stats(self, stats_path: str, default_alphabet: Iterable):
        """
        Loads the stats for the specified alphabet, creating them if necessary.
        stats are in the form {character: (seen count, correct count), ...}
        """

        if not os.path.exists(stats_path):
            stats = {c: (0, 0) for c in default_alphabet}
            with open(stats_path, 'w') as f:
                json.dump(stats, f)
        else:
            with open(stats_path, 'r') as f:
                stats = json.load(f)
        return stats

    def _save_stats(self):
        with open(self._OTHER_STATS_PATH, 'w') as f:
            json.dump(self.other_stats, f)

        with open(self._KANJI_STATS_PATH, 'w') as f:
            json.dump(self.kanji_stats, f)

    def _load_kanji(self, idx):
        with open(self._KANJI_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if idx >= len(lines):
                return None

            return lines[idx].strip()
