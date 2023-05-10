from enum import Enum, auto


class SentenceType(Enum):
    NEW_HIRAKATA = auto()
    MORE_HIRAKATA = auto()
    EXISTING_WORD = auto()
    NEW_KANJI = auto()