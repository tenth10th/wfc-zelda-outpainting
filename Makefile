lint:
	ruff check .

format:
	ruff format .

test:
	pytest .

build: format lint test

reqs:
	pipenv requirements --dev > requirements.txt

upgrade:
	pipenv update

deps: upgrade reqs