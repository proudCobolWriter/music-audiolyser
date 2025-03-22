print: $(wildcard *)
	echo "Printing all files information"
	ls -la  $?

install:
	pip install -r requirements.txt
	pip install --no-deps -e .

install-dev:
	pip install -e .[linting,formatting,other]

reqs:
	pip-compile \
	--generate-hashes \
	--output-file requirements.txt \
	--strip-extras \
	--allow-unsafe \
	pyproject.toml

reqs-dev:
	pip-compile \
	--generate-hashes \
	--output-file requirements-dev.txt \
	--extra linting,formatting,other \
	--allow-unsafe \
	pyproject.toml