# This BDD test performs TMC-Dish pairwise testing to verify EndScan command flow.
@XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario: TMC mid executes EndScan command on DISH
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And TMC subarray <subarray_id> is in obsState SCANNING
    And DishMaster <dish_ids> is in dishMode OPERATE with pointingState TRACK
    When I issue the EndScan command to the TMC subarray <subarray_id>
    Then scan_id gets cleared from Dish <dish_ids>
    And the Dish <dish_ids> remains in dishMode OPERATE and pointingState TRACK  
    And TMC SubarrayNode transitions to obsState READY
    Examples:

        | subarray_id | dish_ids                       |
        | 1           | SKA001,SKA036,SKA063,SKA100    |