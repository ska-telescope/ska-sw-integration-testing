Feature:  TMC Mid executes long running sequences with real csp devices
    @tmc_csp @Team_SAHYADRI @XTP-29381 @XTP-40175
    Scenario Outline: TMC Mid executes configure-scan sequence of commands successfully

    Given the telescope is in ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode <subarray_id> transitions to EMPTY ObsState

    Examples:
            |subarray_id   | scan_ids      | scan_types                                |
            |1             |["1"]          |["science_A"]                              |
            |1             |["1","2"]      |["science_A" ,"target:a"]                  |
            |1             |["1","2"]      |["science_A" ,"science_A"]                 |
            |1             |["1","1"]      |["science_A" ,"science_A"]                 |
            |1             |["1","2","3"]  |["science_A" ,"target:a","calibration:b"]  |



    @tmc_csp @Team_SAHYADRI @XTP-29381 @XTP-40176
    Scenario Outline: TMC Mid executes multiple scan with same configuration successfully

    Given the telescope is in ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And reperform scan with same configuration and new scan id <new_scan_id>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode <subarray_id> transitions to EMPTY ObsState

    Examples:
            |subarray_id  |scan_ids | scan_types    | new_scan_id|
            |1            |["1"]    |["science_A"]  |   10       |


    @tmc_csp @Team_SAHYADRI @XTP-29381 @XTP-42550
    Scenario Outline: TMC Mid executes multiple scans with different resources and configurations

    Given the telescope is in ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    And I reassign with new resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for <new_scan_types> and <new_scan_ids>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode <subarray_id> transitions to EMPTY ObsState

    Examples:

     |subarray_id  | scan_ids | scan_types     | new_scan_ids  | new_scan_types|
     |1            |  ["1"]   | ["science_A"]  | ["2"]         | ["target:a"]  |



    @ttmc_csp @Team_SAHYADRI @XTP-29381 @XTP-42551
    Scenario Outline: TMC Mid executes multiple scans with different configurations, intermittently ending configurations

    Given the telescope is in ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for <new_scan_types> and <new_scan_ids>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode <subarray_id> transitions to EMPTY ObsState

    Examples:

     |subarray_id  | scan_ids | scan_types     | new_scan_ids  | new_scan_types|
     |1            |  ["1"]   | ["science_A"]  | ["2"]         | ["target:a"] |