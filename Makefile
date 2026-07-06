# ML Project Makefile — cross-platform (Windows / Unix)

.PHONY: install test bdd-test train clean help

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
	python -c "import shutil, glob, os; [shutil.rmtree(d, ignore_errors=True) for d in glob.glob('**/__pycache__', recursive=True) + glob.glob('**/.pytest_cache', recursive=True) + glob.glob('**/.cache', recursive=True)]; [os.remove(f) for f in glob.glob('**/*.pyc', recursive=True)]"
