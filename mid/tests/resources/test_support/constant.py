"""This module have all required constants for ska-tmc-integration"""

from ska_control_model import ObsState
from tests.resources.test_support.common_utils.result_code import (
    FaultType,
    ResultCode,
)

centralnode = "mid-tmc/central-node/0"
tmc_subarraynode1 = "mid-tmc/subarray/01"
tmc_csp_master_leaf_node = "mid-tmc/leaf-node-csp/0"
tmc_sdp_master_leaf_node = "mid-tmc/leaf-node-sdp/0"
tmc_csp_subarray_leaf_node = "mid-tmc/subarray-leaf-node-csp/01"
tmc_sdp_subarray_leaf_node = "mid-tmc/subarray-leaf-node-sdp/01"
sdp_subarray1 = "mid-sdp/subarray/01"
csp_subarray1 = "mid-csp/subarray/01"
sdp_master = "mid-sdp/control/0"
csp_master = "mid-csp/control/0"
dish_master1 = "ska001/elt/master"
dish_master2 = "ska036/elt/master"
dish_master3 = "ska063/elt/master"
dish_master4 = "ska100/elt/master"
alarm_handler1 = "alarm/handler/01"
tmc_dish_leaf_node1 = "mid-tmc/leaf-node-dish/SKA001"
tmc_dish_leaf_node2 = "mid-tmc/leaf-node-dish/SKA036"
tmc_dish_leaf_node3 = "mid-tmc/leaf-node-dish/SKA063"
tmc_dish_leaf_node4 = "mid-tmc/leaf-node-dish/SKA100"

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
    "tmc_dish_leaf_node1": tmc_dish_leaf_node1,
    "tmc_dish_leaf_node2": tmc_dish_leaf_node2,
    "tmc_dish_leaf_node3": tmc_dish_leaf_node3,
    "tmc_dish_leaf_node4": tmc_dish_leaf_node4,
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
    "central_node": centralnode,
    "tmc_csp_subarray_leaf_node": tmc_csp_subarray_leaf_node,
    "tmc_sdp_subarray_leaf_node": tmc_sdp_subarray_leaf_node,
}

DEVICE_STATE_STANDBY_INFO = {
    sdp_subarray1: ["DISABLE", "OFF"],
    sdp_master: ["DISABLE", "STANDBY", "OFF"],
    csp_master: ["DISABLE", "STANDBY", "OFF"],
    csp_subarray1: ["DISABLE", "OFF"],
    dish_master1: ["DISABLE", "STANDBY"],
    dish_master2: ["DISABLE", "STANDBY"],
    dish_master3: ["DISABLE", "STANDBY"],
    dish_master4: ["DISABLE", "STANDBY"],
}

DEVICE_STATE_ON_INFO = {
    sdp_subarray1: ["ON"],
    sdp_master: ["ON"],
    csp_master: ["ON"],
    csp_subarray1: ["ON"],
    centralnode: ["ON"],
    dish_master1: ["STANDBY"],
    dish_master2: ["STANDBY"],
    dish_master3: ["STANDBY"],
    dish_master4: ["STANDBY"],
}

DISH_MODE_STANDBYFP_INFO = {
    dish_master1: ["STANDBY_FP"],
    dish_master2: ["STANDBY_FP"],
    dish_master3: ["STANDBY_FP"],
    dish_master4: ["STANDBY_FP"],
}

DISH_MODE_STANDBYLP_INFO = {
    dish_master1: ["STANDBY_LP"],
    dish_master2: ["STANDBY_LP"],
    dish_master3: ["STANDBY_LP"],
    dish_master4: ["STANDBY_LP"],
}

DEVICE_OBS_STATE_EMPTY_INFO = {
    sdp_subarray1: ["EMPTY"],
    tmc_subarraynode1: ["EMPTY"],
    csp_subarray1: ["EMPTY"],
}

DEVICE_OBS_STATE_READY_INFO = {
    csp_subarray1: ["READY"],
    sdp_subarray1: ["READY"],
    tmc_subarraynode1: ["READY"],
}

DEVICE_OBS_STATE_CONFIGURING_INFO = {
    sdp_subarray1: ["CONFIGURING"],
    tmc_subarraynode1: ["CONFIGURING"],
    csp_subarray1: ["CONFIGURING"],
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
    dish_master2: ["STANDBY"],
    dish_master3: ["STANDBY"],
    dish_master4: ["STANDBY"],
}

DEVICE_OBS_STATE_ABORT_INFO = {
    sdp_subarray1: ["ABORTED"],
    tmc_subarraynode1: ["ABORTED"],
    csp_subarray1: ["ABORTED"],
}


DEVICE_OBS_STATE_ABORT_IN_EMPTY = {
    sdp_subarray1: ["ABORTED"],
    tmc_subarraynode1: ["ABORTED"],
}

DEVICE_OBS_STATE_ABORT_IN_EMPTY_SDP = {
    csp_subarray1: ["ABORTED"],
    tmc_subarraynode1: ["ABORTED"],
}

DEVICE_OBS_STATE_ABORT_IN_EMPTY_CSP = {
    sdp_subarray1: ["ABORTED"],
    tmc_subarraynode1: ["ABORTED"],
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

INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.CONFIGURING,
}

COMMAND_NOT_ALLOWED_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.COMMAND_NOT_ALLOWED,
    "error_message": "Exception to test exception propagation",
    "result": ResultCode.FAILED,
}
