UV := uv
PY := $(UV) run python3
DEB := pdb

install: .venv/.installed

.venv/.installed: uv.lock pyproject.toml
	$(UV) sync
	@touch $@

run: .venv/.installed
	$(PY) main.py

debug: .venv/.installed
	$(PY) -m $(DEB) main.py

clean: .venv/.installed
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

fclean: clean
	rm -rf .venv

re: fclean install

lint: .venv/.installed
	$(UV) run flake8 main.py
	$(UV) run mypy main.py --warn-return-any \
		      --warn-unused-ignores \
		      --ignore-missing-imports \
		      --disallow-untyped-defs \
		      --check-untyped-defs

.PHONY: install run debug clean fclean lint re
