.PHONY: help format lint fix check install install-dev clean stats

# Colors for output
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
RESET := \033[0m

help: ## Show this help message
	@echo "$(GREEN)Available commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'

install: ## Install dependencies from requirements.txt
	@echo "$(GREEN)Installing dependencies from requirements.txt...$(RESET)"
	@if [ -f requirements.txt ]; then \
		pip install -r requirements.txt || pip3 install -r requirements.txt; \
	else \
		echo "$(RED)requirements.txt not found!$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Done!$(RESET)"

lint: ## Lint code (show issues without fixing)
	@echo "$(GREEN)Linting code...$(RESET)"
	@ruff check .
	@echo "$(GREEN)Done!$(RESET)"

fix: ## Fix auto-fixable issues and format
	@echo "$(GREEN)Fixing issues...$(RESET)"
	@ruff check --fix --unsafe-fixes .
	@ruff format .
	@echo "$(GREEN)Done!$(RESET)"

clean: ## Clean up cache files
	@echo "$(GREEN)Cleaning cache...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Done!$(RESET)"

stats: ## Show statistics about code quality
	@echo "$(GREEN)Code statistics:$(RESET)"
	@echo "$(YELLOW)Python files:$(RESET)" && find . -name "*.py" -type f | grep -v "__pycache__" | wc -l
	@echo "$(YELLOW)Total lines:$(RESET)" && find . -name "*.py" -type f | grep -v "__pycache__" | xargs wc -l 2>/dev/null | tail -1 || echo "0"
	@echo ""
	@echo "$(GREEN)Ruff check summary:$(RESET)"
	@ruff check . --statistics 2>/dev/null || echo "No issues found"

.DEFAULT_GOAL := help