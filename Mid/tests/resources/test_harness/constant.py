"""Define Constants
"""
import json

import numpy as np
from ska_control_model import ObsState

from tests.resources.test_harness.utils.enums import (
    FaultType,
    ResultCode,
    SimulatorDeviceType,
)

centralnode = "ska_mid/tm_central/central_node"
tmc_subarraynode1 = "ska_mid/tm_subarray_node/1"
tmc_csp_master_leaf_node = "ska_mid/tm_leaf_node/csp_master"
tmc_sdp_master_leaf_node = "ska_mid/tm_leaf_node/sdp_master"
tmc_csp_subarray_leaf_node = "ska_mid/tm_leaf_node/csp_subarray01"
tmc_sdp_subarray_leaf_node = "ska_mid/tm_leaf_node/sdp_subarray01"
tmc_dish_leaf_node1 = "ska_mid/tm_leaf_node/d0001"
tmc_dish_leaf_node2 = "ska_mid/tm_leaf_node/d0036"
tmc_dish_leaf_node3 = "ska_mid/tm_leaf_node/d0063"
tmc_dish_leaf_node4 = "ska_mid/tm_leaf_node/d0100"
sdp_subarray1 = "mid-sdp/subarray/01"
csp_subarray1 = "mid-csp/subarray/01"
sdp_master = "mid-sdp/control/0"
csp_master = "mid-csp/control/0"
dish_master1 = "ska001/elt/master"
dish_master2 = "ska036/elt/master"
dish_master3 = "ska063/elt/master"
dish_master4 = "ska100/elt/master"
sdp_queue_connector = "mid-sdp/queueconnector/01"
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])


COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_IDLE = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Default exception.",
    "result": ResultCode.FAILED,
    "target_obsstates": [ObsState.CONFIGURING, ObsState.IDLE],
}

OBS_STATE_CONFIGURING_STUCK_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_OBSTATE,
    "error_message": "Device stuck in configuring state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.CONFIGURING,
}

DEVICE_HEALTH_STATE_OK_INFO = {
    tmc_csp_subarray_leaf_node: "OK",
    centralnode: "OK",
    tmc_csp_master_leaf_node: "OK",
    tmc_sdp_master_leaf_node: "OK",
    tmc_sdp_subarray_leaf_node: "OK",
}

# TODO use this as as list when multiple subarray considered in testing
ON_OFF_DEVICE_COMMAND_DICT = {
    "sdp_subarray": sdp_subarray1,
    "csp_subarray": csp_subarray1,
    "csp_master": csp_master,
    "tmc_subarraynode": tmc_subarraynode1,
    "sdp_master": sdp_master,
    "dish_master": dish_master1,
    "central_node": centralnode,
}

DEVICE_STATE_STANDBY_INFO = {
    sdp_subarray1: ["DISABLE", "OFF"],
    sdp_master: ["DISABLE", "STANDBY", "OFF"],
    csp_master: ["DISABLE", "STANDBY", "OFF"],
    csp_subarray1: ["DISABLE", "OFF"],
    dish_master1: ["DISABLE", "STANDBY"],
}

DEVICE_STATE_ON_INFO = {
    sdp_subarray1: ["ON"],
    sdp_master: ["ON"],
    csp_master: ["ON"],
    csp_subarray1: ["ON"],
    centralnode: ["ON"],
    dish_master1: ["STANDBY"],
}

DEVICE_OBS_STATE_EMPTY_INFO = {
    sdp_subarray1: ["EMPTY"],
    tmc_subarraynode1: ["EMPTY"],
    csp_subarray1: ["EMPTY"],
}

DEVICE_OBS_STATE_READY_INFO = {
    sdp_subarray1: ["READY"],
    tmc_subarraynode1: ["READY"],
    csp_subarray1: ["READY"],
}

DEVICE_OBS_STATE_IDLE_INFO = {
    sdp_subarray1: ["IDLE"],
    tmc_subarraynode1: ["IDLE"],
    csp_subarray1: ["IDLE"],
}

DEVICE_STATE_OFF_INFO = {
    sdp_subarray1: ["OFF"],
    sdp_master: ["OFF"],
    csp_master: ["OFF"],
    csp_subarray1: ["OFF"],
    dish_master1: ["STANDBY"],
}

DEVICE_OBS_STATE_ABORT_INFO = {
    sdp_subarray1: ["ABORTED"],
    tmc_subarraynode1: ["ABORTED"],
    csp_subarray1: ["ABORTED"],
}

DEVICE_LIST_FOR_CHECK_DEVICES = [
    centralnode,
    csp_subarray1,
    sdp_subarray1,
    tmc_subarraynode1,
    tmc_csp_master_leaf_node,
    tmc_csp_subarray_leaf_node,
    tmc_sdp_master_leaf_node,
    tmc_sdp_subarray_leaf_node,
]

DEVICE_OBS_STATE_SCANNING_INFO = {
    sdp_subarray1: ["SCANNING"],
    tmc_subarraynode1: ["SCANNING"],
    csp_subarray1: ["SCANNING"],
}


INTERMEDIATE_STATE_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.RESOURCING,
}

OBS_STATE_RESOURCING_STUCK_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_OBSTATE,
    "error_message": "Device stuck in Resourcing state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.RESOURCING,
}


OBS_STATE_CONFIGURING_STUCK_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_OBSTATE,
    "error_message": "Device stuck in CONFIGURING obsState",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.CONFIGURING,
}

INTERMEDIATE_OBSSTATE_EMPTY_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.EMPTY,
}

COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Default exception.",
    "result": ResultCode.FAILED,
    "target_obsstates": [ObsState.RESOURCING, ObsState.EMPTY],
}

ERROR_PROPAGATION_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.LONG_RUNNING_EXCEPTION,
        "error_message": "Exception occurred, command failed.",
        "result": ResultCode.FAILED,
    }
)
RESET_DEFECT = json.dumps(
    {
        "enabled": False,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Default exception.",
        "result": ResultCode.FAILED,
    }
)
POINTING_OFFSETS = np.array(
    [
        [
            "SKA001",
            -4.115211938625473,
            69.9725295732531,
            -7.090356031104502,
            104.10028693155607,
            70.1182176899719,
            78.8829949012184,
            95.49061976199042,
            729.5782881970024,
            119.27311545171803,
            1065.4074085647912,
            0.9948872678443994,
            0.8441090109163307,
        ],
        [
            "SKA036",
            -4.115211938625473,
            69.10028693155607,
            -7.5782881970024,
            104.10028693155607,
            70.1182176899719,
            78.8829949012184,
            95.49061976199042,
            729.5782881970024,
            119.27311545171803,
            1065.4074085647912,
            0.9948872678443994,
            0.8441090109163307,
        ],
    ]
)

COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_IDLE = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Default exception.",
    "result": ResultCode.FAILED,
    "target_obsstates": [ObsState.RESOURCING, ObsState.IDLE],
}

COMMAND_NOT_ALLOWED_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.COMMAND_NOT_ALLOWED,
    "error_message": "Command is not allowed",
    "result": ResultCode.FAILED,
}


device_dict = {
    "csp_master": csp_master,
    "tmc_subarraynode": tmc_subarraynode1,
    "sdp_master": sdp_master,
    "dish_master1": dish_master1,
    "dish_master2": dish_master2,
    "dish_master3": dish_master3,
    "dish_master4": dish_master4,
    "dish_master_list": [
        dish_master1,
        dish_master2,
        dish_master3,
        dish_master4,
    ],
    "dish_leaf_node_list": [
        tmc_dish_leaf_node1,
        tmc_dish_leaf_node2,
        tmc_dish_leaf_node3,
        tmc_dish_leaf_node4,
    ],
    "sdp_subarray": sdp_subarray1,
    "csp_subarray": csp_subarray1,
    "sdp_subarray_leaf_node": tmc_sdp_subarray_leaf_node,
    "csp_subarray_leaf_node": tmc_csp_subarray_leaf_node,
    "csp_master_leaf_node": tmc_csp_master_leaf_node,
}

SIMULATOR_DEVICE_FQDN_DICT = {
    SimulatorDeviceType.MID_SDP_DEVICE: [sdp_subarray1],
    SimulatorDeviceType.MID_CSP_DEVICE: [csp_subarray1],
    SimulatorDeviceType.DISH_DEVICE: [
        dish_master1,
        dish_master2,
        dish_master3,
        dish_master4,
    ],
    SimulatorDeviceType.MID_SDP_MASTER_DEVICE: [sdp_master],
    SimulatorDeviceType.MID_CSP_MASTER_DEVICE: [csp_master],
}

DEFAULT_DISH_VCC_CONFIG = {
    "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",
    "tm_data_sources": [
        "car://gitlab.com/ska-telescope/ska-telmodel-data?"
        + "ska-sdp-tmlite-repository-1.0.0#tmdata"
    ],
    "tm_data_filepath": (
        "instrument/ska1_mid_psi/ska-mid-cbf-system-parameters.json"
    ),
}

DISH_001_CALIBRATION_DATA = [1.1, 1.2, 1.3]
DISH_036_CALIBRATION_DATA = [2.1, 2.2, 2.3]
