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

docker-settings:
	cp .vscode/docker-settings.json .vscode/settings.json

local-settings:
	cp .vscode/local-settings.json .vscode/settings.json

run-server:
	docker run \
		--rm -d \
		--name gns3 \
		--privileged \
		-p 7070:7070 \
		davidban77/gns3-server:latest

stop-server:
	docker container stop gns3
