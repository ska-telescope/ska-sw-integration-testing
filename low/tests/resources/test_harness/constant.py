"""Define Constants"""
import json

from ska_control_model import ObsState, ResultCode
from tests.resources.test_harness.utils.enums import (
    FaultType,
    SimulatorDeviceType,
)

TIMEOUT = 80
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])
COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_IDLE = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Default exception.",
    "result": ResultCode.FAILED,
    "target_obsstates": [ObsState.CONFIGURING, ObsState.IDLE],
}

INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.CONFIGURING,
}

OBS_STATE_CONFIGURING_STUCK_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_OBSTATE,
    "error_message": "Device stuck in configuring state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.CONFIGURING,
}

INTERMEDIATE_STATE_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.RESOURCING,
}

INTERMEDIATE_CONFIGURING_STATE_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "error_message": "Device stuck in intermediate state",
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.CONFIGURING,
    }
)

OBS_STATE_RESOURCING_STUCK_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_OBSTATE,
    "error_message": "Device stuck in Resourcing state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.RESOURCING,
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

COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_IDLE = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Default exception.",
    "result": ResultCode.FAILED,
    "target_obsstates": [ObsState.RESOURCING, ObsState.IDLE],
}

COMMAND_NOT_ALLOWED_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.COMMAND_NOT_ALLOWED,
        "error_message": "Command is not allowed",
        "result": ResultCode.FAILED,
    }
)

# As per ADR-9 changes and REL-1975, changing the device names
low_centralnode = "low-tmc/central-node/0"
tmc_low_subarraynode1 = "low-tmc/subarray/01"
tmc_low_subarraynode2 = "low-tmc/subarray/02"
tmc_low_subarraynode3 = " low-tmc/subarray/03"
low_csp_master_leaf_node = "low-tmc/leaf-node-csp/0"
low_sdp_master_leaf_node = "low-tmc/leaf-node-sdp/0"
mccs_master_leaf_node = "low-tmc/leaf-node-mccs/0"
low_csp_subarray_leaf_node = "low-tmc/subarray-leaf-node-csp/01"
low_sdp_subarray_leaf_node = "low-tmc/subarray-leaf-node-sdp/01"
mccs_subarray_leaf_node = "low-tmc/subarray-leaf-node-mccs/01"
low_csp_subarray_leaf_node_2 = "low-tmc/subarray-leaf-node-csp/02"
low_sdp_subarray_leaf_node_2 = "low-tmc/subarray-leaf-node-sdp/02"
mccs_subarray_leaf_node_2 = "low-tmc/subarray-leaf-node-mccs/02"
low_sdp_subarray1 = "low-sdp/subarray/01"
low_sdp_subarray2 = "low-sdp/subarray/02"
low_sdp_subarray3 = "low-sdp/subarray/03"
low_csp_subarray1 = "low-csp/subarray/01"
low_csp_subarray2 = "low-csp/subarray/02"
low_csp_subarray3 = "low-csp/subarray/03"
low_sdp_master = "low-sdp/control/0"
low_csp_master = "low-csp/control/0"
mccs_controller = "low-mccs/control/control"
mccs_subarray1 = "low-mccs/subarray/01"
mccs_subarray2 = "low-mccs/subarray/02"
mccs_subarray3 = "low-mccs/subarray/03"
processor1 = "low-cbf/processor/0.0.0"
mccs_pasdbus_prefix = "low-mccs/pasdbus/*"
mccs_prefix = "low-mccs/*"
mccs_subarraybeam = "low-mccs/subarraybeam/01"
pst = "low-pst/beam/01"

tmc_low_subarray_prefix = "low-tmc/subarray/"
low_csp_subarray_leaf_prefix = "low-tmc/subarray-leaf-node-csp/"
low_sdp_subarray_leaf_prefix = "low-tmc/subarray-leaf-node-sdp/"
mccs_subarray_leaf_prefix = "low-tmc/subarray-leaf-node-mccs/"
low_sdp_subarray_prefix = "low-sdp/subarray/"
low_csp_subarray_prefix = "low-csp/subarray/"
mccs_subarray_prefix = "low-mccs/subarray/"


device_dict_low_for_cn = {
    "csp_master": low_csp_master,
    "tmc_subarraynode": tmc_low_subarraynode1,
    "tmc_subarraynode2": tmc_low_subarraynode2,
    "sdp_master": low_sdp_master,
    "mccs_master": mccs_controller,
    "sdp_subarray": low_sdp_subarray1,
    "sdp_subarray2": low_sdp_subarray2,
    "csp_subarray": low_csp_subarray1,
    "csp_subarray2": low_csp_subarray2,
    "sdp_subarray_leaf_node": low_sdp_subarray_leaf_node,
    "sdp_subarray_leaf_node2": low_sdp_subarray_leaf_node_2,
    "csp_subarray_leaf_node": low_csp_subarray_leaf_node,
    "csp_subarray_leaf_node2": low_csp_subarray_leaf_node_2,
    "mccs_master_leaf_node": mccs_master_leaf_node,
    "mccs_subarray_leaf_node": mccs_subarray_leaf_node,
    "mccs_subarray_leaf_node2": mccs_subarray_leaf_node_2,
    "mccs_subarray": mccs_subarray1,
    "mccs_subarray2": mccs_subarray2,
    "central_node": low_centralnode,
}

SIMULATOR_DEVICE_FQDN_DICT = {
    SimulatorDeviceType.LOW_SDP_DEVICE: [low_sdp_subarray1],
    SimulatorDeviceType.LOW_CSP_DEVICE: [low_csp_subarray1],
    SimulatorDeviceType.LOW_SDP_MASTER_DEVICE: [low_sdp_master],
    SimulatorDeviceType.LOW_CSP_MASTER_DEVICE: [low_csp_master],
    SimulatorDeviceType.MCCS_MASTER_DEVICE: [mccs_controller],
    SimulatorDeviceType.MCCS_SUBARRAY_DEVICE: [mccs_subarray1],
}

LOW_DELAYMODEL_VERSION = "https://schema.skao.int/ska-low-csp-delaymodel/1.0"

INITIAL_LOW_DELAY_JSON = {
    "interface": "https://schema.skao.int/ska-low-csp-delaymodel/1.0",
    "start_validity_sec": 0.1,
    "cadence_sec": 0.1,
    "validity_period_sec": 0.1,
    "config_id": "",
    "station_beam": 1,
    "subarray": 1,
    "station_beam_delays": [
        {
            "station_id": 1,
            "substation_id": 1,
            "xypol_coeffs_ns": [],
            "ypol_offset_ns": 0.0,
        },
        {
            "station_id": 1,
            "substation_id": 1,
            "xypol_coeffs_ns": [],
            "ypol_offset_ns": 0.0,
        },
    ],
}
