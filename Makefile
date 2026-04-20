# ML Project Makefile

.PHONY: install test train clean help

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run all tests"
	@echo "  make bdd-test     - Run BDD tests"
	@echo "  make train        - Train the model"
	@echo "  make clean        - Clean generated files"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

bdd-test:
	pytest tests/bdd/ -v --cov=src

train:
	python src/training/train.py --config config/default_config.yaml

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".cache" -exec rm -r {} +
