DOCKER_ORG := ritualnetwork
EXAMPLE_NAME := telegram

TAG_APP := $(DOCKER_ORG)/example-$(EXAMPLE_NAME)-infernet:latest
TAG_TELEGRAM_POLLING := $(DOCKER_ORG)/$(EXAMPLE_NAME)-polling:latest

build_app:
	@docker build -t $(TAG_APP) --build-arg appname=app --build-arg port=3000 .
	jq ".containers[0].image = \"$(TAG_APP)\"" config.json > updated_config.json && mv updated_config.json config.json

build_telegram_polling:
	@docker build -t $(TAG_TELEGRAM_POLLING) --build-arg appname=telegram_polling --build-arg port=3001 .

build: build_app build_telegram_polling 

run_app: build_app
	docker run --env-file $(EXAMPLE_NAME).env -p 3000:3000 $(TAG_APP)

run_telegram_polling: build_telegram_polling
	docker run -d --env-file $(EXAMPLE_NAME).env -p 3001:3001 $(TAG_TELEGRAM_POLLING)

run: run_telegram_polling run_app 