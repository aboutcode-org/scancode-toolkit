### Macros

read_filelist = $(shell grep -v '^\#' $(1))
srcs_to_objs = $(addprefix $(TOOLCHAIN)/, $(1:.cpp=.o))


### Definitions

ekioh_release_name = ekioh_src_motorola_20100720_r4525
ekioh_archive = ../$(ekioh_release_name).zip
opensource_filelist := ../opensource_files.txt
opensource_files := $(call read_filelist, $(opensource_filelist))
webkit_suffix = _webkit525-kreatvgfx
webkit_work_dir = $(SRC_DIR)/3rdParty/webkit/work
extra_dependencies = $(opensource_filelist) ../common_defs.mk ../common_flags.mk
