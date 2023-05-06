.PHONY: dev drop-db

# This Makefile target, "test", iterates through all API versions found in the
# ./spyglasses/api/ directory. For each version, it sets the SPYGLASSES_API_VERSION
# environment variable and runs the pytest command.
#
# By default, the target runs all tests in the "tests" directory.
# To run a specific test, pass the test name via the TEST_NAME variable:
#   make test TEST_NAME=test_my_function
#
# Usage examples:
#   1. Run all tests for all API versions:
#      make test
#
#   2. Run a specific test (e.g., test_my_function) for all API versions:
#      make test TEST_NAME=test_my_function
test:
	@for file in ./spyglasses/api/*; do \
		number=$$(echo $$file | sed -n 's/.*v\([0-9]*\).*/\1/p'); \
		if [ ! -z "$$number" ]; then \
			echo "Running tests with SPYGLASSES_API_VERSION=$$number"; \
			if [ -z "$(TEST_NAME)" ]; then \
				SPYGLASSES_API_VERSION=$$number pytest tests; \
			else \
				SPYGLASSES_API_VERSION=$$number pytest tests -k $(TEST_NAME); \
			fi; \
		fi; \
	done

dev:
	@echo "Running Spyglasses"
	SPYGLASSES_ENVIRONMENT=DEVELOPMENT SECRET_KEY=\x94BA\xed\x1a\x1e\x8d\xbf\xc9\xdb\xa4\x0e\x0e\xc0\xb6\xf9 flask --app spyglasses run --debug --port 8000

db_console:
	@echo "Connecting to the database"
	sqlite3 ./instance/spyglasses.db
		
