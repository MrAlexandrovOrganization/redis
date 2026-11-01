-include .env
export
include makefiles/versions.mk
DOCKER_COMPOSE_BASE = docker compose --project-directory "$(CURDIR)"
include makefiles/compose.mk
DOCKER_COMPOSE = docker compose --project-directory "$(CURDIR)" $(COMPOSE_FLAGS)

up: active-check
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

.PHONY: up down logs

# Read-only validation of every tracked Compose combination, without runtime secrets.
.PHONY: compose-layout-check
compose-layout-check:
	$(DOCKER_COMPOSE_BASE) --env-file /dev/null -f compose/docker-compose.yml --profile '*' config --no-interpolate --no-env-resolution --quiet

check: compose-layout-check

.PHONY: active-check deploy
active-check:
	@test ! -e .retired || { echo "This stack has been retired" >&2; exit 1; }

deploy: active-check
	$(MAKE) up

.PHONY: config-check
config-check:
	$(DOCKER_COMPOSE) --env-file /dev/null config --quiet --no-env-resolution

check: config-check

.PHONY: ci-deploy
ci-deploy:
	python3 scripts/ci-deploy.py
