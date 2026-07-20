PROJECT_NAME := starlette-request-id
SRC_PATH := src/starlette_request_id
LINT_PATHS := src tests examples
UV ?= uv

.DEFAULT_GOAL := help

.PHONY: help venv/install/main venv/install/all lint/ruff lint/mypy lint format test build clean sys/changelog sys/tag

help: ## Display this help message
	@awk 'BEGIN { FS = ":.*##"; printf "\nUsage:\n  make <target>\n\nTargets:\n" } /^[a-zA-Z0-9_./-]+:.*##/ { printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

venv/install/main: ## Install main dependencies
	$(UV) sync --no-group dev

venv/install/all: ## Install all dependency groups
	$(UV) sync --all-groups

lint/ruff: ## Check formatting and lint with Ruff
	$(UV) run --locked ruff format --check $(LINT_PATHS)
	$(UV) run --locked ruff check $(LINT_PATHS)

lint/mypy: ## Type-check the source package with mypy
	$(UV) run --locked mypy $(SRC_PATH)

lint: lint/ruff lint/mypy ## Run all lint checks

format: ## Format and auto-fix lint issues
	$(UV) run --locked ruff format $(LINT_PATHS)
	$(UV) run --locked ruff check --fix $(LINT_PATHS)

test: ## Run the test suite with coverage
	$(UV) run --locked pytest --cov=starlette_request_id --cov-report=term-missing

build: ## Build distribution packages
	$(UV) build

clean: ## Remove generated files and caches
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

sys/changelog: ## Generate CHANGELOG.md from semantic version tags
	@tmp_file=$$(mktemp CHANGELOG.md.XXXXXX) || exit $$?; \
	tags="$$(git tag --sort=-version:refname | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+$$')"; \
	[ -n "$$tags" ] || { echo "No semantic-version tags found." >&2; exit 1; }; \
	{ \
		printf '# Changelog\n\n'; set -- $$tags; newest=$$1; \
		unreleased=$$(git log --no-merges "$$newest..HEAD" --format='* %s [%an]' --reverse); \
		[ -z "$$unreleased" ] || printf '## Unreleased\n\n%s\n\n' "$$unreleased"; \
		while [ $$# -gt 0 ]; do current=$$1; shift; previous=$${1:-}; date=$$(git log -1 --format=%as "$$current"); \
			printf '## %s (%s)\n\n' "$${current#v}" "$$date"; \
			if [ -n "$$previous" ]; then git log --no-merges "$$previous..$$current" --format='* %s [%an]' --reverse; else git log --no-merges "$$current" --format='* %s [%an]' --reverse; fi; \
			printf '\n'; \
		done; \
	} > "$$tmp_file" && mv "$$tmp_file" CHANGELOG.md

sys/tag: ## Create and push a vX.Y.Z release tag
	@read -r -p "Enter tag version (e.g., 2.0.0): " TAG; \
	printf '%s\n' "$$TAG" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$$' || exit 1; \
	VERSION="$$( $(UV) run --locked python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])' )"; \
	[ "$$VERSION" = "$$TAG" ] || { echo "Tag and project versions differ." >&2; exit 1; }; \
	[ -z "$$(git status --porcelain --untracked-files=all)" ] || { echo "Worktree must be clean." >&2; exit 1; }; \
	! git show-ref --verify --quiet "refs/tags/v$$TAG" || { echo "Tag already exists." >&2; exit 1; }; \
	git tag -a "v$$TAG" -m "Release v$$TAG" && git push origin "v$$TAG"
