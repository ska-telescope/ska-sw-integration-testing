# This BDD test performs TMC-Dish pairwise testing to verify long sequence of commands.
@XTP-42658 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario: TMC executes long sequence of commands successfully
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And TMC subarray is in IDLE obsState
    When I configure the subarray <subarray_id> with <receiver_band_1>
    And I issue End command to the subarray <subarray_id>
    And I reconfigure subarray <subarray_id> with <receiver_band_2>
    And I issue scan command with <scan_id> on subarray
    Then tmc subarraynode reports SCANNING obsState
    Examples:
        | subarray_id | dish_ids                     | scan_id | receiver_band_1 | receiver_band_2 |
        | 1           | SKA001,SKA036,SKA063,SKA100  |    1    |        1        |        2        |  