from enum import Enum


class UserTarifPlan(str, Enum):
    Base = "base"
    Premium = "premium"
