# This BDD test performs TMC-SDP pairwise testing to verify On command flow.
@XTP-29230 @XTP-29381 @Team_SAHYADRI @tmc_sdp
Scenario: Start up the telescope having TMC and SDP subsystems
	Given a Telescope consisting of TMC, SDP, simulated CSP and simulated Dish
	And telescope state is STANDBY
	When I start up the telescope
	Then the SDP must go to ON state
	And telescope state is ON
	