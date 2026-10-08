# Interpreter and config used by the rules; both can be changed on the
# command line, e.g. "make run CONFIG=other.txt".
PYTHON = python3
CONFIG = config.txt
MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# None of the rules creates a file with its own name.
.PHONY: install run debug clean lint lint-strict build

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	find . -type d \( -name __pycache__ -o -name .mypy_cache \
		-o -name .pytest_cache \) -prune -exec rm -rf {} +
	rm -rf build mazegen.egg-info

# The folders left out of the lint are listed in setup.cfg.
lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(MYPY_FLAGS)

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

# Builds mazegen-*.whl and mazegen-*.tar.gz at the root of the repository.
build:
	$(PYTHON) -m build --outdir .
