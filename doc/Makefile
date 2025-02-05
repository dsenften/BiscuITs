# Define the target PDF file
TARGET = index.pdf

# Define the AsciiDoc source file
SOURCE = index.adoc

# Define the PDF theme file
THEME = themes/pdf-theme.yml

# Define the local Git version information file
GIT_INFO_FILE = ../.git/gitHeadInfo.gin

# Define a temporary file to store the local Git version information
GIT_VERSION_FILE = local_git_version.txt

# Define the Python script to get Git version info
PYTHON_SCRIPT = get_git_version.py

.PHONY: all clean

# Default target to generate the PDF file
all: $(TARGET)

# Target to clean the temporary files and output
clean:
	rm -f $(TARGET) $(GIT_VERSION_FILE)

# Target to read the local Git version and store it in a variable
$(GIT_VERSION_FILE): $(GIT_INFO_FILE)
	@python3 $(PYTHON_SCRIPT) > $(GIT_VERSION_FILE)

# Target to generate the PDF file, using the local Git version information
$(TARGET): $(SOURCE) $(GIT_VERSION_FILE)
	asciidoctor-pdf $(SOURCE) -a pdf-theme=$(THEME) -a local_git_version="$$(cat $(GIT_VERSION_FILE))"
