CAR_OCI_REGISTRY_HOST:=artefact.skao.int
PROJECT = ska-sw-integration-testing
TANGO_HOST ?= tango-databaseds:10000 ## TANGO_HOST connection to the Tango DSI
TANGO_HOST_NAME ?= tango-databaseds
TELESCOPE ?= SKA-low
KUBE_NAMESPACE ?= ska-tmc-integration
KUBE_NAMESPACE_SDP ?= ska-tmc-integration-sdp
K8S_TIMEOUT ?= 800s
CI_PROJECT_PATH_SLUG ?= ska-sw-integration-testing
CI_ENVIRONMENT_SLUG ?= ska-sw-integration-testing
CSP_SIMULATION_ENABLED ?= true
SDP_SIMULATION_ENABLED ?= true
MCCS_SIMULATION_ENABLED ?= true
SDP_PROCCONTROL_REPLICAS ?= 1

ifeq ($(TELESCOPE), SKA-low)
    include Makefile-low.mk
else ifeq ($(TELESCOPE), SKA-mid)
    include Makefile-mid.mk
else
    $(error Invalid Ska environment variable. Please set TELESCOPE to 'SKA-low' or 'SKA-mid')
endif
