# This BDD test performs TMC-CSP pairwise testing to verify On command flow.
@XTP-29249 @XTP-29583 @Team_SAHYADRI @tmc_csp
Scenario: StartUp Telescope with TMC and CSP devices
    Given a Telescope consisting of TMC, CSP, simulated DISH and simulated SDP devices
    And telescope state is OFF
    When I start up the telescope
    Then the CSP must go to ON state
    And telescope state is ON
    