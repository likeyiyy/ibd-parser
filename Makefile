.PHONY: clean build publish test bump-patch bump-minor bump-major

clean:
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

test:
	python -m pytest tests/

publish: build
	python -m twine upload dist/*

bump-patch:
	bump2version patch

bump-minor:
	bump2version minor

bump-major:
	bump2version major

install-dev:
	pip install -e ".[dev]"
	pip install bump2version build twine pytest
