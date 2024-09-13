import time

import tango
from tango import DeviceProxy

from tests.resources.test_harness.constant import mccs_subarraybeam

from .central_node_low import CentralNodeWrapperLow
from .subarray_node_low import SubarrayNodeWrapperLow


class TMCLow:
    def __init__(self):
        """Set all devices proxy required for TMC"""
        self.central_node = CentralNodeWrapperLow()
        self.subarray_node = SubarrayNodeWrapperLow()
        self.deleted_device = {}

    def delete_device_from_db(self, server_type):
        if server_type == "MCCS_SUBARRAYBEAM":
            self.mccs_subarraybeam = DeviceProxy(mccs_subarraybeam)
            self.mccs_subarraybeam_server = DeviceProxy(
                f"dserver/{self.mccs_subarraybeam.info().server_id}"
            )
            db = tango.Database()
            # Delete mccs subarraybeam Device
            db.delete_device(mccs_subarraybeam)
            self.deleted_device[mccs_subarraybeam] = {
                "device_name": mccs_subarraybeam,
                "server_name": "MccsSubarrayBeam/subarraybeam-01",
                "class_name": "MccsSubarrayBeam",
            }

    def add_device_to_db(
        self, device_name: str, class_name: str, server_name: str
    ):
        """Add Device to DB"""
        db = tango.Database()
        dev_info = tango.DbDevInfo()
        dev_info.name = device_name
        dev_info._class = class_name
        dev_info.server = server_name
        db.add_device(dev_info)

    def RestartServer(self, server_type: str):
        """Restart server based on provided server type"""
        if server_type == "MCCS_SUBARRAYBEAM":
            self.mccs_subarraybeam_server.RestartServer()
        time.sleep(3)

    def tear_down(self):
        """Tear down"""
        if self.deleted_device:  # Check if any devices have been deleted
            # Add deleted devices back to the database and restart servers
            for _, device_info in self.deleted_device.items():
                self.add_device_to_db(
                    device_info["device_name"],
                    device_info["class_name"],
                    device_info["server_name"],
                )
                # Restart the server after adding the device back
                if device_info["class_name"] == "MccsSubarrayBeam":
                    self.RestartServer("MCCS_SUBARRAYBEAM")

            # Clear the deleted_device dictionary after devices have
            # been added back
            self.deleted_device.clear()

        self.central_node.tear_down()

    def TelescopeOn(self):
        """Execute TelescopeOn command"""
        self.central_node.move_to_on()
