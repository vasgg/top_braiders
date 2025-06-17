from enum import IntEnum, StrEnum, auto


class Stage(StrEnum):
    PROD = auto()
    DEV = auto()


class AcceptanceChoice(IntEnum):
    YES = auto()
    NO = auto()
