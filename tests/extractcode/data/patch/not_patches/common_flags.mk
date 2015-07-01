CPPFLAGS += -DBROWSER
CPPFLAGS += -DBROWSER_STANDALONE
CPPFLAGS += -DEKIOH
CPPFLAGS += -DFONT_ENGINE_FREETYPE
#CPPFLAGS += -DMOZ_X11
CPPFLAGS += -DNDEBUG
#CPPFLAGS += -DXP_UNIX
CPPFLAGS += -D_GNU_SOURCE

CXXFLAGS += -fno-rtti

OPTIMIZATION_FLAGS += -fno-strict-aliasing

# COMMON_FLAGS contains OPTIMIZATION_FLAGS so after this point, changes to
# OPTIMIZATION_FLAGS will not have any effect. Improve SunSpider JavaScript
# benchmark result and gives around 10% faster html rendering.
COMMON_FLAGS := $(filter-out -finline-limit=% -Os -g,$(COMMON_FLAGS))
COMMON_FLAGS += -O2
