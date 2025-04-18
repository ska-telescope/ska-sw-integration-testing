"""CentralNodelow"""
import json
import logging
import time
from time import sleep

from assertpy import assert_that
from ska_control_model import AdminMode, ObsState, ResultCode
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DeviceProxy, DevState
from tests.resources.test_harness.constant import (
    RESET_DEFECT,
    device_dict_low_for_cn,
    low_centralnode,
    low_csp_master,
    low_csp_master_leaf_node,
    low_csp_subarray1,
    low_csp_subarray2,
    low_csp_subarray_leaf_node,
    low_csp_subarray_leaf_node_2,
    low_sdp_master,
    low_sdp_master_leaf_node,
    low_sdp_subarray1,
    low_sdp_subarray2,
    low_sdp_subarray_leaf_node,
    low_sdp_subarray_leaf_node_2,
    mccs_controller,
    mccs_master_leaf_node,
    mccs_subarray1,
    mccs_subarray2,
    pst,
    tmc_low_subarraynode1,
    tmc_low_subarraynode2,
)
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import SIMULATED_DEVICES_DICT
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.sync_decorators import (
    sync_abort,
    sync_assign_resources,
    sync_release_resources,
    sync_restart,
    sync_set_to_off,
    sync_set_to_on,
)
from tests.resources.test_support.common_utils.common_helpers import Resource

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
TIMEOUT = 200


class CentralNodeWrapperLow(object):
    """A wrapper class to implement common tango specific details
    and standard set of commands for TMC Low CentralNode,
    defined by the SKA Control Model."""

    def __init__(self) -> None:
        self.central_node = DeviceProxy(low_centralnode)
        self.subarray_node = DeviceProxy(tmc_low_subarraynode1)
        self.subarray_node_2 = DeviceProxy(tmc_low_subarraynode2)
        self.csp_master_leaf_node = DeviceProxy(low_csp_master_leaf_node)
        self.sdp_master_leaf_node = DeviceProxy(low_sdp_master_leaf_node)
        self.mccs_master_leaf_node = DeviceProxy(mccs_master_leaf_node)

        # Add the number of subarrays available in the deployment, so that
        # they will be considered in the tear down
        self.tmc_subarrays = {
            "1": self.subarray_node,
            "2": self.subarray_node_2,
        }
        self.subarray_devices = {
            "csp_subarray": DeviceProxy(low_csp_subarray1),
            "sdp_subarray": DeviceProxy(low_sdp_subarray1),
            "mccs_subarray": DeviceProxy(mccs_subarray1),
        }
        self.subarray_2_devices = {
            "csp_subarray": DeviceProxy(low_csp_subarray2),
            "sdp_subarray": DeviceProxy(low_sdp_subarray2),
            "mccs_subarray": DeviceProxy(mccs_subarray2),
        }
        self.csp_subarray_leaf_node = DeviceProxy(low_csp_subarray_leaf_node)
        self.sdp_subarray_leaf_node = DeviceProxy(low_sdp_subarray_leaf_node)
        self.csp_subarray_leaf_node_2 = DeviceProxy(
            low_csp_subarray_leaf_node_2
        )
        self.sdp_subarray_leaf_node_2 = DeviceProxy(
            low_sdp_subarray_leaf_node_2
        )
        self.subarray_device_by_id: dict = {"1": self.subarray_devices}
        self.csp_subarray1 = DeviceProxy(low_csp_subarray1)
        self.sdp_subarray1 = DeviceProxy(low_sdp_subarray1)
        self.mccs_subarray1 = DeviceProxy(mccs_subarray1)
        self.csp_subarray2 = DeviceProxy(low_csp_subarray2)
        self.sdp_subarray2 = DeviceProxy(low_sdp_subarray2)
        self.mccs_subarray2 = DeviceProxy(mccs_subarray2)
        self.sdp_master = DeviceProxy(low_sdp_master)
        self.csp_master = DeviceProxy(low_csp_master)
        self.mccs_master = DeviceProxy(mccs_controller)
        self._state = DevState.OFF

        self.json_factory = JsonFactory()
        self.release_input = (
            self.json_factory.create_centralnode_configuration(
                "release_resources_low"
            )
        )
        self.assign_input = self.json_factory.create_centralnode_configuration(
            "assign_resources_low"
        )
        self.event_tracer = TangoEventTracer()
        self.event_recorder = EventRecorder()
        self.event_recorder.subscribe_event(
            self.central_node, "longRunningCommandResult"
        )
        self.event_recorder.subscribe_event(
            self.subarray_node, "longRunningCommandResult"
        )

        self.event_tracer.subscribe_event(
            self.central_node, "longRunningCommandResult"
        )
        self.event_tracer.subscribe_event(
            self.subarray_node, "longRunningCommandResult"
        )

        log_events(
            {
                self.central_node: ["longRunningCommandResult"],
                self.subarray_node: ["longRunningCommandResult"],
            }
        )
        if (
            SIMULATED_DEVICES_DICT["sdp_and_mccs"]
            or SIMULATED_DEVICES_DICT["all_subsystems"]
        ):
            self.pst = DeviceProxy(pst)

    def set_subarray_id(self, subarray_id):
        subarray_id = "{:02d}".format(int(subarray_id))
        self.subarray_devices = {
            "csp_subarray": DeviceProxy(f"low-csp/subarray/{subarray_id}"),
            "sdp_subarray": DeviceProxy(f"low-sdp/subarray/{subarray_id}"),
            "mccs_subarray": DeviceProxy(f"low-mccs/subarray/{subarray_id}"),
        }
        self.subarray_node = DeviceProxy(f"low-tmc/subarray/{subarray_id}")
        self.csp_subarray_leaf_node = DeviceProxy(
            f"low-tmc/subarray-leaf-node-csp/{subarray_id}"
        )
        self.sdp_subarray_leaf_node = DeviceProxy(
            f"low-tmc/subarray-leaf-node-sdp/{subarray_id}"
        )
        self.mccs_subarray_leaf_node = DeviceProxy(
            f"low-tmc/subarray-leaf-node-mccs/{subarray_id}"
        )
        self.subarray_device_by_id[subarray_id] = self.subarray_devices
        self.subarray_device_by_id[subarray_id].update(
            {
                "subarray_node": self.subarray_node,
                "csp_subarray_leaf_node": self.csp_subarray_leaf_node,
                "sdp_subarray_leaf_node": self.sdp_subarray_leaf_node,
                "mccs_subarray_leaf_node": self.mccs_subarray_leaf_node,
            }
        )

    def get_subarray_devices_by_id(self, subarray_id):
        subarray_id = "{:02d}".format(int(subarray_id))
        return self.subarray_device_by_id[subarray_id]

    @property
    def state(self) -> DevState:
        """TMC Low CentralNode operational state"""
        self._state = Resource(self.central_node).get("State")
        return self._state

    @state.setter
    def state(self, value):
        """Sets value for TMC CentralNode operational state

        Args:
            value (DevState): operational state value
        """
        self._state = value

    @property
    def telescope_health_state(self) -> HealthState:
        """Telescope health state representing overall health of telescope"""
        self._telescope_health_state = Resource(self.central_node).get(
            "telescopeHealthState"
        )
        return self._telescope_health_state

    @telescope_health_state.setter
    def telescope_health_state(self, value):
        """Telescope health state representing overall health of telescope

        Args:
            value (HealthState): telescope health state value
        """
        self._telescope_health_state = value

    @property
    def telescope_state(self) -> DevState:
        """Telescope state representing overall state of telescope"""

        self._telescope_state = Resource(self.central_node).get(
            "telescopeState"
        )
        return self._telescope_state

    @telescope_state.setter
    def telescope_state(self, value):
        """Telescope state representing overall state of telescope

        Args:
            value (DevState): telescope state value
        """
        self._telescope_state = value

    @sync_set_to_off(device_dict=device_dict_low_for_cn)
    def move_to_off(self):
        """
        A method to invoke TelescopeOff command to
        put telescope in OFF state

        """
        if SIMULATED_DEVICES_DICT["all_mocks"]:
            LOGGER.info("Invoking TelescopeOff command with all Mocks")
            _, unique_id = self.central_node.TelescopeOff()
            self.set_values_with_all_mocks(DevState.OFF)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER OFF COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )

        elif SIMULATED_DEVICES_DICT["csp_and_sdp"]:
            LOGGER.info(
                "Invoking TelescopeOff command with csp and sdp simulated"
            )
            _, unique_id = self.central_node.TelescopeOff()
            self.set_value_with_csp_sdp_mocks(DevState.OFF)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER OFF COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        elif SIMULATED_DEVICES_DICT["csp_and_mccs"]:
            LOGGER.info(
                "Invoking TelescopeOff command with csp and mccs simulated"
            )
            _, unique_id = self.central_node.TelescopeOff()
            self.set_values_with_csp_mccs_mocks(DevState.OFF)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER OFF COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        elif SIMULATED_DEVICES_DICT["sdp_and_mccs"]:
            LOGGER.info(
                "Invoking TelescopeOff command with sdp and mccs simulated"
            )
            _, unique_id = self.central_node.TelescopeOff()
            self.set_values_with_sdp_mccs_mocks(DevState.OFF)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER OFF COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        else:
            LOGGER.info(
                "Invoke TelescopeOff command with all real sub-systems"
            )
            _, unique_id = self.central_node.TelescopeOff()
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER OFF COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )

    def _clear_command_call_and_transition_data(self, clear_transition=False):
        """Clears the command call data"""
        if SIMULATED_DEVICES_DICT["all_mocks"]:
            for sim_device in [
                low_csp_subarray1,
                low_sdp_subarray1,
            ]:
                device = DeviceProxy(sim_device)
                device.ClearCommandCallInfo()
                if clear_transition:
                    device.ResetTransitions()

    def tear_down(self):
        """Handle Tear down of central Node"""
        LOGGER.info("Calling Tear down for Central node.")
        # reset HealthState.UNKNOWN for mock devices
        self._reset_health_state_for_mock_devices()
        self.reset_defects_for_devices()
        for id, subarray in self.tmc_subarrays.items():
            LOGGER.info(
                "Calling Tear down from Central node for Subarray %s, %s",
                id,
                subarray,
            )
            LOGGER.info("Subarray ObsState %s, %s", id, subarray.obsState)
            if subarray.obsState in [
                ObsState.RESOURCING,
            ]:
                LOGGER.info("Calling Abort and Restart on SubarrayNode")
                _, unique_id = self.subarray_abort(id)
                assert_that(self.event_tracer).described_as(
                    "FAILED ASSUMPTION AFTER ABORT COMMAND: "
                    "Central Node device"
                    f"({subarray.dev_name()}) "
                    "is expected have longRunningCommand as"
                    '(unique_id,(ResultCode.STARTED,"Command Started"))',
                ).within_timeout(TIMEOUT).has_change_event_occurred(
                    subarray,
                    "longRunningCommandResult",
                    (
                        unique_id[0],
                        json.dumps(
                            (int(ResultCode.STARTED), "Command Started")
                        ),
                    ),
                )

                _, unique_id = self.subarray_restart(id)
                assert_that(self.event_tracer).described_as(
                    "FAILED ASSUMPTION AFTER RESTART COMMAND: "
                    "Central Node device"
                    f"({subarray.dev_name()}) "
                    "is expected have longRunningCommand as"
                    '(unique_id,(ResultCode.OK,"Command Completed"))',
                ).within_timeout(TIMEOUT).has_change_event_occurred(
                    subarray,
                    "longRunningCommandResult",
                    (
                        unique_id[0],
                        json.dumps((int(ResultCode.OK), "Command Completed")),
                    ),
                )

            elif subarray.obsState == ObsState.ABORTED:
                _, unique_id = self.subarray_restart(id)
                assert_that(self.event_tracer).described_as(
                    "FAILED ASSUMPTION AFTER RESTART COMMAND: "
                    "Central Node device"
                    f"({subarray.dev_name()}) "
                    "is expected have longRunningCommand as"
                    '(unique_id,(ResultCode.OK,"Command Completed"))',
                ).within_timeout(TIMEOUT).has_change_event_occurred(
                    subarray,
                    "longRunningCommandResult",
                    (
                        unique_id[0],
                        json.dumps((int(ResultCode.OK), "Command Completed")),
                    ),
                )
            elif subarray.obsState == ObsState.IDLE:
                LOGGER.info("Calling Release Resource on centralnode")
                release_json = json.loads(self.release_input)
                release_json["subarray_id"] = int(id)
                LOGGER.info(
                    "release_json[subarray_id]: %s",
                    release_json["subarray_id"],
                )
                _, unique_id = self.invoke_release_resources(
                    json.dumps(release_json), id
                )
                assert_that(self.event_tracer).described_as(
                    "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
                    "Central Node device"
                    f"({self.central_node.dev_name()}) "
                    "is expected have longRunningCommand as"
                    '(unique_id,(ResultCode.OK,"Command Completed"))',
                ).within_timeout(TIMEOUT).has_change_event_occurred(
                    self.central_node,
                    "longRunningCommandResult",
                    (
                        unique_id[0],
                        json.dumps((int(ResultCode.OK), "Command Completed")),
                    ),
                )
        if SIMULATED_DEVICES_DICT["sdp_and_mccs"]:
            if self.pst.obsState == ObsState.ABORTED:
                log_events({self.pst: ["obsState"]})
                self.event_tracer.subscribe_event(self.pst, "obsState")
                self.pst.obsreset()
                assert_that(self.event_tracer).described_as(
                    "FAILED TEAR DOWN"
                    "PST device"
                    f"({self.pst.dev_name()}) "
                    f"is expected to be in IDLE obstate",
                ).within_timeout(TIMEOUT).has_change_event_occurred(
                    self.pst,
                    "obsState",
                    ObsState.IDLE,
                )
            self.set_standby()
        elif (
            SIMULATED_DEVICES_DICT["csp_and_mccs"]
            or SIMULATED_DEVICES_DICT["all_mocks"]
        ):
            self.move_to_off()
        self._clear_command_call_and_transition_data(clear_transition=True)
        self.event_recorder.clear_events()
        self.event_tracer.clear_events()
        # Adding a small sleep to allow the systems to clean up processes
        sleep(0.15)

    @sync_set_to_on(device_dict=device_dict_low_for_cn)
    def move_to_on(self):
        """
        A method to invoke TelescopeOn command to
        put telescope in ON state
        """
        LOGGER.info(
            "Starting up the Telescope %s", self.central_node.telescopeState
        )
        LOGGER.info(f"Received simulated devices: {SIMULATED_DEVICES_DICT}")
        if SIMULATED_DEVICES_DICT["all_mocks"]:
            LOGGER.info("Invoking TelescopeOn command with all Mocks")
            _, unique_id = self.central_node.TelescopeOn()
            self.set_values_with_all_mocks(DevState.ON)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER ON COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )

        elif SIMULATED_DEVICES_DICT["csp_and_sdp"]:
            LOGGER.info(
                "Invoking TelescopeOn command with csp and sdp simulated"
            )
            # Set adminMode to Online for mccs_master
            if self.mccs_master.adminMode != AdminMode.ONLINE:
                self.mccs_master.adminMode = AdminMode.ONLINE
            # Set adminMode to Online for mccs_subarray
            if self.mccs_subarray1.adminMode != AdminMode.ONLINE:
                self.mccs_subarray1.adminMode = AdminMode.ONLINE
            _, unique_id = self.central_node.TelescopeOn()
            self.set_value_with_csp_sdp_mocks(DevState.ON)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER ON COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        elif SIMULATED_DEVICES_DICT["csp_and_mccs"]:
            LOGGER.info(
                "Invoking TelescopeOn command with csp and MCCS simulated"
            )
            _, unique_id = self.central_node.TelescopeOn()

            self.set_values_with_csp_mccs_mocks(DevState.ON)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER ON COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        elif SIMULATED_DEVICES_DICT["sdp_and_mccs"]:
            LOGGER.info(
                "Invoking TelescopeOn command with sdp and mccss simulated"
            )
            # Set adminMode to Online for csp_master
            if self.csp_master.adminMode != AdminMode.ONLINE:
                self.csp_master.adminMode = AdminMode.ONLINE
            # Set adminMode to Online for csp_subarray
            if self.csp_subarray1.adminMode != AdminMode.ONLINE:
                self.csp_subarray1.adminMode = AdminMode.ONLINE
            time.sleep(3)
            self.pst.On()
            _, unique_id = self.central_node.TelescopeOn()
            self.set_values_with_sdp_mccs_mocks(DevState.ON)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER ON COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        else:
            # Set adminMode to Online for csp_master
            if self.csp_master.adminMode != AdminMode.ONLINE:
                self.csp_master.adminMode = AdminMode.ONLINE
            # Set adminMode to Online for csp_subarray
            if self.csp_subarray1.adminMode != AdminMode.ONLINE:
                self.csp_subarray1.adminMode = AdminMode.ONLINE
            time.sleep(3)
            LOGGER.info("Turning the PST device on")
            self.pst.On()
            LOGGER.info("Invoke TelescopeOn command with all real sub-systems")
            _, unique_id = self.central_node.TelescopeOn()
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER ON COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )

    def set_standby(self):
        """
        A method to invoke TelescopeStandby command to
        put telescope in STANDBY state

        """
        LOGGER.info("Putting Telescope in Standby state")
        if SIMULATED_DEVICES_DICT["all_mocks"]:
            LOGGER.info("Invoking TelescopeStandby commands with all Mocks")
            _, unique_id = self.central_node.TelescopeStandBy()
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
            self.set_values_with_all_mocks(DevState.STANDBY)

        elif SIMULATED_DEVICES_DICT["csp_and_sdp"]:
            LOGGER.info(
                "Invoking TelescopeStandby command with csp and sdp simulated"
            )
            _, unique_id = self.central_node.TelescopeStandBy()
            self.set_value_with_csp_sdp_mocks(DevState.STANDBY)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )

        elif SIMULATED_DEVICES_DICT["csp_and_mccs"]:
            LOGGER.info(
                "Invoking TelescopeStandby command with csp and mccs simulated"
            )
            _, unique_id = self.central_node.TelescopeStandBy()
            self.set_values_with_csp_mccs_mocks(DevState.STANDBY)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER STANDbY COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )

        elif SIMULATED_DEVICES_DICT["sdp_and_mccs"]:
            LOGGER.info(
                "Invoking TelescopeStandby command with sdp and mccs simulated"
            )
            _, unique_id = self.central_node.TelescopeStandBy()
            self.set_values_with_sdp_mccs_mocks(DevState.STANDBY)
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER STANDbY COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        else:
            LOGGER.info(
                "Invoke TelescopeStandby command with all real sub-systems"
            )
            _, unique_id = self.central_node.TelescopeStandBy()
            assert_that(self.event_tracer).described_as(
                "FAILED ASSUMPTION AFTER STANDbY COMMAND: "
                "Central Node device"
                f"({self.central_node.dev_name()}) "
                "is expected have longRunningCommand as"
                '(unique_id,(ResultCode.OK,"Command Completed"))',
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                self.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        sleep(0.15)

    @sync_assign_resources()
    def store_resources(self, assign_json: str, subarray_id: str):
        """Invoke Assign Resource command on subarray Node
        Args:
            assign_json (str): Assign resource input json
        """
        # This methods needs to change, with subsequent changes in the Tear
        # Down of the fixtures. Will be done as an improvement later.
        result, message = self.central_node.AssignResources(assign_json)
        LOGGER.info("Invoked AssignResources on CentralNode")
        return result, message

    @sync_release_resources()
    def invoke_release_resources(self, input_string, subarray_id: str):
        """Invoke Release Resource command on central Node
        Args:
            input_string (str): Release resource input json
        """
        result, message = self.central_node.ReleaseResources(input_string)
        return result, message

    @sync_abort()
    def subarray_abort(self, subarray_id):
        """Invoke Abort command on subarray Node"""
        result, message = self.subarray_node.Abort()
        return result, message

    @sync_restart()
    def subarray_restart(self, subarray_id):
        """Invoke Restart command on subarray Node"""
        result, message = self.subarray_node.Restart()
        return result, message

    def _reset_health_state_for_mock_devices(self):
        """Reset Mock devices"""
        if (
            SIMULATED_DEVICES_DICT["csp_and_sdp"]
            or SIMULATED_DEVICES_DICT["all_mocks"]
        ):
            for mock_device in [
                self.sdp_master,
                self.csp_master,
            ]:
                device = DeviceProxy(mock_device)
                device.SetDirectHealthState(HealthState.UNKNOWN)
        elif SIMULATED_DEVICES_DICT["csp_and_mccs"]:
            for mock_device in [
                self.csp_master,
            ]:
                device = DeviceProxy(mock_device)
                device.SetDirectHealthState(HealthState.UNKNOWN)
        elif SIMULATED_DEVICES_DICT["sdp_and_mccs"]:
            for mock_device in [
                self.sdp_master,
            ]:
                device = DeviceProxy(mock_device)
                device.SetDirectHealthState(HealthState.UNKNOWN)
        else:
            LOGGER.info("No devices to reset healthState")

    def perform_action(self, command_name: str, input_json: str = ""):
        """Execute provided command on centralnode
        Args:
            command_name (str): Name of command to execute
            input_json (str): Json send as input to execute command
        """
        if input_json:
            result, message = self.central_node.command_inout(
                command_name, input_json
            )
            LOGGER.info("unique id returned by the command call %s", message)
        else:
            result, message = self.central_node.command_inout(command_name)

        return result, message

    def set_values_with_all_mocks(self, subarray_state):
        """
        A method to set values on mock CSP, SDP and MCCS devices.
        Args:
            subarray_state: DevState - subarray state value for
                                        CSP and SDP Subarrays
        """
        device_to_on_list = [
            self.subarray_devices.get("csp_subarray"),
            self.subarray_devices.get("sdp_subarray"),
            self.subarray_devices.get("mccs_subarray"),
        ]
        for device in device_to_on_list:
            device.SetDirectState(subarray_state)

    def set_value_with_csp_sdp_mocks(self, subarray_state):
        """
        A method to set values on mock CSP and SDP devices.
        Args:
            subarray_state: DevState - subarray state value for
                                    CSP and SDP Subarrays
        """
        device_to_on_list = [
            self.subarray_devices.get("csp_subarray"),
            self.subarray_devices.get("sdp_subarray"),
        ]
        for device in device_to_on_list:
            device.SetDirectState(subarray_state)

    def set_values_with_csp_mccs_mocks(self, subarray_state):
        """
        A method to set values on mock CSP and MCCS devices.
        Args:
            subarray_state: DevState - subarray state value for
                                    CSP Subarray
        """
        device_to_on_list = [
            self.subarray_devices.get("csp_subarray"),
            self.subarray_devices.get("mccs_subarray"),
        ]
        for device in device_to_on_list:
            device.SetDirectState(subarray_state)

    def set_values_with_sdp_mccs_mocks(self, subarray_state):
        """
        A method to set values on mock SDP and MCCS devices.
        Args:
            subarray_state: DevState - subarray state value for
                                    SDP Subarray
        """
        device_to_on_list = [
            self.subarray_devices.get("sdp_subarray"),
            self.subarray_devices.get("mccs_subarray"),
        ]
        for device in device_to_on_list:
            device.SetDirectState(subarray_state)

    def reset_defects_for_devices(self):
        """Resets the defects for given devices."""
        if SIMULATED_DEVICES_DICT["all_mocks"]:
            for mock_device in [
                self.csp_subarray1,
                self.sdp_subarray1,
                self.mccs_master,
                self.mccs_subarray1,
            ]:
                mock_device.SetDefective(RESET_DEFECT)
                if mock_device != self.mccs_master:
                    mock_device.ResetDelayInfo()

    def set_serial_number_of_cbf_processor(self):
        """Sets serial number for cbf processor"""
        if SIMULATED_DEVICES_DICT["sdp_and_mccs"]:
            cbf_proc1 = DeviceProxy("low-cbf/processor/0.0.0")
            cbf_proc2 = DeviceProxy("low-cbf/processor/0.0.1")

            cbf_proc1.serialnumber = "XFL14SLO1LIF"
            cbf_proc1.subscribetoallocator("low-cbf/allocator/0")
            cbf_proc1.register()

            cbf_proc2.serialnumber = "XFL1HOOQ1Y44"
            cbf_proc2.subscribetoallocator("low-cbf/allocator/0")
            cbf_proc2.register()

    def are_sdp_components_online(self):
        start_time = time.time()
        elapsed_time = 0
        component_status: dict = json.loads(self.sdp_master.components)
        statuses: list = [
            value["status"] for _, value in component_status.items()
        ]
        status: set = set(statuses)
        while status != {"ONLINE"}:
            if elapsed_time > TIMEOUT:
                return False
            time.sleep(1)
            elapsed_time = time.time() - start_time
        return True
