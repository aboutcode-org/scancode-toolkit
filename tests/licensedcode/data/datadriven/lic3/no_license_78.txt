DEFAULT_X11_DIR = /usr/X11R6

ifneq (,$(wildcard $(PWLIB_GUIDIR)/include/Xm/Combox.h))
all::
	echo Your Motif version is not Motif 2.0 compliant
endif

# Specify the MOTIF library path
GUILIB		:= -L$(PWLIB_GUIDIR)/lib

#
#  Motif needs libXpm in order to link, so include this if present
#
ifneq (,$(wildcard $(PWLIB_GUIDIR)/lib/libXp.*))
GUILIB		:= $(GUILIB) -lXp 
endif

# Specify the MOTIF libraries and include paths
# These must come before any X11 paths incase they override them.
GUILIB		:= $(GUILIB) -lMrm -lXm -lXt -lXmu -lX11
STDCCFLAGS	:= $(STDCCFLAGS) -I$(PWLIB_GUIDIR)/include 

# Include the X11 paths if needed.
ifneq ($(DEFAULT_X11_DIR), $(PWLIB_GUIDIR))
GUILIB		:= $(GUILIB) -L$(DEFAULT_X11_DIR)/lib
STDCCFLAGS	:= $(STDCCFLAGS) -I$(DEFAULT_X11_DIR)/include 
endif

