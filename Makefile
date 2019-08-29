export FLASK_ENV=development

help:
	@echo "Docker-compose-backed builder for the github security advisory dashboard."
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

run: gulp
	docker-compose up

shell:
	docker-compose run dashboard sh

rebuild:
	docker-compose build

test:
	docker-compose run dashboard sh test.sh

audit:
	docker-compose run dashboard flask audit

gulp:
	docker-compose run dashboard sh -c 'cd build && npm install && npm rebuild node-sass && gulp'
