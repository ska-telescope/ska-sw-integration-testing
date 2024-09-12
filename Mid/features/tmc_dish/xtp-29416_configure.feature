# This BDD test performs TMC-Dish pairwise testing to verify Configure command flow.
@XTP-29416 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario: Configure the telescope having TMC and Dish Subsystems
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And the TMC subarray is in IDLE obsState
    When I issue the Configure command to the TMC subarray <subarray_id>
    Then the DishMaster <dish_ids> transitions to dishMode OPERATE and pointingState TRACK
    And TMC subarray <subarray_id> obsState transitions to READY obsState

        Examples:
        | subarray_id  | dish_ids                           |
        | 1            | SKA001,SKA036,SKA063,SKA100        |
        