Feature: Configure the subarray using TMC
	@XTP-xxxxx
	Scenario: Configure the low telescope subarray using TMC
		Given a low telescope
        And telescope is in ON state
        And subarray <subarray_id> is in IDLE ObsState
		When I configure it for a scan
        Then the CSP, SDP and MCCS subarrays tranistions in READY obsState
		Then the subarray must be in the READY state

Feature: End Configuration on subarray using TMC
	@XTP-xxxxx
	Scenario: End the low telescope subarray using TMC
		Given a low telescope
        And telescope is in ON state
        And subarray <subarray_id> is in IDLE ObsState
		When I end the configuration
        Then the CSP, SDP and MCCS subarrays tranistions in IDLE obsState
		Then the subarray must be in the IDLE state
