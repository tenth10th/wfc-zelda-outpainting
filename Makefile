lint:
	ruff check .

format:
	ruff format .

test:
	pytest .

build: format lint test