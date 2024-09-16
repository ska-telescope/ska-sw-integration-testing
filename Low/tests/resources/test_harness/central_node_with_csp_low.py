import logging

from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState
from tango import DeviceProxy, DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import device_dict_low, processor1
from tests.resources.test_harness.utils.wait_helpers import Waiter

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class CentralNodeCspWrapperLow(CentralNodeWrapperLow):
    """A wrapper class to implement common tango specific details
    and standard set of commands for TMC Low CentralNode with real csp device,
    defined by the SKA Control Model."""

    def __init__(self) -> None:
        super().__init__()
        self.processor1 = DeviceProxy(processor1)
        device_dict_low["cbf_subarray1"] = "low-cbf/subarray/01"
        device_dict_low["cbf_controller"] = "low-cbf/control/0"
        self.wait = Waiter(**device_dict_low)

    def move_to_on(self):
        """
        A method to invoke TelescopeOn command to
        put telescope in ON state
        """
        self.pst.On()
        self.central_node.TelescopeOn()
        device_to_on_list = [
            self.subarray_devices.get("sdp_subarray"),
            self.subarray_devices.get("mccs_subarray"),
        ]
        for device_proxy in device_to_on_list:
            device_proxy.SetDirectState(DevState.ON)
        self.wait.set_wait_for_telescope_on()
        self.wait.wait(300)

    def _reset_health_state_for_mock_devices(self):
        """Reset Mock devices"""
        for mock_device in [self.sdp_master, self.mccs_master]:
            device = DeviceProxy(mock_device)
            device.SetDirectHealthState(HealthState.UNKNOWN)

    def tear_down(self):
        """Handle Tear down of central Node"""
        # reset HealthState.UNKNOWN for mock devices
        LOGGER.info("Calling Tear down for central node.")
        self._reset_health_state_for_mock_devices()
        if self.subarray_node.obsState == ObsState.IDLE:
            LOGGER.info("Calling ReleaseResources on CentralNode")
            self.invoke_release_resources(self.release_input)
        elif self.subarray_node.obsState == ObsState.RESOURCING:
            LOGGER.info("Calling Abort and Restart on SubarrayNode")
            self.pst.obsreset()
            self.subarray_abort()
            self.subarray_restart()
        elif self.subarray_node.obsState == ObsState.ABORTED:
            self.subarray_restart()
        self.move_to_off()

    def move_to_off(self):
        """
        A method to invoke TelescopeOff command to
        put telescope in OFF state

        """
        self.central_node.TelescopeOff()
        device_to_off_list = [
            self.subarray_devices.get("sdp_subarray"),
            self.subarray_devices.get("mccs_subarray"),
        ]
        for device in device_to_off_list:
            device_proxy = DeviceProxy(device)
            device_proxy.SetDirectState(DevState.OFF)

    def set_serial_number_of_cbf_processor(self):
        """Sets serial number for cbf processor"""
        cbf_proc1 = DeviceProxy("low-cbf/processor/0.0.0")
        cbf_proc2 = DeviceProxy("low-cbf/processor/0.0.1")

        cbf_proc1.serialnumber = "XFL14SLO1LIF"
        cbf_proc1.subscribetoallocator("low-cbf/allocator/0")
        cbf_proc1.register()

        cbf_proc2.serialnumber = "XFL1HOOQ1Y44"
        cbf_proc2.subscribetoallocator("low-cbf/allocator/0")
        cbf_proc2.register()
