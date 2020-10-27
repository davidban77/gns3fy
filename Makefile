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
	poetry run tox -e py38
	poetry run pytest --cov-report=html --cov=gns3fy tests/

build:
	poetry build

publish:
	poetry publish

docker-settings:
	cp .vscode/docker-settings.json .vscode/settings.json

local-settings:
	cp .vscode/local-settings.json .vscode/settings.json
