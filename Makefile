ROOT := $(shell pwd)
DOCKERDIR := $(ROOT)/docker

.PHONY: coverage docs mypy ruff-check ruff-fix ruff-format test tests-xvfb tox
.PHONY: docker-image docker-container publish-to-pypi rstcheck

coverage:
	coverage run -m pytest tests
	coverage report -m

docker-image:
	"$(DOCKERDIR)"/build-docker.sh "$(DOCKERDIR)"

docker-container:
	xhost +
	docker run --rm -e DISPLAY=${DISPLAY} -v /tmp/.X11-unix:/tmp/.X11-unix:rw -it python-ghproj
	xhost -

docs:
	cd "$(ROOT)"/docs && make clean && make html

mypy:
	mypy src/ tests/

pre-commit:
	pre-commit run --all-files

publish-to-pypi:
	uv build
	twine upload dist/*

# NOTE: to avoid rstcheck to fail on info-level messages, we set the report-level to WARNING
rstcheck:
	rstcheck --report-level=WARNING -r docs/

ruff-check:
	ruff check src tests

ruff-fix:
	ruff check --fix src tests

ruff-format:
	ruff format src tests

test:
	@if [ "$(shell uname -s)" = "Darwin" ]; then \
		QT_QPA_PLATFORM=offscreen pytest tests/; \
	elif [ "$(shell uname -s)" = "Linux" ] && echo "$(shell uname -r)" | grep -q microsoft; then \
		QT_QPA_PLATFORM=offscreen pytest tests/; \
	elif [ "$(shell uname -s)" = "Linux" ]; then \
		xvfb-run -a pytest tests/; \
	else \
		pytest tests/; \
	fi

# Run tests with xvfb for headless GUI testing on native Linux
# Note: Requires 'sudo apt install xvfb' on Ubuntu/Debian systems
tests-xvfb:
	xvfb-run -a pytest tests/

tox:
	tox

view-docs:
	@xdg-open "file://$(ROOT)/docs/_build/html/index.html"
