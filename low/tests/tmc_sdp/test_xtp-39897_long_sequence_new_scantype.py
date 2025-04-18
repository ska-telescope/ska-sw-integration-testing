"""
TMC Low executes multiple scans with different resources and configurations
"""

import json

import pytest
from pytest_bdd import parsers, scenario, when
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    update_eb_pb_ids,
)
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory


@pytest.mark.tmc_sdp
@scenario(
    "../../low/features/tmc_sdp/xtp_39894_tmc_sdp_long_sequence.feature",
    "TMC Low executes multiple scans with different "
    "resources and configurations",
)
def test_tmc_sdp_long_sequences():
    """
    TMC Low executes multiple-scan with different resources and configurations
    """


@when(
    parsers.parse(
        "I reassign with new resources to TMC SubarrayNode {subarray_id}"
    )
)
def reassign_resources(
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: int,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """A method to move subarray into the IDLE ObsState"""
    central_node_low.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low_multiple_scan2", command_input_factory
    )
    input_json = update_eb_pb_ids(assign_input_json)
    assign_str = json.loads(input_json)
    assign_str["sdp"]["processing_blocks"][0]["parameters"][
        "time-to-ready"
    ] = 2

    _, unique_id = central_node_low.store_resources(
        json.dumps(assign_str), "1"
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
        lookahead=10,
    )
