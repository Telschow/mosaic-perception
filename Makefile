.PHONY: install test lint format format-check typecheck clean run compare evaluate benchmark app trackeval-reference benchmark-golden benchmark-golden-check provenance-check

install:
	uv sync --locked --all-extras

test:
	uv run pytest

lint:
	uv run ruff check src tests scripts app

format:
	uv run ruff format src tests scripts app

format-check:
	uv run ruff format --check src tests scripts app

typecheck:
	uv run mypy src

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	uv run mosaic run --scenario nominal --seed 1

compare:
	uv run mosaic compare --scenario nominal --seeds 1,2,3

evaluate:
	uv run mosaic evaluate --scenario all --seeds 0-24 --output results/

benchmark:
	uv run mosaic benchmark --scenario all --seeds 0-24 --duration 10.0

app:
	uv run streamlit run app/streamlit_app.py

trackeval-reference:
	uv run python -m tests.crosscheck.regenerate_reference

benchmark-golden:
	uv run python scripts/check_benchmark_golden.py --update

benchmark-golden-check:
	uv run python scripts/check_benchmark_golden.py

provenance-check:
	uv run python scripts/check_artifact_provenance.py
