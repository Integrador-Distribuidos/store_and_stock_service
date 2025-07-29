from sqlalchemy.orm import Session
from datetime import datetime, date
from sqlalchemy import inspect, null
from app.models import models, product_audit, stock_audit, stock_movement_audit
from decimal import Decimal
from sqlalchemy import inspect


# Funções auxiliares (mantidas conforme o original, mas podem ser colocadas em um utilitário)
def serialize_for_json(data):
    """
    Converte objetos datetime e date em strings ISO 8601 para serialização JSON.
    """
    def convert(value):
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return value
    # Aplica a conversão recursivamente se houver dicionários aninhados,
    # embora o inspect.column_attrs geralmente retorne apenas campos de nível superior.
    # Para simplicidade, a versão original que funciona para dicionários de nível único é mantida.
    return {key: convert(val) for key, val in data.items()}

def serialize_stocks(origin, destination):
    return {
        "origin_stock": obtain_serializable_data(origin) if origin else None,
        "destination_stock": obtain_serializable_data(destination) if destination else None
    }

def obtain_serializable_data(obj):
    def make_serializable(value):
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        return value

    return {
        c.key: make_serializable(getattr(obj, c.key))
        for c in inspect(obj).mapper.column_attrs
    }

def obtain_data(object:dict):
        # 2. Obter os dados atuais da movimentação (snapshot)
        # É importante que o objeto 'movement' esteja em um estado consistente aqui.
    data_object = {
            c.key: getattr(object, c.key)
            for c in inspect(object).mapper.column_attrs
        }
    return data_object


def product_audit_(db: Session, id_product: int, operation: str, old_data: dict, new_data: dict, changed_by: int):
    """
    Cria um registro de auditoria para alterações rrelacionadas a Produto.

    Args:
        db (Session): A sessão do banco de dados.
        id_product (int): O ID do produto a ser auditado.
        operation (str): A operação realizada (ex: 'CREATE', 'UPDATE', 'DELETE').
        changed_by (int): O ID do usuário que realizou a operação.

    Raises:
        ValueError: Se o produto não for encontrado.
        Exception: Para outros erros inesperados durante a auditoria.
    """
    try:
        # 1. Recuperar a movimentação de estoque
        product = db.query(models.Product).filter(models.Product.id_product == id_product).first()
        
        if not product:
            # Usar ValueError é mais específico do que Exception genérica para "não encontrado"
            raise ValueError(f"Produto com ID {id_product} não encontrado para auditoria.")


        serialized_old_product_data = None
        serialized_new_product_data = None
        # 3. Serializar dados para formato JSON (especialmente datas)
        # O resultado é um dicionário Python que será armazenado no campo JSONB.
        if old_data:
            serialized_old_product_data = serialize_for_json(old_data)
        if new_data:
            serialized_new_product_data = serialize_for_json(new_data)

        # 4. Criar o registro de auditoria
        # Assumindo que models.stock_movement_audit.StockMovementAudit é o modelo correto.
        # Se 'data' for mapeado para 'new_data' no seu modelo de auditoria, ajuste aqui.
        audit_record = product_audit.ProductAudit( # ou models.StockMovementAudit
            id_product=id_product,
            operation=operation.upper(), # Garante que a operação seja em maiúsculas
            # Passa o dicionário Python. O driver do banco de dados/ORM cuidará da conversão para JSONB.
            old_data=serialized_old_product_data, 
            new_data=serialized_new_product_data,
            changed_by=changed_by,
            date=datetime.utcnow() # Timestamp UTC para consistência
        )

        # 5. Adicionar e commitar a auditoria no banco de dados
        db.add(audit_record)
        db.commit()
        # db.refresh(audit_record) # Opcional: Se precisar do ID do registro de auditoria recém-criado

    except ValueError as ve:
        print(f"Erro de Validação na Auditoria de Produto: {ve}")
        db.rollback() # Garante que a transação seja desfeita em caso de erro
        raise # Re-levanta a exceção para que o chamador possa tratá-la
    except Exception as e:
        print(f"Erro inesperado durante a auditoria de Produto {id_product}: {e}")
        db.rollback() # Em caso de qualquer outro erro, desfaz a transação
        raise # Re-levanta a exceção





def movement_audit(db: Session, id_movement: int, operation: str,old_data: dict, new_data: dict, changed_by: int):
    """
    Cria um registro de auditoria para uma movimentação de estoque.

    Args:
        db (Session): A sessão do banco de dados.
        id_movement (int): O ID da movimentação de estoque a ser auditada.
        operation (str): A operação realizada (ex: 'CREATE', 'UPDATE', 'DELETE').
        changed_by (int): O ID do usuário que realizou a operação.

    Raises:
        ValueError: Se a movimentação não for encontrada.
        Exception: Para outros erros inesperados durante a auditoria.
    """

    try:
        # 1. Recuperar a movimentação de estoque
        movement = db.query(models.StockMovement).filter(models.StockMovement.id_movement == id_movement).first()
        
        if not movement:
            # Usar ValueError é mais específico do que Exception genérica para "não encontrado"
            raise ValueError(f"Movimentação de estoque com ID {id_movement} não encontrada para auditoria.")

        serialized_old_movement_data = None
        serialized_new_movement_data = None

        # 3. Serializar dados para formato JSON (especialmente datas)
        # O resultado é um dicionário Python que será armazenado no campo JSONB.
        if new_data:
            serialized_new_movement_data = serialize_for_json(new_data)
        if old_data:
            serialized_old_movement_data = serialize_for_json(old_data)

        # 4. Criar o registro de auditoria
        # Assumindo que models.stock_movement_audit.StockMovementAudit é o modelo correto.
        # Se 'data' for mapeado para 'new_data' no seu modelo de auditoria, ajuste aqui.
        audit_record = stock_movement_audit.StockMovementAudit( # ou models.StockMovementAudit
            id_movement=id_movement,
            operation=operation.upper(), # Garante que a operação seja em maiúsculas
            # Passa o dicionário Python. O driver do banco de dados/ORM cuidará da conversão para JSONB.
            new_data=serialized_new_movement_data,
            old_data=serialized_old_movement_data, 
            changed_by=changed_by,
            date=datetime.utcnow() # Timestamp UTC para consistência
        )

        # 5. Adicionar e commitar a auditoria no banco de dados
        db.add(audit_record)
        db.commit()
        # db.refresh(audit_record) # Opcional: Se precisar do ID do registro de auditoria recém-criado

    except ValueError as ve:
        print(f"Erro de Validação na Auditoria de Movimentação: {ve}")
        db.rollback() # Garante que a transação seja desfeita em caso de erro
        raise # Re-levanta a exceção para que o chamador possa tratá-la
    except Exception as e:
        print(f"Erro inesperado durante a auditoria da movimentação {id_movement}: {e}")
        db.rollback() # Em caso de qualquer outro erro, desfaz a transação
        raise # Re-levanta a exceção




def stock_audit_(db: Session, id_stock: int, operation: str, old_data: dict, new_data: dict, changed_by: int):
    """
    Cria um registro de auditoria para alterações rrelacionadas a Estoque.

    Args:
        db (Session): A sessão do banco de dados.
        id_product (int): O ID do produto a ser auditado.
        operation (str): A operação realizada (ex: 'CREATE', 'UPDATE', 'DELETE').
        changed_by (int): O ID do usuário que realizou a operação.

    Raises:
        ValueError: Se o produto não for encontrado.
        Exception: Para outros erros inesperados durante a auditoria.
    """
    try:
        # 1. Recuperar a movimentação de Estoque
        stock = db.query(models.Stock).filter(models.Stock.id_stock == id_stock).first()
        
        if not stock:
            # Usar ValueError é mais específico do que Exception genérica para "não encontrado"
            raise ValueError(f"Estoque com ID {id_stock} não encontrado para auditoria.")


        serialized_old_stock_data = None
        serialized_new_stock_data = None
        # 3. Serializar dados para formato JSON (especialmente datas)
        # O resultado é um dicionário Python que será armazenado no campo JSONB.
        if old_data:
            serialized_old_stock_data = serialize_for_json(old_data)
        if new_data:
            serialized_new_stock_data = serialize_for_json(new_data)

        # 4. Criar o registro de auditoria
        # Assumindo que models.stock_movement_audit.StockMovementAudit é o modelo correto.
        # Se 'data' for mapeado para 'new_data' no seu modelo de auditoria, ajuste aqui.
        audit_record = stock_audit.StockAudit( # ou models.StockMovementAudit
            id_stock=id_stock,
            operation=operation.upper(), # Garante que a operação seja em maiúsculas
            # Passa o dicionário Python. O driver do banco de dados/ORM cuidará da conversão para JSONB.
            old_data=serialized_old_stock_data, 
            new_data=serialized_new_stock_data,
            changed_by=changed_by,
            date=datetime.utcnow() # Timestamp UTC para consistência
        )

        # 5. Adicionar e commitar a auditoria no banco de dados
        db.add(audit_record)
        db.commit()
        # db.refresh(audit_record) # Opcional: Se precisar do ID do registro de auditoria recém-criado

    except ValueError as ve:
        print(f"Erro de Validação na Auditoria de Estoque: {ve}")
        db.rollback() # Garante que a transação seja desfeita em caso de erro
        raise # Re-levanta a exceção para que o chamador possa tratá-la
    except Exception as e:
        print(f"Erro inesperado durante a auditoria de Estoque {id_stock}: {e}")
        db.rollback() # Em caso de qualquer outro erro, desfaz a transação
        raise # Re-levanta a exceção