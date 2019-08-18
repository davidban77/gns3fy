docs-publish:
	cd docs; mkdocs gh-deploy -m "[ci skip]"

docs-generate:
	cd docs; pydoc-markdown > content/api_reference.md

docs-show:
	cd docs; mkdocs serve
