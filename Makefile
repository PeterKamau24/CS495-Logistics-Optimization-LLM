.PHONY: setup test lint run clean

setup:
	poetry install

test:
	poetry run pytest

lint:
	poetry run ruff check .

run:
	poetry run python src/main.py

clean:
	powershell -Command "Remove-Item -Recurse -Force .pytest_cache, __pycache__ -ErrorAction SilentlyContinue"