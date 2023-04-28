.PHONY: test dev

test:
ifdef VERSION
	@echo "Running tests with SPYGLASSES_API_VERSION=$(VERSION)"
	SPYGLASSES_API_VERSION=$(VERSION) python -m unittest
else
	@echo "Running tests"
	python -m unittest
endif

dev:
	@echo "Running Spyglasses"
	flask --app spyglasses run --debug
