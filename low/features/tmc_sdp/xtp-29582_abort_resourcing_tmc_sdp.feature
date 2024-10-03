Feature: Default

        #This BDD test performs TMC-SDP pairwise testing to verify Abort command flow.
        @XTP-29582 @XTP-29227 @tmc_sdp
        Scenario: Abort invocation using TMC
                Given TMC and SDP subarray are busy assigning resources
                When I command it to Abort
                Then the SDP subarray should go into an aborted obsstate
                And the TMC subarray obsState transitions to ABORTED
        