TELESCOPE ?= SKA-low
ifeq ($(TELESCOPE), SKA-low)
    include Makefile-low.mk
else ifeq ($(TELESCOPE), SKA-mid)
    include Makefile-mid.mk
else
    $(error Invalid Ska environment variable. Please set Ska to 'low' or 'mid')
endif
