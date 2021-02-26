.PHONY: bundle
bundle:
	rm -rf ./python && mkdir -p ./python
	find . -type d -name __pycache__ -exec rm -r {} \+
	poetry export -f requirements.txt --without-hashes > requirements-poetry.txt
	cat requirements-poetry.txt

.PHONY: clean
clean:
	rm -rf python/ ASTDEPythonUtils_layer.zip requirements-poetry.txt
