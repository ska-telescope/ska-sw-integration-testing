# This BDD test performs TMC-Dish pairwise testing to verify Abort command flow in obsState IDLE.
@XTP-30209 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario: TMC executes Abort command on DISH.LMC when TMC Subarray is in IDLE 
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And TMC subarray <subarray_id>  is in IDLE obsState
    When I issue the Abort command to the TMC subarray 
    Then the DishMaster <dish_ids> remains in dishmode STANDBY-FP  
    And the TMC subarray transitions to obsState ABORTED

        Examples:
        | subarray_id  | dish_ids                       |
        | 1            | SKA001,SKA036,SKA063,SKA100    |
        

