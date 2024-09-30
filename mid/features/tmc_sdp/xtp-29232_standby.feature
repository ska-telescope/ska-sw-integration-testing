# This BDD test performs TMC-SDP pairwise testing to verify Standby command flow.
@XTP-29232 @XTP-29381 @Team_SAHYADRI @tmc_sdp
Scenario: Standby the telescope having TMC and SDP subsystems
	Given a Telescope consisting of TMC and SDP that is in ON State
	And  simulated CSP and Dish in ON States
	And telescope state is ON
	When I put the telescope to STANDBY
	Then the sdp controller must go to STANDBY State
	And the sdp subarray must go to OFF State
	And telescope state is STANDBY
	