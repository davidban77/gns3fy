# Needs to be on master branch
docs-publish:
	cd docs; mkdocs gh-deploy -m "[ci skip]"

docs-generate:
	cd docs; pydoc-markdown > content/api_reference.md

docs-show:
	cd docs; mkdocs serve

test:
	poetry run flake8 .
	poetry run black --diff --check .
	poetry run tox
	poetry run pytest --cov-report=xml --cov=gns3fy tests/
