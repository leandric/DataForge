# =========================
# Configurações
# =========================
PYTHON := python
PYTEST := pytest
TEST_DIR := test

# =========================
# Targets
# =========================

.PHONY: help test test-sync test-async test-carga clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make test        -> roda todos os testes"
	@echo "  make test-sync   -> roda testes síncronos"
	@echo "  make test-async  -> roda testes assíncronos"
	@echo "  make test-carga  -> roda teste de carga (milhares de clientes)"
	@echo "  make clean       -> limpa cache de testes"

# Roda todos os testes
test:
	$(PYTHON) -m $(PYTEST) -q -s

# Apenas testes síncronos
test-sync:
	$(PYTHON) -m $(PYTEST) -q -s $(TEST_DIR)/test_carga_clientes.py

# Apenas testes assíncronos
test-async:
	$(PYTHON) -m $(PYTEST) -q -s $(TEST_DIR)/test_carga_clientes_async.py

# Alias semântico para teste de carga
test-carga: test-sync

# Limpa cache do pytest e bytecode
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache