# api/models/__init__.py
from .clientes_models import Cliente
from .produtos_model import Produto
from .lojas_models import Loja
from .vendas_models import Venda

__all__ = ["Cliente", "Produto", "Loja", "Venda"]
