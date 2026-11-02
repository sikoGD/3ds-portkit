# Minimal libctru homebrew build. Requires devkitPro 3ds-dev and DEVKITARM.
ifeq ($(strip $(DEVKITARM)),)
$(error DEVKITARM not set. Install devkitPro 3ds-dev and source devkit-env)
endif
include $(DEVKITARM)/3ds_rules

TARGET := portkit-demo
BUILD := build
SOURCES := source
INCLUDES :=
ARCH := -march=armv6k -mtune=mpcore -mfloat-abi=hard -mtp=soft
CFLAGS := -g -Wall -Wextra -O2 -mword-relocations -ffunction-sections $(ARCH) -D__3DS__
CFLAGS += $(INCLUDE)
LDFLAGS := -specs=3dsx.specs -g $(ARCH) -Wl,-Map,$(notdir $*.map)
LIBS := -lctru -lm
LIBDIRS := $(CTRULIB)
APP_TITLE := PORTKIT_DEMO
APP_DESCRIPTION := Original libctru sample
APP_AUTHOR := PortKit contributors

ifneq ($(BUILD),$(notdir $(CURDIR)))
export OUTPUT := $(CURDIR)/$(TARGET)
export VPATH := $(foreach dir,$(SOURCES),$(CURDIR)/$(dir))
export DEPSDIR := $(CURDIR)/$(BUILD)
export OFILES := $(notdir $(patsubst %.c,%.o,$(foreach dir,$(SOURCES),$(wildcard $(dir)/*.c))))
export INCLUDE := $(foreach dir,$(INCLUDES),-I$(CURDIR)/$(dir)) -I$(CURDIR)/$(BUILD)
export LIBPATHS := $(foreach dir,$(LIBDIRS),-L$(dir)/lib)
export LIBINCLUDES := $(foreach dir,$(LIBDIRS),-I$(dir)/include)
.PHONY: all clean
all: $(BUILD)
$(BUILD):
	@mkdir -p $@
	@$(MAKE) --no-print-directory -C $(BUILD) -f $(CURDIR)/Makefile
clean:
	@rm -rf $(BUILD) $(TARGET).3dsx $(TARGET).elf
else
DEPENDS := $(OFILES:.o=.d)
-include $(DEPENDS)
$(OUTPUT).3dsx: $(OUTPUT).elf
$(OUTPUT).elf: $(OFILES)
	@echo Linking $(notdir $@)
	@$(LD) $(LDFLAGS) $(OFILES) $(LIBPATHS) $(LIBS) -o $@
%.o: $(CURDIR)/../source/%.c
	@echo Compiling $(notdir $<)
	@$(CC) $(CFLAGS) $(LIBINCLUDES) -MMD -MP -MF $(DEPSDIR)/$*.d -c $< -o $@
endif
