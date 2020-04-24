#
# Makefile (for developers)
#

.PHONY: coverage
coverage:
	pytest --cov check_oldies

.PHONY: coverage-html
coverage-html:
	pytest --cov check_oldies --cov-report html
	python -c "import webbrowser; webbrowser.open('htmlcov/index.html')"

.PHONY: test
test:
	pytest

.PHONY: docs
docs:
	SPHINXOPTS="-W -n" $(MAKE) -C docs html

.PHONY: quality
quality:
	check-manifest
	isort --check-only --diff .
	pylint --reports=no setup.py src/check_oldies tests
	check-branches
	check-fixmes
	python setup.py sdist && twine check dist/*

.PHONY: clean
clean:
	rm -rf .coverage
	find . -name "*.pyc" | xargs rm -f
