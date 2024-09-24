Feature: Default

	#This BDD test performs TMC-SDP pairwise testing to verify Assign Resources command flow.
    @XTP-29292 @XTP-29227 @tmc_sdp
    Scenario: Assign resources to SDP subarray using TMC
        Given the Telescope is in ON state
        And the subarray <subarray_id> obsState is EMPTY
        When I assign resources with the <receptors> to the subarray <subarray_id>
        Then the SDP subarray <subarray_id> must be in IDLE obsState
        And  the TMC subarray <subarray_id> obsState is transitioned to IDLE
        And the correct resources <receptors> are assigned to the SDP subarray and the TMC subarray          
        Examples: 
            | subarray_id | receptors             |
            | 1          | "C10", "C136", "C1", "C217", "C13", "C42"|

