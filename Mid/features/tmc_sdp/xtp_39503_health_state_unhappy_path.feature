# This BDD test performs TMC-SDP pairwise testing to verify healthState behaviour
@XTP-39503 @XTP-29381 @Team_SAHYADRI @tmc_sdp_unhappy
Scenario Outline: Verify TMC TelescopeHealthState transition based on SDP Controller HealthState
    Given a Telescope consisting of TMC, SDP, simulated CSP and simulated Dish 
    When The <devices> health state changes to <health_state> 
    Then the telescope health state is <telescope_health_state>
    Examples:
    | devices                       | health_state               | telescope_health_state |
    | sdp controller                | DEGRADED                   |   DEGRADED             |
    | dish master1,sdp controller   | OK,DEGRADED                |   DEGRADED             |
    | csp master,sdp controller     | OK,DEGRADED                |   DEGRADED             |
    | dish master1,sdp controller   | DEGRADED,DEGRADED          |   DEGRADED             |
    | csp master,sdp controller     | DEGRADED,DEGRADED          |   DEGRADED             |