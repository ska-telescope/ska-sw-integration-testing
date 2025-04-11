import json

import pytest
from assertpy import assert_that
from pytest_bdd import given
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)
from tests.system_level_tests.utils import (
    check_subarray_obsstate,
    set_subarray_to_idle,
)

TIMEOUT = 100
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])


@given("a Low telescope")
def given_the_sut(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_node_2_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
) -> None:
    """
    Given a TMC

    Args:
        central_node_low: fixture for a TMC CentralNode under test
        subarray_node_low: fixture for a TMC SubarrayNode under test
        event_tracer: fixture for EventTracer class
    """

    assert central_node_low.central_node.ping() > 0
    assert central_node_low.sdp_master.ping() > 0
    assert subarray_node_low.subarray_devices["sdp_subarray"].ping() > 0
    event_tracer.subscribe_event(central_node_low.csp_master, "State")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "State"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "State"
    )
    event_tracer.subscribe_event(central_node_low.sdp_master, "State")
    event_tracer.subscribe_event(central_node_low.mccs_master, "State")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["mccs_subarray"], "State"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "scanID"
    )

    event_tracer.subscribe_event(
        subarray_node_2_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_2_low.subarray_devices["csp_subarray"], "State"
    )
    event_tracer.subscribe_event(
        subarray_node_2_low.subarray_devices["sdp_subarray"], "State"
    )
    event_tracer.subscribe_event(
        subarray_node_2_low.subarray_devices["mccs_subarray"], "State"
    )
    event_tracer.subscribe_event(
        subarray_node_2_low.subarray_devices["sdp_subarray"], "scanID"
    )

    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            subarray_node_low.subarray_node: ["longRunningCommandResult"],
            subarray_node_low.subarray_devices["csp_subarray"]: ["State"],
            subarray_node_low.subarray_devices["sdp_subarray"]: [
                "State",
                "scanID",
            ],
            subarray_node_low.subarray_devices["mccs_subarray"]: ["State"],
            subarray_node_2_low.subarray_node: ["longRunningCommandResult"],
            subarray_node_2_low.subarray_devices["csp_subarray"]: ["State"],
            subarray_node_2_low.subarray_devices["sdp_subarray"]: [
                "State",
                "scanID",
            ],
            subarray_node_2_low.subarray_devices["mccs_subarray"]: ["State"],
            central_node_low.sdp_master: ["State"],
            central_node_low.csp_master: ["State"],
            central_node_low.mccs_master: ["State"],
        }
    )


def check_devices_state_on(
    event_tracer: TangoEventTracer,
    devices: dict,
    expected_state: DevState = DevState.ON,
):
    """Helper function to check if multiple devices are in the
    expected state."""
    for name, device in devices.items():
        assert_that(event_tracer).described_as(
            f"FAILED ASSUMPTION AFTER ON COMMAND: "
            f"{name} device ({device.dev_name()}) "
            f"is expected to be in State {expected_state.name}"
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            device, "State", expected_state
        )


@given("a Telescope consisting of SDP, CSP and MCCS that is ON")
@given("telescope is in ON state")
def check_state_is_on(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_node_2_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """A method to check CentralNode.telescopeState"""
    central_node_low.move_to_on()

    devices = {
        "CSP Master": central_node_low.csp_master,
        "CSP Subarray": subarray_node_low.subarray_devices["csp_subarray"],
        "CSP Subarray2": subarray_node_2_low.subarray_devices["csp_subarray"],
        "SDP Master": central_node_low.sdp_master,
        "SDP Subarray": subarray_node_low.subarray_devices["sdp_subarray"],
        "SDP Subarray2": subarray_node_2_low.subarray_devices["sdp_subarray"],
        "MCCS Master": central_node_low.mccs_master,
        "MCCS Subarray": subarray_node_low.subarray_devices["mccs_subarray"],
        "MCCS Subarray2": subarray_node_2_low.subarray_devices[
            "mccs_subarray"
        ],
    }

    # Check if all devices are in ON state
    check_devices_state_on(event_tracer, devices)

    # Check if the Central Node is in TelescopeState ON
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node, "telescopeState", DevState.ON
    )


def subscribe_to_obsstate_events(event_tracer, subarray_node_low):
    """Subscribe to obsState events for all relevant subarray devices."""
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")


# def check_subarray_obsstate(
#     subarray_node_low: SubarrayNodeWrapperLow,
#     event_tracer: TangoEventTracer,
#     obs_state: ObsState,
# ):
#     """Check if each subarray device is in the expected obsState."""
#     subarray_devices = {
#         "SDP": subarray_node_low.subarray_devices["sdp_subarray"],
#         "CSP": subarray_node_low.subarray_devices["csp_subarray"],
#         "MCCS": subarray_node_low.subarray_devices["mccs_subarray"],
#         "TMC": subarray_node_low.subarray_node,
#     }

#     for name, device in subarray_devices.items():
#         assert_that(event_tracer).described_as(
#             f"{name} Subarray device ({device.dev_name()}) "
#             f"should be in {obs_state.name} obsState."
#         ).within_timeout(TIMEOUT).has_change_event_occurred(
#             device, "obsState", obs_state
#         )


@given("a Telescope with 2 subarrays configured for a IDLE")
def subarrays_in_idle_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_node_2_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    # Assign resources to subarray 1
    set_subarray_to_idle(
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
        "1",
    )

    # Assign resources to Subarray 2
    set_subarray_to_idle(
        central_node_low,
        subarray_node_2_low,
        command_input_factory,
        event_tracer,
        "2",
    )


@given("a Telescope with 2 subarrays configured for a READY")
def subarrays_in_ready_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_node_2_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):

    configure_input_json_1 = prepare_json_args_for_commands(
        "configure_low_real_subarray1", command_input_factory
    )
    configure_input_json_2 = prepare_json_args_for_commands(
        "configure_low_real_subarray2", command_input_factory
    )
    _, pytest.unique_id_sa_1 = subarray_node_low.store_configuration_data(
        configure_input_json_1, "1"
    )

    _, pytest.unique_id_sa_2 = subarray_node_2_low.store_configuration_data(
        configure_input_json_2, "2"
    )
    # Verify longRunningCommandResult for the TMC Subarray Node 1
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in READY obsState'"
        "TMC Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to have longRunningCommandResult as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id_sa_1[0], COMMAND_COMPLETED),
    )
    # Verify longRunningCommandResult for the TMC Subarray Node 2
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in READY obsState'"
        "TMC Subarray Node device"
        f"({subarray_node_2_low.subarray_node.dev_name()}) "
        "is expected to have longRunningCommandResult as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(200).has_change_event_occurred(
        subarray_node_2_low.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id_sa_2[0], COMMAND_COMPLETED),
    )

    check_subarray_obsstate(
        subarray_node_low.subarray_node,
        subarray_node_low.subarray_devices,
        event_tracer,
        obs_state=ObsState.READY,
    )
    check_subarray_obsstate(
        subarray_node_2_low.subarray_node,
        subarray_node_low.subarray_devices,
        event_tracer,
        obs_state=ObsState.READY,
    )
    event_tracer.clear_events()
