"""
This module assigns the enum values to PointingState,
DishMode, Number of devices LivelinessProbeType, TimeoutState
"""
from enum import IntEnum, unique


@unique
class PointingState(IntEnum):
    """
    This is an enumerator class that contains PointingState values.
    """

    READY = 0
    SLEW = 1
    TRACK = 2
    SCAN = 3
    UNKNOWN = 4
    NONE = 5


@unique
class DishMode(IntEnum):
    """
    This class assigns the enum value to DishMode.
    """

    # ska-mid-dish-manager is having dependency conflicts with ska-tmc-common
    # So redefined DishMode enum, which reflects the ska-mid-dish-manager
    # DishMode enum.
    # We will work out on this separately once dish manager is sorted.
    STARTUP = 0
    SHUTDOWN = 1
    STANDBY_LP = 2
    STANDBY_FP = 3
    MAINTENANCE = 4
    STOW = 5
    CONFIG = 6
    OPERATE = 7
    UNKNOWN = 8
