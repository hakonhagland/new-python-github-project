ROOT := $(shell pwd)
DOCKERDIR := $(ROOT)/docker

.PHONY: coverage docs mypy test flake8 tox
.PHONY: black-check black publish-to-pypi isort

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

isort:
	isort --diff --check-only --profile black src/ tests/
	isort --diff --profile black src/ tests/

mypy:
	mypy src/ tests/

test:
	pytest tests/

flake8:
	flake8 src/ tests/

black-check:
	black --diff --color src/ tests/

black:
	black src/ tests/

publish-to-pypi:
	poetry publish --build

tox:
	tox
