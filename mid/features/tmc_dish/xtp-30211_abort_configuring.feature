# This BDD test performs TMC-Dish pairwise testing to verify Abort command flow in obsState CONFIGURING.
@XTP-30211 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario: Abort configuring DISH.LMC using TMC
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And the TMC subarray <subarray_id> is busy configuring and DishMaster <dish_ids> is in pointingState TRACK
    When I issue the Abort command to the TMC subarray 
    Then the DishMaster <dish_ids> transitions to dishMode STANDBY-FP and pointingState READY  
    And the TMC subarray transitions to obsState ABORTED

        Examples:
        | subarray_id  | dish_ids                       |
        | 1            | SKA001,SKA036,SKA063,SKA100    |
        

