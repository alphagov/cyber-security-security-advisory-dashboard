
help:
	@echo "Docker-compose-backed builder for the github security advisory dashboard."
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

# DEVELOP
run: rebuild assets
	docker-compose up

shell:
	docker-compose run dashboard bash

rebuild:
	docker-compose build --pull

test:
	export FLASK_ENV=development
	docker-compose run -e TOKEN=faketoken dashboard ./test.sh tests

contract-test:
	export FLASK_ENV=development
	docker-compose run dashboard ./test.sh contract_tests

audit:
	docker-compose run dashboard python -m cProfile -o audit.profile audit_lambda.py audit

task:
	docker-compose run dashboard python audit_lambda.py run-task $(TASK)

send_to_splunk:
	docker-compose run dashboard python audit_lambda.py send_to_splunk

# DEPLOY
reset:
	rm -f setup.cfg

clean:
	rm -rf setup.cnf build/.package build/*.zip

zip:
	docker-compose run dashboard bash pack.sh

deploy: zip
	cd build/terraform; terraform apply
