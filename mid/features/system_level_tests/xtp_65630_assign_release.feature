Feature: test Assign and Release Resources for the Mid Subarray
    This feature tests the functionality of assigning and releasing resources for the Mid subarray in 
    the telescope system. The scenarios ensure that the subarrays transition correctly between their 
    operational states

	@XTP-65630 @XTP-66801 @TEAM_SAHYADRI
	Scenario: Assign resources to Mid subarray
		Given a Mid telescope
		And a Telescope consisting of SDP, CSP and DISH that is ON
		And subarray is in EMPTY ObsState
		When I assign resources to the subarray
		Then the TMC, CSP and SDP subarrays transition to RESOURCING obsState
		And the TMC, CSP and SDP subarrays transition to IDLE obsState
		And the TMC receives LongRunningCommandResult event OK from subsystems CSP and SDP
		And the requested resources are assigned to subarray
		
	@XTP-67033 @XTP-66801 @TEAM_SAHYADRI
	Scenario: Release resources from Mid subarray
		Given a Mid telescope
		And a Telescope consisting of SDP, CSP and DISH that is ON
		And subarray is in the IDLE obsState
		When I release all resources assigned to it
		Then the TMC, CSP and SDP subarrays transition to RESOURCING obsState
		And the TMC, CSP and SDP subarrays transition to EMPTY obsState
		And the TMC receives LongRunningCommandResult event OK from subsystems CSP and SDP
