CAR_OCI_REGISTRY_HOST:=artefact.skao.int
PROJECT = ska-sw-integration-testing
TANGO_HOST ?= tango-databaseds:10000 ## TANGO_HOST connection to the Tango DSI
TANGO_HOST_NAME ?= tango-databaseds
TELESCOPE ?=  $(error Please specify TELESCOPE='SKA-mid' or TELESCOPE='SKA-low')
KUBE_NAMESPACE ?= ska-sw-integration-testing
KUBE_NAMESPACE_SDP ?= ska-sw-integration-testing-sdp
CI_PROJECT_PATH_SLUG ?= ska-sw-integration-testing
CI_ENVIRONMENT_SLUG ?= ska-sw-integration-testing
CSP_SIMULATION_ENABLED ?= true
SDP_SIMULATION_ENABLED ?= true
MCCS_SIMULATION_ENABLED ?= true
SDP_PROCCONTROL_REPLICAS ?= 1
CLUSTER_DOMAIN ?= cluster.local
HELM_RELEASE ?= test
DEPLOYMENT_TYPE = $(shell echo $(TELESCOPE) | cut -d '-' -f2)
MARK ?= $(shell echo $(TELESCOPE) | sed "s/-/_/g") ## What -m opt to pass to pytest

# K8S_TEST_IMAGE_TO_TEST ?= artefact.skao.int/ska-tango-images-tango-itango:9.3.12## docker image that will be run for testing purpose
K8S_TEST_IMAGE_TO_TEST ?= harbor.skao.int/production/ska-tango-images-pytango-builder:9.4.2 
COUNT ?= 1 ## Number of times the tests should run
SUBARRAY_COUNT ?= 1

CI_REGISTRY ?= gitlab.com

CI_PROJECT_DIR ?= .

XAUTHORITY ?= $(HOME)/.Xauthority
THIS_HOST := $(shell ip a 2> /dev/null | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' | head -n1)
DISPLAY ?= $(THIS_HOST):0

ITANGO_DOCKER_IMAGE = $(CAR_OCI_REGISTRY_HOST)/ska-tango-images-tango-itango:9.5.0

# Test runner - run to completion job in K8s
# name of the pod running the k8s_tests
K8S_TEST_RUNNER = test-runner-$(HELM_RELEASE)

CI_PROJECT_PATH_SLUG ?= ska-sw-integration-testing
CI_ENVIRONMENT_SLUG ?= ska-sw-integration-testing
CSP_SIMULATION_ENABLED ?= true
SDP_SIMULATION_ENABLED ?= true
DISH_SIMULATION_ENABLED ?= true
MCCS_SIMULATION_ENABLED ?= true
SDP_PROCCONTROL_REPLICAS ?= 1

# ----------------------------------------------------------------------------
# Exit at failure flag
#
# The following flag is used to determine whether the test run should exit at
# the first failure or continue running tests after a failure. By default, the
# test run will exit at the first failure. To continue running tests after a
# failure, set the flag to 'false'.

EXIT_AT_FAIL ?= true ## Flag for determining exit at failure.
# Set 'true' to exit at first failure. Set 'false' to continue running
# tests after failure. It defaults to 'true' if not set.
# Actually, any value other than 'false' will be treated as 'true'.

ifeq ($(EXIT_AT_FAIL), true)
ADD_ARGS += -x
endif

ifeq ($(MAKECMDGOALS),k8s-test)
ADD_ARGS +=  --true-context
MARK ?= $(shell echo $(TELESCOPE) | sed "s/-/_/g")
endif

# Instead of:
#   include Makefile-low.mk
#   include Makefile-mid.mk
# we now embed them directly in this file, under conditionals:

ifeq ($(TELESCOPE), SKA-low)

# "this is Makefile-low.mk"
PYTHON_LINT_TARGET ?= low/tests/

# run one test with FILE=acceptance/test_subarray_node.py::test_check_internal_model_according_to_the_tango_ecosystem_deployed
FILE ?= low/tests## A specific test file to pass to pytest

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with

CSP_MASTER ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/low-csp/control/0
CSP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/low-csp/subarray
SDP_MASTER ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/low-sdp/control/0
SDP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/low-sdp/subarray

PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK) $(ADDMARK)' $(ADD_ARGS) $(FILE) --count=$(COUNT)

PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src \
                             TANGO_HOST=$(TANGO_HOST) \
                             TELESCOPE=$(TELESCOPE) \
                             CLUSTER_DOMAIN=$(CLUSTER_DOMAIN) \
                             CSP_SIMULATION_ENABLED=$(CSP_SIMULATION_ENABLED) \
                             SDP_SIMULATION_ENABLED=$(SDP_SIMULATION_ENABLED) \
                             MCCS_SIMULATION_ENABLED=$(MCCS_SIMULATION_ENABLED) \
                             KUBE_NAMESPACE=$(KUBE_NAMESPACE) \
                             KUBE_NAMESPACE_SDP=$(KUBE_NAMESPACE_SDP)

K8S_TEST_TEST_COMMAND ?= $(PYTHON_VARS_BEFORE_PYTEST) $(PYTHON_RUNNER) \
                        pytest \
                        $(PYTHON_VARS_AFTER_PYTEST) ./low/tests \
                        | tee pytest.stdout # k8s-test test command to run in container

XRAY_EXECUTION_CONFIG_FILE ?= low/tests/xray-config.json


else ifeq ($(TELESCOPE), SKA-mid)


# "this is Makefile-mid.mk"
DISH_NAMESPACE_1 ?= dish-lmc-1
DISH_NAMESPACE_2 ?= dish-lmc-2
DISH_NAMESPACE_3 ?= dish-lmc-3
DISH_NAMESPACE_4 ?= dish-lmc-4

PYTHON_LINT_TARGET ?= mid/tests/

# run one test with FILE=acceptance/test_subarray_node.py::test_check_internal_model_according_to_the_tango_ecosystem_deployed
FILE ?= mid/tests## A specific test file to pass to pytest

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with

DISH_TANGO_HOST ?= tango-databaseds
COUNT ?= 1 ## Number of times the tests should run
SUBARRAY_COUNT ?= 1
DISH_NAME_1 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_1).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA001
DISH_NAME_36 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_2).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA036
DISH_NAME_63 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_3).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA063
DISH_NAME_100 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_4).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA100
CSP_MASTER ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-csp/control/0
CSP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-csp/subarray
SDP_MASTER ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-sdp/control/0
SDP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-sdp/subarray

PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK) $(ADDMARK)' $(ADD_ARGS) $(FILE) --count=$(COUNT)

PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src \
                             TANGO_HOST=$(TANGO_HOST) \
                             TELESCOPE=$(TELESCOPE) \
                             CLUSTER_DOMAIN=$(CLUSTER_DOMAIN) \
                             CSP_SIMULATION_ENABLED=$(CSP_SIMULATION_ENABLED) \
                             SDP_SIMULATION_ENABLED=$(SDP_SIMULATION_ENABLED) \
                             DISH_SIMULATION_ENABLED=$(DISH_SIMULATION_ENABLED) \
                             DISH_NAMESPACE_1=$(DISH_NAMESPACE_1) \
                             DISH_NAMESPACE_2=$(DISH_NAMESPACE_2) \
                             DISH_NAMESPACE_3=$(DISH_NAMESPACE_3) \
                             DISH_NAMESPACE_4=$(DISH_NAMESPACE_4) \
                             DISH_NAME_1=$(DISH_NAME_1) \
                             DISH_NAME_36=$(DISH_NAME_36) \
                             DISH_NAME_63=$(DISH_NAME_63) \
                             DISH_NAME_100=$(DISH_NAME_100) \
                             KUBE_NAMESPACE=$(KUBE_NAMESPACE) \
                             KUBE_NAMESPACE_SDP=$(KUBE_NAMESPACE_SDP)

K8S_TEST_TEST_COMMAND ?= $(PYTHON_VARS_BEFORE_PYTEST) $(PYTHON_RUNNER) \
                        pytest \
                        $(PYTHON_VARS_AFTER_PYTEST) ./mid/tests \
                        | tee pytest.stdout # k8s-test test command to run in container

XRAY_EXECUTION_CONFIG_FILE ?= mid/tests/xray-config.json


else
    $(error Invalid Ska environment variable. Please set TELESCOPE to 'SKA-low' or 'SKA-mid')
endif



-include .make/base.mk
-include .make/k8s.mk
-include .make/helm.mk
-include .make/python.mk
-include .make/oci.mk
-include .make/xray.mk
-include PrivateRules.mak

CONFIG = $(shell echo $(TELESCOPE) | grep -oP '(?<=-)\S+')
k8s_test_folder = $(CONFIG)/tests
k8s_test_src_dir = $(CONFIG)/

test-requirements:
	@poetry export --without-hashes --with dev --format requirements.txt --output $(CONFIG)/tests/requirements.txt

k8s-pre-test: test-requirements

# ----------------------------------------------------------------------------
# Trick to select a subset of the tests to run by their python name
# Very useful when debugging a single test
#
# Example:
# make k8s-test MARK=tmc_csp PYTHON_TEST_NAME="abort"
# # Expected result: among all the tests with "tmc_csp" as a marker,
# #  			  only the ones with "abort" in their name will be run.

PYTHON_TEST_NAME ?= ## -k parameter for pytest

ifneq ($(PYTHON_TEST_NAME),)
	PYTHON_VARS_AFTER_PYTEST := $(PYTHON_VARS_AFTER_PYTEST) -k '$(PYTHON_TEST_NAME)'
endif

# ----------------------------------------------------------------------------
# test results files
# (The following variables are used to generate the various test results files
# i.e., cucumber.json, report.json, and report.html)
#
# report.html is used to generate the BDD test report by the pytest-bdd-report
# plugin. The plugin generates a BDD test report in HTML format, that will
# then be published in the artifacts and that will be linked in the
# Jira ticket of the test execution.

# target file names for the cucumber-related test results json files
CUCUMBER_JSON_RESULT_FILE ?= build/cucumber.json
REPORT_JSON_RESULT_FILE ?= build/report.json
XRAY_TEST_RESULT_FILE ?= build/cucumber.json

# target file name for the BDD test report in HTML format
# Leave or set to empty to disable the HTML BDD test report generation
HTML_REPORT_TARGET_FILE ?= build/report.html

# ----------------------------------------------------------------------------
# Add all the flags needed to generate the test results files

# Add BDD report output
PYTHON_VARS_AFTER_PYTEST := $(PYTHON_VARS_AFTER_PYTEST) \
	--cucumberjson="$(CUCUMBER_JSON_RESULT_FILE)" \
	--json-report \
	--json-report-file="$(REPORT_JSON_RESULT_FILE)"

# Add BDD HTML test report (if enabled)
ifneq ($(HTML_REPORT_TARGET_FILE),)
	PYTHON_VARS_AFTER_PYTEST := $(PYTHON_VARS_AFTER_PYTEST) \
		--bdd-report="$(HTML_REPORT_TARGET_FILE)"
endif

# ----------------------------------------------------------------------------
# Publish the BDD HTML test report to the just published
# Jira test execution issue

PUBLISH_HTML_REPORT_TO_JIRA_SCRIPT ?= helper_scripts/publish_test_report.py
## The Python script that will publish the BDD HTML test report to the Jira test execution issue
# (Set to empty to disable the publishing of the BDD HTML test report to the Jira test execution issue)

# after the test run and the Test Execution Jira ticket is created,
# if the HTML report is enabled and
# the script to publish the HTML report to Jira is available,
# then publish a link to the HTML report to Jira
xray-post-publish:
	if [ -f "$(HTML_REPORT_TARGET_FILE)" ] && [ -f "$(PUBLISH_HTML_REPORT_TO_JIRA_SCRIPT)" ]; then \
		echo "Publishing the BDD HTML test report to the Jira test execution issue"; \
		python3 $(PUBLISH_HTML_REPORT_TO_JIRA_SCRIPT); \
	fi
