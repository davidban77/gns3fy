# Needs to be on master branch
docs-publish:
	mkdocs gh-deploy -m "[ci skip]" --force

docs-generate:
	pydoc-markdown docs/pydoc-markdown.yml > docs/content/api_reference.md

docs-show:
	mkdocs serve

test:
	poetry run flake8 .
	poetry run black --diff --check .
	poetry run pytest --cov-report=html --cov=gns3fy tests/

build:
	poetry build

publish:
	poetry publish

gh-release:
	gh release create v${VERSION} -F docs/content/about/changelog.md -t "Release v${VERSION}" --repo davidban77/gns3fy

docker-settings:
	cp .vscode/docker-settings.json .vscode/settings.json

local-settings:
	cp .vscode/local-settings.json .vscode/settings.json
