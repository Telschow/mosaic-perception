.PHONY: install test lint format typecheck clean run compare app

install:
	uv sync

test:
	pytest

lint:
	ruff check src tests

format:
	ruff format src tests

typecheck:
	mypy src

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	mosaic run --scenario nominal --seed 42

compare:
	mosaic compare --scenario nominal --seeds 1,2,3

app:
	streamlit run app/streamlit_app.py
