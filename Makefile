ifeq ($(OS),Windows_NT)
ROOT := $(shell cd)
DOCKERDIR := $(ROOT)\docker
else
ROOT := $(shell pwd)
DOCKERDIR := $(ROOT)/docker
endif

.PHONY: coverage docs mypy ruff-check ruff-fix ruff-format test tox
.PHONY: docker-image docker-container publish-to-pypi rstcheck
.PHONY: pylint-sort-check pylint-sort-check-all

# Windows: GUI windows shown during tests (QT_QPA_PLATFORM=offscreen causes crashes)
# Unix/Linux/macOS: Headless testing with offscreen platform
coverage:
	./scripts/run-coverage.sh
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

pylint-sort-check:
	pylint src tests --disable=all --enable=unsorted-functions,unsorted-methods

pylint-sort-check-all:
	pylint src tests

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

# Windows: GUI windows shown during tests (QT_QPA_PLATFORM=offscreen causes crashes)
# Unix/Linux/macOS: Headless testing with offscreen platform
test:
ifeq ($(OS),Windows_NT)
	pytest tests/
else
	QT_QPA_PLATFORM=offscreen pytest tests/
endif

tox:
	tox

view-docs:
	@xdg-open "file://$(ROOT)/docs/_build/html/index.html"
