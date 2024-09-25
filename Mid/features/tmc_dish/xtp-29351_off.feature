# This BDD test performs TMC-Dish pairwise testing to verify Off command flow.
@XTP-29351 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario: Shut down with TMC and DISH devices
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    When I switch off the telescope
    Then DishMaster <dish_ids> must transition to STANDBY-LP mode
    And telescope is OFF

        Examples:
        | dish_ids                           |
        | SKA001,SKA036,SKA063,SKA100        |
        