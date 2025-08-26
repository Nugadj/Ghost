# Ghost Protocol Beacon Makefile
# Compiles the C beacon for multiple platforms

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2
LDFLAGS = 

# Platform-specific settings
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    LDFLAGS += -lpthread
    TARGET = beacon_linux
endif
ifeq ($(UNAME_S),Darwin)
    LDFLAGS += -lpthread
    TARGET = beacon_macos
endif
ifeq ($(OS),Windows_NT)
    LDFLAGS += -lws2_32 -lwininet
    TARGET = beacon_windows.exe
    CFLAGS += -D_WIN32_WINNT=0x0601
endif

# Source files
SOURCES = beacon.c communication.c
OBJECTS = $(SOURCES:.c=.o)

# Default target
all: $(TARGET)

# Build target
$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

# Compile source files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Static build (for better portability)
static: LDFLAGS += -static
static: $(TARGET)

# Debug build
debug: CFLAGS += -g -DDEBUG
debug: $(TARGET)

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TARGET) beacon_linux beacon_macos beacon_windows.exe

# Install (copy to system path)
install: $(TARGET)
	cp $(TARGET) /usr/local/bin/ghost-beacon

# Cross-compile for Windows from Linux
windows:
	x86_64-w64-mingw32-gcc $(CFLAGS) -D_WIN32_WINNT=0x0601 $(SOURCES) -o beacon_windows.exe -lws2_32 -lwininet

# Cross-compile for multiple platforms
cross-compile:
	# Linux
	gcc $(CFLAGS) $(SOURCES) -o beacon_linux -lpthread
	# Windows (requires mingw-w64)
	x86_64-w64-mingw32-gcc $(CFLAGS) -D_WIN32_WINNT=0x0601 $(SOURCES) -o beacon_windows.exe -lws2_32 -lwininet

# Help
help:
	@echo "Ghost Protocol Beacon Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build beacon for current platform"
	@echo "  static     - Build statically linked beacon"
	@echo "  debug      - Build with debug symbols"
	@echo "  windows    - Cross-compile for Windows"
	@echo "  clean      - Remove build artifacts"
	@echo "  install    - Install beacon to system path"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Usage Examples:"
	@echo "  make                    # Build for current platform"
	@echo "  make static            # Build static binary"
	@echo "  make debug             # Build with debugging"
	@echo "  make cross-compile     # Build for multiple platforms"

.PHONY: all static debug clean install windows cross-compile help
