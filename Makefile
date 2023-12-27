MAKEPATH := $(abspath $(lastword $(MAKEFILE_LIST)))
PWDSLASH := $(dir $(MAKEPATH))
PWD := $(realpath -s $(PWDSLASH))
PROJECT_ID=$(shell gcloud config get-value project)
APP=indoor-tent-control
ENVIRONMENT=DEV

# -------------------------------------------
#
# Git info
#
# -------------------------------------------
ifndef ${TAG}
	TAG := $(shell git --git-dir=$(PWD)/.git rev-parse HEAD)
endif
ifndef ${SHORT_TAG}
	SHORT_TAG := $(shell git --git-dir=$(PWD)/.git rev-parse --short HEAD)
endif
ifndef ${BRANCH}
	BRANCH := $(shell git --git-dir=$(PWD)/.git rev-parse --abbrev-ref HEAD)
endif

# -------------------------------------------
#
# Help
#
# -------------------------------------------
.DEFAULT_GOAL := help
help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

# -------------------------------------------
#
# Project info run: make info
#
# -------------------------------------------
.PHONY: info
info:			## Useful information
	@echo "--------------------------------------------------------------"
	@echo "Commands:"
	@echo " - make docker-build\t Docker build all containers for production"
	@echo " - make deploy     \t Compile source, lint, test, docker push and terraform deployment"
	@echo "--------------------------------------------------------------"
	@echo "Workdir (pwd): \t\t${PWD}"
	@echo "Git branch: \t\t${BRANCH}"
	@echo "Git tag: \t\t${TAG}"
	@echo "Git short tag: \t\t${SHORT_TAG}"
	@echo "\n"

# -------------------------------------------
# Dev commands
# -------------------------------------------
.PHONY: clear-db create-db-tables seed-db-tables fill-db-tables clear-and-fill-db ingest-data
clear-db:
	poetry run python data/clear_db.py

create-db-tables:
	poetry run python models/__init__.py

seed-db-tables:
	poetry run python data/db_seeds.py

ingest-data:
	poetry run python src/ingest/roster.py
	poetry run python src/ingest/player.py
	poetry run python src/ingest/schedule.py

process-data:
	poetry run python src/process/player_schedule_points.py
	
clear-and-fill-db:
	@make clear-db
	@make create-db-tables
	@make seed-db-tables
	@make ingest-data
	@make process-data

up:
	poetry run streamlit run render/main.py

install:
	poetry install

format:
	poetry run isort .
	poetry run black .

lint:
	poetry run ruff . --fix

test:
	poetry run pytest --cov-report=html --cov -v

update:
	poetry update

check:
	@make install
	@make format
	@make lint
	@make test

ifeq ($(OS),Windows_NT)
    # If running on Windows
    TREE_CMD = dir /S /B

else
    # If running on Unix-like systems (Linux or macOS)
    ifeq ($(shell command -v pbcopy 2> /dev/null),)
        ifeq ($(shell command -v xclip 2> /dev/null),)
            $(error Clipboard utility (pbcopy or xclip) not found)
        else
            TREE_CMD = tree -I '_pycache_|env|venv' | xclip -selection clipboard
        endif
    else
        TREE_CMD = tree -I '_pycache_|env|venv' | pbcopy
    endif
endif

.PHONY: tree lint
tree:
	$(TREE_CMD)