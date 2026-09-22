PYTHON ?= python3

.PHONY: run vfs test lint clean

run: vfs
	$(PYTHON) src/main.py --vfs build/vfs/deep.zip

vfs:
	$(PYTHON) tools/make_vfs.py

test:
	$(PYTHON) -m pytest -v

lint:
	$(PYTHON) -m flake8 src tests tools

clean:
	rm -rf build .pytest_cache
	find . -name __pycache__ -type d -exec rm -rf {} +
