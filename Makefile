# Needs to be on master branch
docs-publish:
	mkdocs gh-deploy -m "[ci skip]" --force

docs-generate:
	pydoc-markdown docs/pydoc-markdown.yml > docs/content/api_reference.md

docs-show:
	mkdocs serve

test:
	poetry run ruff check .
	poetry run ruff format --check .
	poetry run pytest --cov-report=html --cov=gns3fy tests/

build:
	poetry build

publish:
	poetry publish

gh-release:
	gh release create v${VERSION} -F docs/content/about/changelog.md -t "Release v${VERSION}" --repo yueguobin/gns3fy-next

docker-settings:
	cp .vscode/docker-settings.json .vscode/settings.json

local-settings:
	cp .vscode/local-settings.json .vscode/settings.json
