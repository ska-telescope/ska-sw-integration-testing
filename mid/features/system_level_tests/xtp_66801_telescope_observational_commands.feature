Feature: This feature tests AssignResources, ReleaseResources, Scan and EndScan for the Mid Subarray
    This feature tests the Observation State functionalities for the Mid subarray in 
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
	
	@XTP-68817 @XTP-66801 @TEAM_SAHYADRI
	Scenario: Configure a Mid telescope subarray for a scan using TMC
		Given a Mid telescope
		And a Telescope consisting of SDP, CSP and DISH that is ON
		And subarray is in the IDLE obsState
		When I issue the Configure command to subarray
		Then the TMC, CSP and SDP subarrays transition to CONFIGURING obsState
		And the TMC, CSP and SDP subarrays transition to READY obsState
		And the DishMaster transitions to dishMode OPERATE and pointingState TRACK
		And the TMC receives LongRunningCommandResult event OK from subsystems CSP,SDP and DISH
        

	@XTP-68818 @XTP-66801 @TEAM_SAHYADRI
	Scenario: End command on Mid telescope
		Given a Mid telescope
		And a Telescope consisting of SDP, CSP and DISH that is ON
		And subarray is in READY ObsState
		When I issue the End command to subarray
		Then the TMC, CSP and SDP subarrays transition to IDLE obsState
		And the DishMaster transitions to pointingState READY
		And the TMC receives LongRunningCommandResult event OK from subsystems CSP,SDP and DISH
		

	@XTP-68819 @XTP-66801 @TEAM_SAHYADRI
	Scenario: Execute Scan on the Mid telescope
		Given a Mid telescope
		And a Telescope consisting of SDP, CSP and DISH that is ON
		And subarray is in the READY obsState
		And the DishMaster is in dishMode OPERATE and pointingState TRACK
		When I issue the Scan command to subarray
		Then the TMC, CSP and SDP subarrays transition to SCANNING obsState
		And the TMC receives LongRunningCommandResult event OK from subsystems CSP,SDP and DISH

	@XTP-68822 @XTP-66801 @TEAM_SAHYADRI
	Scenario: Executes EndScan command on Mid telescope
		Given a Mid telescope
		And a Telescope consisting of SDP, CSP and DISH that is ON
		And subarray is in Scanning ObsState
		When I issue the EndScan command to the subarray
		Then the TMC, CSP and SDP subarrays transition to ObsState READY
		And the DishMaster transitions to pointingState TRACK
		And the TMC receives LongRunningCommandResult event OK from subsystems CSP,SDP and DISH