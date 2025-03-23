BGREEN:=\033[1;32m
BRED:=\033[1;31m
NC:=\033[0m

print: $(wildcard *)
	echo "Printing all files' information"
	ls -la  $?

cleancode:
	@printf "$(BRED)Formatting the codebase using Black:$(NC)\n"
	black .

checkcode:
	@printf "$(BRED)Checking the codebase's formatting using Black:$(NC)\n"
	black . --check
	@sleep 1.5
	@printf "$(BGREEN)Now linting the code using Pylint:$(NC)\n"
	-pylint . || true

install:
	pip install -r requirements.txt
	pip install --no-deps -e .

install-docker:
	# shrinks image size by removing cache 
	pip install -r requirements.txt --no-cache-dir
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