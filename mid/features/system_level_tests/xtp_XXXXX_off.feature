
Scenario: Switch off the mid telescope
    Given a mid telescope
    And a Telescope consisting of SDP, CSP and DISH that is ON
    When I invoke the OFF command on the telescope
    Then the SDP and CSP go to OFF state
    And DishMaster must transition to STANDBY-LP mode