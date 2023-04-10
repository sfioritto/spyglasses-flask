.PHONY: test dev

test:
	@for file in ./spyglasses/api/*; do \
		number=$$(echo $$file | sed -n 's/.*v\([0-9]*\).*/\1/p'); \
		if [ ! -z "$$number" ]; then \
			echo "Running tests with SPYGLASSES_API_VERSION=$$number"; \
			SPYGLASSES_API_VERSION=$$number python -m unittest; \
		fi; \
	done



dev:
	@echo "Running Spyglasses"
	SPYGLASSES_ENVIRONMENT=DEVELOPMENT flask --app spyglasses run --debug --port 8000
