#PYTHON_SOURCES = publication_admin tests migrations
#
#run:  ## [Local development] Run document publication admin API over HTTP on port 8000
#	uvicorn publication_admin.main:app --host 0.0.0.0 --port 8000 --reload
#
#run_worker:
#	taskiq worker publication_admin.worker.engine:tasksiq_broker publication_admin.worker.tasks.schedules --reload
#
#run_scheduler:
#	taskiq scheduler publication_admin.worker.engine:taskiq_scheduler publication_admin.worker.tasks.schedules
#
#run-local-infra:
#	docker compose up -d postgres rabbit redis kafka
#
#test:
#	pytest -m "not integration" --cov=publication_admin --junitxml=report.xml -k '$(TEST)'
#
#test-integration:
#	alembic upgrade head
#	alembic check
#	pytest -m "integration" --exitfirst --cov=publication_admin --cov-report=html --junitxml=report.xml -k '$(TEST)'
#
#docker-test-integration: ## [Local development] Run integration tests with docker locally
#	docker compose up --exit-code-from test-app --abort-on-container-exit test-app postgres
#
#run-infra:  ## [Local development] Up local dependencies for development (postgres, rabbit and scheduler)
#	docker compose up -d postgres rabbit scheduler -d
#
#down-infra:  ## [Local development] Shut down local services
#	docker compose down
#
#coverage:
#	pytest -m "not integration" --cov=publication_admin --cov-report=html
#	open htmlcov/index.html
#
#lint:  ## [Local development] Run code quality checks (formatting, imports, lint, types, etc)
#	ruff check ${PYTHON_SOURCES} && ruff format --check ${PYTHON_SOURCES}
#
#format:  ## [Local development] Auto-format python code
#	ruff format ${PYTHON_SOURCES} && ruff check --fix ${PYTHON_SOURCES}
#
make-migrations:
	alembic revision --autogenerate

migrate:
	alembic upgrade head
#
#.PHONY: help
#
#help: # Run `make help` to get help on the make commands
#	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
