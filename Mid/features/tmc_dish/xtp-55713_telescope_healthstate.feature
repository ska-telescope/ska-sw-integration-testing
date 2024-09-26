# This BDD test performs TMC-Dish pairwise testing to verify CentralNode TelescopeHealthState
@XTP-55713 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario Outline: Verify CentralNode TelescopeHealthState
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    When the <device> health state changes to <health_state>
    Then the telescope health state is <telescope_health_state>
    Examples:
    | device          | health_state | telescope_health_state |dish_ids                           |
    | dish manager    | UNKNOWN      | UNKNOWN                |SKA001,SKA036,SKA063,SKA100        |