export FLASK_ENV=development

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
	docker-compose run dashboard sh

rebuild:
	docker-compose build

assets:
	docker-compose run dashboard sh assets.sh

test:
	docker-compose run dashboard sh test.sh

audit:
	docker-compose run dashboard python audit_lambda.py

task:
	docker-compose run dashboard python audit_lambda.py run-task $(TASK)

# DEPLOY
reset:
	rm -f setup.cfg

clean:
	rm -rf setup.cnf build/.package build/*.zip

zip:
	docker-compose run dashboard bash pack.sh

deploy: zip
	cd build/terraform; terraform apply
