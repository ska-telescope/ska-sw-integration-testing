@XTP-42581 @XTP-29778 @Team_SAHYADRI @tmc_dish
Scenario Outline: Testing of successive configure functionality with same receiver_band
    Given a Telescope consisting of TMC, DISH <dish_ids>, simulated CSP and simulated SDP
    And the Telescope is in ON state
    And the TMC subarray is in IDLE obsState
    And the command configure is issued to the TMC subarray with <receiver_band>
    And the subarray transitions to obsState READY
    When the next successive configure command is issued to the TMC subarray with <receiver_band>
    Then the dish rejects the command with message receiver band is already band B <receiver_band>
    And TMC subarray remains in obsState READY

        Examples:
        | receiver_band |       dish_ids                | 
        |       1       |   SKA001,SKA036,SKA063,SKA100 |