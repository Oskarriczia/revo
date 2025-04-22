.PHONY: build run tests clean unittests ut apitests at tests db

build:
	docker-compose build

run:
	docker-compose up -d app

db:
	docker-compose up -d db

tests: unittests apitests

unittests: clean
	docker-compose run unittests

ut: unittests

apitests: clean
	docker-compose run apitests

ap: apitests

clean:
	docker-compose down -v --remove-orphans