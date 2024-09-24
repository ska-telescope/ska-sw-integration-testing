Feature: Default

	#This BDD test performs TMC-SDP pairwise testing to verify End command flow.
	@XTP-29227 @XTP-29415 @tmc_sdp
		Scenario: End configure from SDP Subarray using TMC
		Given the Telescope is in ON state
		And a subarray <subarray_id> in the READY obsState
		When I issue End command to the subarray <subarray_id>
		Then the SDP subarray <subarray_id> transitions to IDLE obsState
		And TMC subarray <subarray_id> transitions to IDLE obsState
		Examples:
		| subarray_id   |
		|  1            |