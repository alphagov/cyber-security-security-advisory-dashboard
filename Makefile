export FLASK_ENV=development

help:
	@echo "Docker-compose-backed builder for the github security advisory dashboard."
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

run: rebuild
	docker-compose up

# DEVELOP
shell:
	docker-compose run dashboard sh

rebuild:
	docker-compose build

test:
	docker-compose run dashboard sh test.sh

audit:
	docker-compose run dashboard flask audit

task:
	docker-compose run dashboard flask run-task $(TASK)

activity_prs:
	docker-compose run dashboard flask activity_prs

dependabot_status:
	docker-compose run dashboard flask dependabot-status alphagov

alert_status:
	docker-compose run dashboard flask alert-status

build_routes:
	docker-compose run dashboard flask build-routes

repo_owners:
	docker-compose run dashboard flask repo-owners

pr_status:
	docker-compose run dashboard flask pr-status


# DEPLOY
reset:
	rm -f setup.cfg

package_dir: clean
	mkdir -p build/.package/static
	mkdir -p build/.package/templates
	mkdir -p build/.package/query
	mkdir -p build/.package/output

copy_src: package_dir
	cp *.py build/.package
	cp -R static/* build/.package/static/
	cp -R templates/* build/.package/templates/
	cp -R query/* build/.package/query/
	cp -R output/* build/.package/output/

add_deps: package_dir
	bash -c "echo -e '[install]\nprefix=\n' > setup.cfg"; pip3 install -r requirements.txt -t build/.package

clean:
	rm -rf setup.cnf build/.package build/*.zip

zip: add_deps copy_src
	cd build/.package; zip -9 ../alphagov_audit_lambda_package.zip -r .

deploy: zip
	cd build/terraform; terraform apply
