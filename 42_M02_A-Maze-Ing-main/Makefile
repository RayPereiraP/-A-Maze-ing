MAIN = a_maze_ing

RM = rm -f

VENV_DIR := .venv
VENV_PY := $(VENV_DIR)/bin/python

# if venv exists, use it
ifeq ($(wildcard $(VENV_PY)),)
  PYTHON ?= python3
  PIP ?= pip3
  ACTIVATE = . $(VENV_DIR)/bin/activate

else
  PYTHON := $(VENV_PY)
  PIP := $(VENV_DIR)/bin/pip

endif

REQ = dev-requirements.txt
CONFIG = config.txt
OUTPUT_FILE := $(shell grep '^OUTPUT_FILE=' $(CONFIG) | cut -d'=' -f2)
SETUP := setup.py

# --- colours ---
RESET := \033[0m
BOLD  := \033[1m
RED   := \033[31m
GRN   := \033[32m
YEL   := \033[33m
BLU   := \033[34m

all: run

help:
	@printf "$(YEL)make install$(RESET)		# install dependencies (current env)\n"
	@printf "$(YEL)make venv-install$(RESET)	# create venv + install dependencies\n\n"
	@printf "$(YEL)make / make all / make run$(RESET)	# run program\n"
	@printf "$(YEL)make debug$(RESET)			# run program in pdb\n\n"
	@printf "$(YEL)make lint$(RESET)		# run flake8 and mypy\n"
	@printf "$(YEL)make lint-strict$(RESET)	# run flake8 and mypy in a strict mode\n\n"
	@printf "$(YEL)make clean$(RESET)		# remove caches and temps\n"
	@printf "$(YEL)make venv-clean$(RESET)		# remove venv\n"
	@printf "$(YEL)make fclean$(RESET)		# remove caches and temps + venv\n"
	@printf "$(YEL)make re$(RESET)			# make fclean + make all together\n\n"
	@printf "$(YEL)make build$(RESET)		# create a .whl and .tar.gz packages\n"

install:
	@printf "Installing dependencies...\n"
ifeq ($(wildcard $(VENV_PY)),)
	@read -p "Virtual env not found. Install dependencies globally? [y/N]: " yn; \
	if [ "$$yn" = "y" ] || [ "$$yn" = "Y" ]; then \
		$(PIP) install -qr $(REQ); \
		@printf "$(YEL)Dependencies installed successfully in the global environment$(RESET)\n"; \
	else \
		printf "Skipped installation. Use $(YEL)make venv-install$(RESET) to create virtual env.\n"; \
	fi
else
	@read -p "Virtual env detected. Install dependencies into $(VENV_DIR)? [y/N]: " yn; \
	if [ "$$yn" = "y" ] || [ "$$yn" = "Y" ]; then \
		$(PIP) install -qr $(REQ); \
		printf "$(YEL)Dependencies installed successfully in the virtual env $(VENV_DIR)$(RESET)\n"; \
	else \
		printf "Skipped installation.\n"; \
	fi
endif

venv-install:
ifeq ($(wildcard $(VENV_PY)),)
	@printf "Creating virtual environment...\n"
	@$(PYTHON) -m venv $(VENV_DIR)
	@printf "$(YEL)Virtual env created in $(VENV_DIR)$(RESET)\n"
	@printf "Activate it: $(YEL)source $(VENV_DIR)/bin/activate$(RESET)\n"
endif
	@$(MAKE) -s install

run:
	$(PYTHON) -m $(MAIN) $(CONFIG)

build:
	$(PYTHON) -m build

debug:
	$(PYTHON) -m pdb $(MAIN).py $(CONFIG)

clean:
	@find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) -exec rm -r {} +
	@$(RM) $(OUTPUT_FILE) $(LINT_LOGFILE)
	@printf "$(YEL)Caches successfully deleted.$(RESET)\n"

venv-clean:
	@$(RM) -r $(VENV_DIR)
	@printf "$(YEL)Virtual env $(VENV_DIR) successfully deleted.$(RESET)\n"

fclean: clean venv-clean

LINT_LOGFILE=lint.log
# MYPY_FLAGS := --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
MYPY_EXCLUDE = --exclude '($(VENV_DIR)|venv|_private|Makefile)'
FLAKE_EXCLUDE = --exclude=$(VENV_DIR),venv,_private,Makefile
# use exclude/ignore files for mypy and flake?

.lint-base:
	@overall=0; \
	echo "" > $(LINT_LOGFILE); \
	# --- flake8 --- \
	printf "Running flake8... "; \
	if command -v flake8 >/dev/null 2>&1; then \
		status=0; \
		echo "flake8" > $(LINT_LOGFILE); \
		flake8 . $(FLAKE_EXCLUDE) >> $(LINT_LOGFILE) 2>&1 || status=1; \
		if [ $$status -eq 0 ]; \
		then printf "$(GRN)[OK]$(RESET)\n"; \
		else printf "$(RED)[KO]$(RESET)\n"; \
		fi; \
		overall=$$((overall | $$status)); \
	else \
		printf "\n\n$(YEL)[WARNING]:$(RESET) flake8 not installed\n"; \
		printf "install with: $(YEL)pip install flake8$(RESET) or $(YEL)make venv-install$(RESET)\n"; \
		status=1; \
		overall=$$((overall | $$status)); \
	fi; \
	# --- mypy --- \
	printf "Running mypy... "; \
	if command -v mypy >/dev/null 2>&1; then \
		status=0; \
		echo "" >> $(LINT_LOGFILE); \
		echo "mypy" >> $(LINT_LOGFILE); \
		mypy . $(MYPY_FLAGS) $(MYPY_EXCLUDE) >> $(LINT_LOGFILE) 2>&1 || status=1; \
		if [ $$status -eq 0 ]; \
		then printf "$(GRN)[OK]$(RESET)\n"; \
		else printf "$(RED)[KO]$(RESET)\n"; \
		fi; \
		overall=$$((overall | $$status)); \
	else \
		printf "\n\n$(YEL)[WARNING]:$(RESET) mypy not installed\n"; \
		printf "install with: $(YEL)make install$(RESET) or $(YEL)make venv-install$(RESET)\n"; \
	fi; \
	if [ $$status -eq 0 ]; then \
		printf "\n✅ $(GRN)Lint passed!$(RESET)\n"; \
	else \
		printf "\n❌ $(RED)Lint failed!$(RESET)\n"; \
		printf " - check $(BLU)$(LINT_LOGFILE)$(RESET) for details\n"; \
	fi
# 	exit $$overall

lint: MYPY_FLAGS := --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
lint: .lint-base

lint-strict: MYPY_FLAGS := --strict
lint-strict: .lint-base

re: clean all

.PHONY: all clean install run debug lint lint-strict re help venv-install venv-clean fclean build
