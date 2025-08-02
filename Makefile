ROOT := $(shell pwd)
DOCKERDIR := $(ROOT)/docker

.PHONY: coverage docs mypy ruff-check ruff-fix ruff-format test tox
.PHONY: docker-image docker-container publish-to-pypi rstcheck

coverage:
ifeq ($(OS),Windows_NT)
	coverage run -m pytest tests  # Windows: GUI windows shown (QT_QPA_PLATFORM=offscreen causes crashes)
else
	QT_QPA_PLATFORM=offscreen coverage run -m pytest tests
endif
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
ifeq ($(OS),Windows_NT)
	pytest tests/  # Windows: GUI windows shown (QT_QPA_PLATFORM=offscreen causes crashes)
else
	QT_QPA_PLATFORM=offscreen pytest tests/
endif

tox:
	tox

view-docs:
	@xdg-open "file://$(ROOT)/docs/_build/html/index.html"
