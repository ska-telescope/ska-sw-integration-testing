Feature:  TMC Mid executes long running sequences with real sdp devices
    @tmc_sdp @Team_SAHYADRI @XTP-39931 @XTP-29381
    Scenario Outline: TMC Mid executes multiple scan with same configuration successfully

    Given Telescope is ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And reperform scan with same configuration and new scan id
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode <subarray_id> transitions to EMPTY ObsState

    Examples:
            |subarray_id  |scan_ids | scan_types |
            |1            |["1"]    |["science_A"]  |