Scenario: Execute Scan on the Low telescope
	Given a Low telescope
	And telescope is in ON state
	And subarray is in READY ObsState
	When I invoke scan command 
	Then the TMC, CSP, SDP, and MCCS subarrays transition to SCANNING obsState