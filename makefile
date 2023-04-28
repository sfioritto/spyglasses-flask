.PHONY: test dev

test:
ifdef VERSION
	@echo "Running tests with SPYGLASSES_API_VERSION=$(VERSION)"
	SPYGLASSES_API_VERSION=$(VERSION) python -m unittest
else
	@echo "Running tests"
	SPYGLASSES_API_VERSION= python -m unittest
endif

dev:
ifdef VERSION
	@echo "Running Flask app with SPYGLASSES_API_VERSION=$(VERSION)"
	SPYGLASSES_API_VERSION=$(VERSION) flask --app spyglasses run --debug
else
	@echo "Running Spyglasses"
	SPYGLASSES_API_VERSION= flask --app spyglasses run --debug
endif
