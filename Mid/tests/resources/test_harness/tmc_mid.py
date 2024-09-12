"""TMC Class which contain method specific to TMC
"""
import time

from tango import DeviceProxy

from tests.resources.test_harness.constant import tmc_csp_master_leaf_node

from .central_node_mid import CentralNodeWrapperMid


class TMCMid:
    def __init__(self):
        """Set all devices proxy required for TMC"""
        self.central_node = CentralNodeWrapperMid()
        self.csp_master_leaf_node = DeviceProxy(tmc_csp_master_leaf_node)
        self.csp_master_ln_server = DeviceProxy(
            f"dserver/{self.csp_master_leaf_node.info().server_id}"
        )
        self.central_node_server = DeviceProxy(
            f"dserver/{self.central_node.central_node.info().server_id}"
        )
        self.dish_leaf_node_server = ""

    @property
    def IsDishVccConfigSet(self):
        """ """
        return self.central_node.IsDishVccConfigSet

    @property
    def DishVccValidationStatus(self):
        """Current dish vcc validation status of central node"""
        return self.central_node.DishVccValidationStatus

    @property
    def dish_leaf_node_list(self):
        """Return Dish Leaf Node List"""
        return self.central_node.dish_leaf_node_list

    def RestartServer(self, server_type: str):
        """Restart server based on provided server type"""
        if server_type == "CSP_MLN":
            self.csp_master_ln_server.RestartServer()
        elif server_type == "CENTRAL_NODE":
            self.central_node_server.RestartServer()
        elif server_type.startswith("DISHLN"):
            index = int(server_type.split("_")[-1])
            dish_leaf_node_server_id = (
                self.central_node.dish_leaf_node_list[index].info().server_id
            )
            self.dish_leaf_node_server = DeviceProxy(
                f"dserver/{dish_leaf_node_server_id}"
            )
            self.dish_leaf_node_server.RestartServer()
            # Give some time to other device restart
            # to keep the kube-system stable
            time.sleep(3)

    def load_dish_vcc_configuration(self, dish_vcc_config):
        """Load Dish Vcc config on TMC"""
        return self.central_node.load_dish_vcc_configuration(dish_vcc_config)

    def tear_down(self):
        """tear down"""
        self.central_node.tear_down()

    def TelescopeOn(self):
        """Execute TelescopeOn command"""
        self.central_node.move_to_on()
