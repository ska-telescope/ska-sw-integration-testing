Feature: Configure the subarray using TMC
	@XTP-66007 @XTP-64112
	Scenario: Configure the Low telescope subarray using TMC
		Given a low telescope
		And telescope is in ON state
		And subarray <subarray_id> is in IDLE ObsState
		When I configure it for a scan
		Then the TMC, CSP, SDP, and MCCS subarrays transition to CONFIGURING obsState
    	And the TMC, CSP, SDP, and MCCS subarrays transition to READY obsState
		Examples: 
			| subarray_id |
			| 1           |    

Feature: End Configuration on subarray using TMC
	@XTP-66037 @XTP-64112
	Scenario: End the low telescope subarray using TMC
		Given a Low telescope
        And telescope is in ON state
        And subarray <subarray_id> is in READY ObsState
		When I end the configuration
    	Then the TMC, CSP, SDP and MCCS subarrays transition to IDLE obsState
		Examples: 
			| subarray_id |
			| 1           |   