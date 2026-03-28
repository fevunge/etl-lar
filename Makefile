SHELL := /bin/bash

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
STREAMLIT ?= streamlit

SRC_DIR := src
SRC := $(SRC_DIR)/main.py
REQUIREMENTS := requirements.txt
STATUS_DIR := .status
INSTALL_STAMP := $(STATUS_DIR)/installed

.DEFAULT_GOAL := help
.PHONY: help setup install run all stream clean

help:
	@echo "Targets disponíveis:"
	@echo "  make install  - instala dependências do projeto"
	@echo "  make run      - executa o pipeline ETL"
	@echo "  make stream   - executa a app com Streamlit"
	@echo "  make clean    - remove estado local de instalação"

setup:
	@mkdir -p $(STATUS_DIR)

$(INSTALL_STAMP): $(REQUIREMENTS) | setup
	@$(PIP) install -r $(REQUIREMENTS)
	@touch $(INSTALL_STAMP)
	@echo "Dependências instaladas com sucesso."

install: $(INSTALL_STAMP)
	@echo "Ambiente pronto."

run: install
	@$(PYTHON) $(SRC)

all: run

stream: install
	@$(STREAMLIT) run $(SRC)

clean:
	@rm -rf $(STATUS_DIR)
	@echo "Estado local removido."


