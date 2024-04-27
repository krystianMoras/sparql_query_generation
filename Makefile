install:
	pip install poetry
	poetry install
run:
	poetry run python src/sparql_query_generation/server.py