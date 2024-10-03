# This BDD test performs TMC-Dish pairwise testing to verify On command flow.
@XTP-29354 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario: Start up Telescope with TMC and DISH devices
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    When I start up the telescope
    Then DishMaster <dish_ids> must transition to STANDBY-FP mode
    And telescope state is ON

        Examples:
        | dish_ids                           |
        | SKA001,SKA036,SKA063,SKA100        |
        