"""Enum to used in tests
"""
import enum
from enum import IntEnum, unique


@unique
class DishMode(IntEnum):
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


@unique
class SubarrayState(IntEnum):
    ON = 0
    OFF = 1
    FAULT = 8
    INIT = 9
    UNKNOWN = 13


@unique
class SubarrayObsState(IntEnum):
    EMPTY = 0
    RESOURCING = 1
    IDLE = 2
    CONFIGURING = 3
    READY = 4
    SCANNING = 5


@unique
class SimulatorDeviceType(IntEnum):
    MID_CSP_DEVICE = 0
    MID_SDP_DEVICE = 1
    DISH_DEVICE = 2
    MID_CSP_MASTER_DEVICE = 3
    MID_SDP_MASTER_DEVICE = 4


class FaultType(enum.IntEnum):
    """Enum class for raising various exceptions from helper devices."""

    NONE = 0
    COMMAND_NOT_ALLOWED = 1
    FAILED_RESULT = 2
    LONG_RUNNING_EXCEPTION = 3
    STUCK_IN_INTERMEDIATE_STATE = 4
    STUCK_IN_OBSTATE = 5


class ResultCode(enum.IntEnum):
    """Python enumerated type for command result codes."""

    OK = 0
    """The command was executed successfully."""

    STARTED = 1
    """The command has been accepted and will start immediately."""

    QUEUED = 2
    """The command has been accepted and will be executed at a future time."""

    FAILED = 3
    """The command could not be executed."""

    UNKNOWN = 4
    """The status of the command is not known."""

    REJECTED = 5
    """The command execution has been rejected."""

    NOT_ALLOWED = 6
    """The command is not allowed to be executed."""

    ABORTED = 7
    """The command in progress has been aborted."""
