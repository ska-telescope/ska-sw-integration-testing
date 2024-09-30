Feature: Default

	#This BDD test performs TMC-SDP pairwise testing to verify Release Resources command flow.
    @XTP-29291 @XTP-29227 @tmc_sdp
    Scenario: Release resources from SDP Subarray using TMC
        Given a TMC and SDP
        And a subarray <subarray_id> in the IDLE obsState
        When I release all resources assigned to it
        Then the SDP subarray <subarray_id> must be in EMPTY obsState
        And TMC subarray <subarray_id> obsState transitions to EMPTY
        Examples:
            | subarray_id  | 
            | 1            |
