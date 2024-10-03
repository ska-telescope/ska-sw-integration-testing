class CentralNodeWrapper:
    """A wrapper class to implement common tango specific details
    and standard set of commands for TMC CentralNode,
    defined by the SKA Control Model.
    """

    def __init__(
        self,
    ) -> None:
        self.central_node = None
        self.subarray_node = None
        self.csp_master_leaf_node = None
        self.sdp_master_leaf_node = None
        self.mccs_master_leaf_node = None
        self.subarray_devices = {}
        self.sdp_master = None
        self.csp_master = None
        self.mccs_master = None
        self.dish_master_list = None
        self._state = None

    def move_to_on(self) -> NotImplementedError:
        """
        Abstract method for move_to_on
        """
        raise NotImplementedError(
            "To be defined in respective derived classes"
        )

    def move_to_off(self):
        """
        Abstract method for move_to_off
        """
        raise NotImplementedError(
            "To be defined in respective derived classes"
        )

    def set_standby(self):
        """
        Abstract method for move_to_standby
        """
        raise NotImplementedError(
            "To be defined in respective derived classes"
        )

    def store_resources(self):
        """
        Abstract method for invoking AssignResources()
        """
        raise NotImplementedError(
            "To be defined in respective derived classes"
        )

    def invoke_release_resources(self):
        """
        Abstract method for invoking ReleaseResources()
        """
        raise NotImplementedError(
            "To be defined in respective derived classes"
        )
