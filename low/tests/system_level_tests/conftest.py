from assertpy import assert_that
from pytest_bdd import given
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)

TIMEOUT = 100


@given("a Low telescope")
def given_the_sut(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
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
        central_node_low.subarray_devices["sdp_subarray"], "State"
    )
    event_tracer.subscribe_event(central_node_low.sdp_master, "State")
    event_tracer.subscribe_event(central_node_low.mccs_master, "State")
    event_tracer.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "State"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            subarray_node_low.subarray_devices["csp_subarray"]: ["State"],
            subarray_node_low.subarray_devices["sdp_subarray"]: ["State"],
            subarray_node_low.subarray_devices["mccs_subarray"]: ["State"],
            central_node_low.sdp_master: ["State"],
            central_node_low.csp_master: ["State"],
            central_node_low.mccs_master: ["State"],
        }
    )


@given("telescope is in ON state")
@given("a Telescope consisting of SDP, CSP and MCCS that is ON")
def check_state_is_on(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """A method to check CentralNode.telescopeState"""
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "CSP devices"
        "are expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.csp_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "SDP devices"
        "are expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.sdp_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "State",
        DevState.ON,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "MCCS devices"
        "are expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.mccs_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "State",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
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


def check_subarray_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    obs_state: ObsState,
):
    """Check if each subarray device is in the expected obsState."""
    subarray_devices = {
        "SDP": subarray_node_low.subarray_devices["sdp_subarray"],
        "CSP": subarray_node_low.subarray_devices["csp_subarray"],
        "MCCS": subarray_node_low.subarray_devices["mccs_subarray"],
        "TMC": subarray_node_low.subarray_node,
    }

    for name, device in subarray_devices.items():
        assert_that(event_tracer).described_as(
            f"{name} Subarray device ({device.dev_name()}) "
            f"should be in {obs_state.name} obsState."
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            device, "obsState", obs_state
        )
