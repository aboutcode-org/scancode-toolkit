#
# Copyright (c) 2002-2005 Sam Leffler, Errno Consulting
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer,
#    without modification.
# 2. Redistributions in binary form must reproduce at minimum a disclaimer
#    similar to the "NO WARRANTY" disclaimer below ("Disclaimer") and any
#    redistribution must be conditioned upon including a substantially
#    similar Disclaimer requirement for further binary redistribution.
# 3. Neither the names of the above-listed copyright holders nor the names
#    of any contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# Alternatively, this software may be distributed under the terms of the
# GNU General Public License ("GPL") version 2 as published by the Free
# Software Foundation.
#
# NO WARRANTY
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF NONINFRINGEMENT, MERCHANTIBILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGES.
#
# $Id: //depot/sw/linuxsrc/src/802_11/madwifi/madwifi/ath/Makefile#12 $
#

#
# Makefile for the Atheros WLAN driver.
#

ifeq ($(obj),)
obj=	.
endif

TOP = $(obj)/..

ifeq ($(strip $(BUS)),AHB)
BUSNAME=ahb
COPTS+= -DATH_AHB
else
BUSNAME=pci
COPTS+= -DATH_PCI
endif

include $(TOP)/Makefile.inc

obj-m		+= ath_$(BUSNAME).o
ath_$(BUSNAME)-objs	:= if_ath.o if_ath_$(BUSNAME).o

INCS += -I$(TOP) -I$(ATH_HAL) -I$(HAL) -I$(WLAN)

EXTRA_CFLAGS+= $(INCS) $(COPTS) -DOPT_AH_H=\"$(HAL)/public/$(TARGET).opt_ah.h\"

-include $(TOPDIR)/Rules.make

all:
	$(MAKE) -C $(KERNELPATH) SUBDIRS=$(shell pwd) modules

install:
	test -d $(DESTDIR)/$(KMODPATH) || mkdir -p $(DESTDIR)/$(KMODPATH)
	install ath_$(BUSNAME).$(KMODSUF) $(DESTDIR)/$(KMODPATH)

clean:
	rm -f *~ *.o *.ko *.mod.c .*.cmd
	rm -f .depend .version .*.o.flags .*.o.d
	rm -rf .tmp_versions

ath_$(BUSNAME).o: $(ath_$(BUSNAME)-objs)
	$(LD) $(LDOPTS) -o ath_$(BUSNAME).$(KMODSUF) -r $(ath_$(BUSNAME)-objs)
