# This BDD test performs TMC-Dish pairwise testing to verify Scan command flow.
@XTP-30385 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario: TMC executes Scan command on DISH
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And TMC subarray <subarray_id> is in READY obsState 
    And Dish <dish_ids> is in dishMode OPERATE with pointingState TRACK
    When I issue the scan command to the TMC subarray <subarray_id>
    Then <scan_id> assigned to Dish <dish_ids>
    And the Dish <dish_ids> remains in dishMode OPERATE and pointingState TRACK  
    And TMC SubarrayNode transitions to obsState SCANNING
    And TMC SubarrayNode transitions to obsState READY once the scan duration is elapsed
    Examples:

        | subarray_id | dish_ids                       | scan_id |
        | 1           | SKA001,SKA036,SKA063,SKA100    | 1       |
        