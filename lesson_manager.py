import os.path
import json
from typing import Iterable

from constants.sentence_type_enum import SentenceType

"""
   1. Start with Hiragana and Katakana words
   2. Reading examples for any of them
   3. Once all have been seen at least 20 times and have > 90% accuracy, introduce new Kanji
   4. Introduce Kanji in order of most frequently used.
   5. Allow AI to pick from at most N previously seen Kanji as well
   6. Follow steps 2 and 3
   """

class LessonManager:
    _KANJI_STATS_PATH = './data/kanji_stats.json'
    _WORD_STATS_PATH = './data/other_stats.json'
    _KANJI_PATH = './data/kanji_freq_list.txt'

    ACCURACY_THRESHOLD = 0.8
    MIN_SEEN_THRESHOLD = 5
    MIN_WORDS = 20  # Always introduce new words if below
    REQ_HIRA_KATA_WORDS = 100  # Only introduce Kanji above this

    def __init__(self):
        self.word_stats = self._load_stats(self._WORD_STATS_PATH)
        self.kanji_stats = self._load_stats(self._KANJI_STATS_PATH)

    def get_focus_words(self, count=1) -> (SentenceType, list[str]):
        """
        Picks the count words/kanji to focus on in the next exercise
        TODO Rewrite to avoid duplicate data and repeated calculations
        """
        # If not words shown yet ask for a new one
        if len(self.word_stats) < self.MIN_WORDS:
            return SentenceType.NEW_HIRAKATA, list(self.word_stats.keys())[:count-1]

        combined_stats = self.word_stats | self.kanji_stats

        # Calculate accuracies
        accuracies = [[c, correct / seen] if seen else [c, 0.0] for c, (seen, correct) in combined_stats.items()]

        # Sort from lowest to highest
        accuracies = sorted(accuracies, key=lambda x: x[1])

        # If at least one is below 90% accurate, practice it
        if accuracies[0][1] < self.ACCURACY_THRESHOLD:
            return SentenceType.EXISTING_WORD, [c for c, _ in accuracies[:count]]

        # Otherwise check seen count
        seen_counts = sorted([[c, seen] for c, (seen, correct) in combined_stats.items()], key=lambda x: x[1])

        # If at least one is below the seen threshold, practice it
        if seen_counts[0][1] < self.MIN_SEEN_THRESHOLD:
            return SentenceType.EXISTING_WORD, [c for c, _ in seen_counts[:count]]

        # If all else is fine, introduce a new character
        # Hiragana and Katakana only
        if len(self.word_stats) < self.REQ_HIRA_KATA_WORDS:
            return SentenceType.MORE_HIRAKATA, list(self.word_stats.keys())[:count - 1]

        # Kanji
        next_kanji = self._load_kanji(len(self.kanji_stats))

        if next_kanji:
            self.kanji_stats[next_kanji] = (0, 0)
            return SentenceType.NEW_KANJI, [c for c, _ in seen_counts[:count - 1]] + [next_kanji]

        # Final guard: Return least seen
        return SentenceType.EXISTING_WORD, [c for c, _ in seen_counts[:count]]

    def _load_stats(self, stats_path: str):
        """
        Loads the stats for the specified dataset, creating them if necessary.
        stats are in the form {word: (seen count, correct count), ...}
        """

        if not os.path.exists(stats_path):
            stats = {}
            with open(stats_path, 'w') as f:
                json.dump(stats, f)
        else:
            with open(stats_path, 'r') as f:
                stats = json.load(f)
        return stats

    def _save_stats(self):
        with open(self._WORD_STATS_PATH, 'w') as f:
            json.dump(self.word_stats, f)

        with open(self._KANJI_STATS_PATH, 'w') as f:
            json.dump(self.kanji_stats, f)

    def _load_kanji(self, idx):
        with open(self._KANJI_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if idx >= len(lines):
                return None

            return lines[idx].strip()
